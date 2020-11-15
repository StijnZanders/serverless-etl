import os
from models.operator import Operator
import inspect
import zipfile

class PythonOperator(Operator):

    def __init__(self, *, dag, task_id, description, python_callable, op_kwargs, requirements: []):
        super().__init__()

        self.dag = dag
        self.task_id = task_id
        self.description = description
        self.python_callable = python_callable
        self.op_kwargs = op_kwargs
        self.requirements = requirements

    def _write_cloud_function_code(self):

        code = inspect.getsource(self.python_callable)

        code += "\ndef cloudfunction_execution(event, context):\n"\
                f"\t{self.python_callable.__name__}({self.op_kwargs})\n"\
                f"{self._write_to_pub_sub_code()}"

        main = f"output/{self.dag.dag_id}/{self.task_id}/main.py"
        os.makedirs(os.path.dirname(main), exist_ok=True)

        with open(main, "w") as file:
            file.write(code)

        requirements = f"output/{self.dag.dag_id}/{self.task_id}/requirements.txt"

        self.requirements.extend(["google-cloud","google-cloud-pubsub"])

        with open(requirements,"w") as file:
            file.write("\n".join(self.requirements))

    def _write_to_pub_sub_code(self):

        code = "\tfrom google.cloud import pubsub_v1\n"\
               "\timport json\n"\
               "\timport os\n"\
               "\tPROJECT_ID = 'serverless-etl-test'\n"\
               "\tpublisher = pubsub_v1.PublisherClient()\n"\
               f"\ttopic_name = 'task_{self.dag.dag_id}_{self.task_id}'\n"\
               "\ttopic_path = publisher.topic_path(PROJECT_ID, topic_name)\n"\
               "\tmessage_json = json.dumps({'data': {'message': 'test'},})\n"\
               "\tmessage_bytes = message_json.encode('utf-8')\n"\
               "\tpublish_future = publisher.publish(topic_path, data=message_bytes)\n"\
               "\tpublish_future.result()"

        return code

    def get_terraform_json(self) -> {}:

        self._write_cloud_function_code()

        source_dir = f"{self.dag.dag_id}/{self.task_id}"
        file_path = f"{self.dag.dag_id}/{self.task_id}.zip"

        if len(self.upstream_tasks) > 0:
            trigger_resource = f"task_{self.dag.dag_id}_{self.upstream_tasks[0]}"
        else:
            trigger_resource = f"dag_{self.dag.dag_id}"

        configuration = {
            "data": {
                "archive_file": [{
                    f"task_{self.task_id}": {
                        "type": "zip",
                        "source_dir": source_dir,
                        "output_path": file_path
                    }
                }]
            },
            "resource": {
                "google_storage_bucket_object": [{
                    f"task_{self.task_id}": {
                        "name": file_path+"#${data.archive_file.task_"+self.task_id+".output_md5}",
                        "bucket": "${google_storage_bucket.bucket.name}",
                        "source": file_path
                    }
                }],
                "google_cloudfunctions_function": [{
                    f"function_{self.task_id}": {
                        "name": f"{self.dag.dag_id}-{self.task_id}",
                        "description": self.description,
                        "runtime": "python38",
                        "available_memory_mb": 256,
                        "service_account_email": os.environ["SERVICE_ACCOUNT_EMAIL"],
                        "source_archive_bucket": "${google_storage_bucket.bucket.name}",
                        "source_archive_object": "${google_storage_bucket_object.task_"+self.task_id+".name}",
                        "event_trigger": {
                            "event_type": "providers/cloud.pubsub/eventTypes/topic.publish",
                            "resource": trigger_resource
                        },
                        "entry_point": "cloudfunction_execution"
                    }
                }],
                "google_pubsub_topic": [{
                    f"task_{self.dag.dag_id}_{self.task_id}": {
                        "name": f"task_{self.dag.dag_id}_{self.task_id}"
                    }
                }]
            }
        }

        return configuration