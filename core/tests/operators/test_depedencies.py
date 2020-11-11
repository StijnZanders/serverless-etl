from unittest import TestCase
from operators.python_operator import PythonOperator
from models.dag import DAG


class TestOperatorDependencies(TestCase):

    def setUp(self):

        def test(arg):
            pass

        default_args = {}

        self.test_dag = DAG(
            dag_id="test_dag",
            description="Test DAG",
            default_args=default_args,
            schedule_interval="0 * * * *"
        )

        self.test_task = PythonOperator(
            dag=self.test_dag,
            task_id="test_task",
            description="Test task",
            python_callable=test,
            op_kwargs={'arg': 'great test'},
            requirements=["pandas==1.0.0", "pandas_gbq==0.14.0"]
        )

        self.test_task2 = PythonOperator(
            dag=self.test_dag,
            task_id="test_task2",
            description="Test task 2",
            python_callable=test,
            op_kwargs={'arg': 'great test'},
            requirements=["pandas==1.0.0", "pandas_gbq==0.14.0"]
        )

    def test_upstream_setting(self):

        self.test_task.set_upstream(self.test_task2)

        upstream_tasks = self.test_task.upstream_tasks
        downstream_tasks = self.test_task2.downstream_tasks

        self.assertEqual("test_task2", upstream_tasks[0])
        self.assertEqual("test_task", downstream_tasks[0])

    def test_upstream_lshift_setting(self):

        self.test_task << self.test_task2

        upstream_tasks = self.test_task.upstream_tasks
        downstream_tasks = self.test_task2.downstream_tasks

        self.assertEqual("test_task2", upstream_tasks[0])
        self.assertEqual("test_task", downstream_tasks[0])

    def test_downstream_setting(self):

        self.test_task.set_downstream(self.test_task2)

        downstream_tasks = self.test_task.downstream_tasks
        upstream_tasks = self.test_task2.upstream_tasks

        self.assertEqual("test_task2", downstream_tasks[0])
        self.assertEqual("test_task", upstream_tasks[0])

