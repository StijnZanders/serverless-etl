import os
from models.operator import Operator

class PythonOperator(Operator):

    def __init__(self, *, dag, task_id, description, python_callable, op_kwargs):
        self.dag = dag
        self.task_id = task_id
        self.description = description
        self.python_callable = python_callable
        self.op_kwargs = op_kwargs


    def get_terraform_json(self) -> {}:

        resources = {
            "google_storage_bucket_object": [{
                f"topic_{self.task_id}": {
                    "name": f"{self.task_id}.zip",
                    "bucket": "${google_storage_bucket.bucket.name}",
                    "source": f"test_directory/{self.task_id}.zip"#f"./{self.dag.dag_id}/{self.task_id}"
                }
            }],
            "google_cloudfunctions_function": [{
                f"function_{self.task_id}": {
                    "name": f"{self.dag.dag_id}-{self.task_id}",
                    "description": self.description,
                    "runtime": "python38",
                    "available_memory_mb": 128,
                    "service_account_email": os.environ["SERVICE_ACCOUNT_EMAIL"],
                    "source_archive_bucket": "${google_storage_bucket.bucket.name}",
                    "source_archive_object": "${google_storage_bucket_object.topic_"+self.task_id+".name}",
                    "event_trigger": {
                        "event_type": "providers/cloud.pubsub/eventTypes/topic.publish",
                        "resource": self.dag.dag_id
                    }
                }
            }]
        }

        return resources