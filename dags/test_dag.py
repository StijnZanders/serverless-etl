from models.dag import DAG
from operators.python_operator import PythonOperator
from datetime import timedelta


default_args = {

}

test_dag = DAG(
    dag_id="test_dag",
    description="DAG that will for now just create a Google cloud scheduler",
    default_args=default_args,
    schedule_interval="0 * * * *"
)

def test(arg):
    print(f"Test {arg}")


test_task = PythonOperator(
    dag=test_dag,
    task_id="test_task",
    description="Test task",
    python_callable=test,
    op_kwargs={'arg': 'great test'}
)

test_dag2 = DAG(
    dag_id="test_dag2",
    description="DAG that will for now just create a Google cloud scheduler",
    default_args=default_args,
    schedule_interval="0 1 * * *"
)

test_task2 = PythonOperator(
    dag=test_dag2,
    task_id="test_task2",
    description="Test task2",
    python_callable=test,
    op_kwargs={'arg': 'great test2'}
)