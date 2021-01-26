from limber.models.dag import DAG
from limber.operators.python_operator import PythonOperator
from plugins.test_utils import test, test_multiple_outputs, test_with_context

default_args = {

}

test_dag = DAG(
    dag_id="test_dag",
    description="DAG that will for now just create a Google cloud scheduler",
    default_args=default_args,
    schedule_interval="0 * * * *"
)

test_task = PythonOperator(
    dag=test_dag,
    task_id="test_task",
    description="Test task",
    python_callable=test,
    op_kwargs={'arg': 'great test'}
)

test_task2 = PythonOperator(
    dag=test_dag,
    task_id="test_task2",
    description="Test task2",
    python_callable=test_multiple_outputs,
    op_kwargs={'arg': 'great test2'},
    memory=128
)

test_task3 = PythonOperator(
    dag=test_dag,
    task_id="test_task3",
    description="Test task3",
    python_callable=test_with_context,
    provide_context=True,
    op_kwargs={'arg': 'great test3'}
)

test_task4 = PythonOperator(
    dag=test_dag,
    task_id="test_task4",
    description="Throttled task",
    python_callable=test,
    provide_context=True,
    throttle_rate_limits={
        "max_concurrent_dispatches": 3,
        "max_dispatches_per_second": 2
    },
    throttle_retry_config={
        "max_attempts": 5,
        "max_retry_duration": "4s",
        "max_backoff": "3s",
        "min_backoff": "2s",
        "max_doublings": 1
    },
    op_kwargs={}
)

test_task >> test_task2

test_task2 >> test_task3

test_task3 >> test_task4
