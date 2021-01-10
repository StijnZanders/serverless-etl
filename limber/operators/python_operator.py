import os
from ..models.operator import Operator
import inspect
import shutil
import hashlib
import zipfile
import stat

class PythonOperator(Operator):

    def __init__(self, *, dag, task_id, description, python_callable, op_kwargs, provide_context=False, memory=256):
        super().__init__()

        self.dag = dag
        self.task_id = task_id
        self.description = description
        self.python_callable = python_callable
        self.op_kwargs = op_kwargs
        self.provide_context = provide_context
        self.memory = memory

    def _get_func_parameters(self, kwargs) -> str:

        parameters = []
        for key, value in kwargs.items():
            parameters.append(f"{key}='{value}'")

        if self.provide_context:
            parameters.append("context=data")

        return ",".join(parameters)

    def _write_cloud_function_code(self, folder):

        task_folder = f"{folder}/{self.dag.dag_id}/{self.task_id}"
        shutil.rmtree(task_folder, ignore_errors=True)

        self._write_plugins_folder(task_folder)
        self._write_main(task_folder)
        self._write_requirements(task_folder)

        output_path = f"{task_folder}.zip"

        with zipfile.ZipFile(output_path, "w") as zip_file:
            self._create_zip_folder(task_folder, zip_file, os.path.abspath(task_folder))

        hash = hashlib.md5(open(f"{task_folder}.zip", "rb").read()).hexdigest()

        return hash

    def _write_plugins_folder(self, task_folder):
        shutil.copytree("plugins", f"{task_folder}/plugins")
        shutil.copytree("dags", f"{task_folder}/dags")

    def _write_main(self, task_folder):

        module_name = self.dag.filename.replace("/",".").replace("\\", ".").replace(".py", "")
        code = f"from {module_name} import {self.python_callable.__name__}\n\n"

        code += "def cloudfunction_execution(event, context):\n"

        if self.provide_context:
            code += "    import base64\n" \
                    "    import json\n" \
                    "    if 'data' in event:\n"\
                    "        data = base64.b64decode(event['data']).decode('utf-8')\n"\
                    "        data = json.loads(data)\n"

        parameters = self._get_func_parameters(self.op_kwargs)

        code += f"    outputs = {self.python_callable.__name__}({parameters})\n"\
                f"\n    if outputs is None:\n"\
                f"        outputs = ['done']\n"\
                f"\n    topic_name = 'task_{self.dag.dag_id}_{self.task_id}'\n"\


        pubsub_code = inspect.getsourcelines(self._write_to_pub_sub_code)
        code += "\n    def call_pub_sub(message, topic_name):\n"
        code += "".join(pubsub_code[0][1:])

        code += "\n    for output in outputs:\n"
        code += "        call_pub_sub(output, topic_name)\n"

        main = f"{task_folder}/main.py"
        os.makedirs(os.path.dirname(main), exist_ok=True)

        with open(main, "w") as file:
            file.write(code)

    def _write_requirements(self, task_folder):
        target_file = f"{task_folder}/requirements.txt"

        requirements_file_name = "requirements.txt"

        with open(requirements_file_name, "r") as requirements_file:
            requirements = requirements_file.read().split("\n")

        with open(target_file, "w") as file:
            file.write("\n".join(requirements))

    def _create_zip_folder(self, path, zip_file: zipfile, directory_root):
        for root, dirs, files in os.walk(path):
            for file in files:
                self._add_file(zip_file, os.path.join(root, file), os.path.relpath(f"{root}/{file}", directory_root))

    def _add_file(self, zip_file: zipfile, file_path, zip_path=None):
        permission = 0o555 if os.access(file_path, os.X_OK) else 0o444
        zip_info = zipfile.ZipInfo.from_file(file_path, zip_path)
        zip_info.date_time = (2019, 1, 1, 0, 0, 0)
        zip_info.external_attr = (stat.S_IFREG | permission) << 16
        with open(file_path, "rb") as fp:
            zip_file.writestr(
                zip_info,
                fp.read(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )

    def _write_to_pub_sub_code(self, message, topic_name):
        from google.cloud import pubsub_v1
        import os
        import json

        PROJECT_ID = os.environ['GCP_PROJECT']
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, topic_name)
        message_json = json.dumps({'data': {'message': message},})
        message_bytes = message_json.encode('utf-8')
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()

    def get_terraform_json(self, *, folder) -> {}:

        hash = self._write_cloud_function_code(folder=folder)

        source_dir = f"{self.dag.dag_id}/{self.task_id}"

        if len(self.upstream_tasks) > 0:
            trigger_resource = f"task_{self.dag.dag_id}_{self.upstream_tasks[0]}"
        else:
            trigger_resource = f"dag_{self.dag.dag_id}"

        configuration = {
            "resource": {
                "google_storage_bucket_object": [{
                    f"task_{self.task_id}": {
                        "name": f"{source_dir}_{hash}.zip",
                        "bucket": "${google_storage_bucket.bucket.name}",
                        "source": f"{source_dir}.zip"
                    }
                }],
                "google_cloudfunctions_function": [{
                    f"function_{self.task_id}": {
                        "name": f"{self.dag.dag_id}-{self.task_id}",
                        "description": self.description,
                        "runtime": "python37",
                        "available_memory_mb": self.memory,
                        "service_account_email": os.environ["CLOUD_FUNCTIONS_SERVICE_ACCOUNT_EMAIL"],
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