import datetime
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from airflow.operators.python import PythonOperator
from utils.utils import get_sql_query
from utils.variables import read_dag_vars
from airflow.providers.google.cloud.operators.bigquery import BigQueryValueCheckOperator
from airflow import models
from airflow.models import Variable


default_args = {
    "owner": "Composer Example",
    "depends_on_past": True,
    "email": [""],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": datetime.timedelta(minutes=5),
    "start_date": datetime.datetime(year=2023, month=4, day=12, hour=14),
}


EPOCH_KEY = "epoch"

# Retreive the current epoch as a airflow variable
def current_epoch(ti):
    cur_epoch = Variable.get("epoch_run_index", default_var=0)

    logging.info("Epoch is {epoch}".format(epoch=cur_epoch))

    ti.xcom_push(key=EPOCH_KEY, value=int(cur_epoch))

# Update the epoch as a airflow variable for the next DAG run
def update_epoch(ti):
    epoch = ti.xcom_pull(key=EPOCH_KEY, task_ids="current_epoch")

    next_epoch = int(epoch) + 1

    logging.info("Finished validations. Setting new epoch to: {epoch}".format(epoch=next_epoch))

    Variable.set("epoch_run_index", next_epoch)


with models.DAG(
    "validate_epoch",
    default_args=default_args,
    schedule_interval=datetime.timedelta(days=1),
    params=read_dag_vars(),
    max_active_runs=1,
) as dag:
    
    # Retrieve current epoch
    current_epoch_task = PythonOperator(
        task_id="current_epoch", python_callable=current_epoch
    )

    # Check for this current epoch that checkpoints have been indexed
    has_checkpoints_task = BigQueryValueCheckOperator(
        task_id="has_checkpoints",
        sql=get_sql_query('has_checkpoints'),
        pass_value=1,
        use_legacy_sql=False
    )

    # Check the top checkpoint sequence number = total checkpoints indexed this epoch
    checkpoints_count_task = BigQueryValueCheckOperator(
        task_id="checkpoints_count",
        sql=get_sql_query('checkpoints_count'),
        pass_value=1,
        use_legacy_sql=False
    )

    # Check total move calls in transactions = total move calls indexed this epoch
    move_calls_task = BigQueryValueCheckOperator(
        task_id="move_calls",
        sql=get_sql_query('move_calls'),
        pass_value=1,
        use_legacy_sql=False
    )

    # Check total transaction blocks indexed = total transaction blocks for this epoch
    txn_blocks_count_task = BigQueryValueCheckOperator(
        task_id="txn_blocks_count",
        sql=get_sql_query('transaction_blocks_count'),
        pass_value=1,
        use_legacy_sql=False
    )

    # Finalize and update epoch for next run
    update_epoch_task = PythonOperator(
        task_id="update_epoch", python_callable=update_epoch
    )

    current_epoch_task >> has_checkpoints_task >> [checkpoints_count_task, move_calls_task,txn_blocks_count_task] >> update_epoch_task