import logging

from airflow.models import Variable
from airflow import models
from google.cloud import bigquery
from airflow.providers.google.cloud.operators.bigquery import BigQueryValueCheckOperator
from sensors.EpochSensor import EpochSensor
from utils.variables import read_dag_vars
from utils.utils import get_sql_query
from airflow.operators.python import PythonOperator


from datetime import datetime, timedelta
import json

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

default_args = {
    "owner": "Composer Example",
    'provide_context': True,
    "depends_on_past": True,
    "email": [""],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(year=2023, month=4, day=12, hour=14),
    # Set this to load to a particular day/epoch
    # "end_date": datetime(year=2024, month=2, day=12, hour=11)
}


EPOCH_KEY = "epoch"
# Retreive the current epoch as a airflow variable and set in xcom for other tasks to pull
def current_epoch(ti):
    cur_epoch = Variable.get("epoch_run_index", default_var=0)

    logging.info("Epoch is {epoch}".format(epoch=cur_epoch))

    ti.xcom_push(key=EPOCH_KEY, value=int(cur_epoch))

# Update the epoch as a airflow variable for the next DAG run
def update_epoch(ti):
    epoch = ti.xcom_pull(key=EPOCH_KEY, task_ids="prepare")

    next_epoch = int(epoch) + 1

    logging.info(
        "Finished validations. Setting next epoch to: {epoch}".format(epoch=next_epoch))

    Variable.set("epoch_run_index", next_epoch)

with models.DAG(
    "validate_epoch",
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    params=read_dag_vars(),
    max_active_runs=1,
) as dag:
    
    check_epoch_task = EpochSensor(
        task_id='check_epoch',
        http_conn_id='sui_mainnet_api',
        # endpoint is blank since this is JSON RPC
        endpoint='/',
        request_params={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "suix_getLatestSuiSystemState",
            "params": []
        },
        headers={"Content-Type": "application/json"},
        # Since epochs aren't exactly 24 hours as we've seen drifts over time
        poke_interval=timedelta(minutes=30).total_seconds(), 
        # Just in case there is significant drift so try for ~12 hours
        timeout=timedelta(hours=12).total_seconds(),
        dag=dag,
    )

    # Retrieve current epoch
    prepare_task = PythonOperator(
        task_id="prepare", python_callable=current_epoch,
        dag=dag
    )

    # Check for this current epoch that checkpoints have been indexed
    has_checkpoints_task = BigQueryValueCheckOperator(
        task_id="has_checkpoints",
        sql=get_sql_query('has_checkpoints'),
        pass_value=1,
        use_legacy_sql=False,
        
        dag=dag
    )

    def create_load_task(type, table_name):
        # since ti.xcom_ not avaiable in this context
        epoch = Variable.get("epoch_run_index", default_var=0)
        source_bucket_id = Variable.get("source_bucket_id")

        def load_task():
            target_project_id = Variable.get(
                "target_project_id", default_var=0)

            # Since Airflow vars are stored as strings
            skip_load = Variable.get("skip_load").lower() == "true"
            if not skip_load:
                target_dataset_name = Variable.get("target_dataset_name")

                client = bigquery.Client(project=target_project_id)
                job_config = bigquery.LoadJobConfig()
                job_config.source_format = bigquery.SourceFormat.CSV
                job_config.field_delimiter = "|"
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                job_config.allow_quoted_newlines = True

                data_location_uri = 'gs://{bucket}/{type}/epoch_{epoch}'.format(
                    bucket=source_bucket_id, type=type, epoch=epoch)
                uri = '{data_location_uri}/*.csv'.format(
                    data_location_uri=data_location_uri)

                table_ref = client.dataset(
                    target_dataset_name).table(table_name)
                load_job = client.load_table_from_uri(
                    uri, table_ref, job_config=job_config)

                try:
                    logging.info('Creating a job: ' +
                                 json.dumps(job_config.to_api_repr()))
                    result = load_job.result()
                    logging.info(result)
                    assert load_job.errors is None or len(load_job.errors) == 0
                except Exception:
                    logging.info(load_job.errors)
                    # raise

                assert load_job.state == 'DONE'
            else:
                logging.info(
                    'Skip load flag set to TRUE. Skipping load of {type}'.format(type=type))

        load_operator = PythonOperator(
            task_id='load_{type}'.format(type=type, epoch=epoch),
            python_callable=load_task,
            execution_timeout=timedelta(minutes=30),
            dag=dag
        )

        return load_operator

    # Check the top checkpoint sequence number = total checkpoints indexed this epoch
    checkpoints_count_task = BigQueryValueCheckOperator(
        task_id="checkpoints_count",
        sql=get_sql_query('checkpoints_count'),
        pass_value=1,
        use_legacy_sql=False,
        dag=dag
    )

    # Check total move calls in transactions = total move calls indexed this epoch
    move_calls_task = BigQueryValueCheckOperator(
        task_id="move_calls",
        sql=get_sql_query('move_calls'),
        pass_value=1,
        use_legacy_sql=False,
        dag=dag
    )

    # Check total transaction blocks indexed = total transaction blocks for this epoch
    txn_blocks_count_task = BigQueryValueCheckOperator(
        task_id="txn_blocks_count",
        sql=get_sql_query('transaction_blocks_count'),
        pass_value=1,
        use_legacy_sql=False,
        dag=dag
    )

    # Finalize and update epoch for next run
    cleanup_task = PythonOperator(
        task_id="cleanup", python_callable=update_epoch
    )

    load_tasks = [create_load_task("checkpoints", "CHECKPOINT"),
                  create_load_task("events", "EVENT"),
                  create_load_task("move_call", "MOVE_CALL"),
                  create_load_task("move_package", "MOVE_PACKAGE"),
                  create_load_task("objects", "OBJECT"),
                  create_load_task("transactions", "TRANSACTION"),
                  create_load_task("transaction_objects", "TRANSACTION_OBJECT")
                  ]

    check_epoch_task >> prepare_task >> load_tasks >> has_checkpoints_task >> [
        checkpoints_count_task,
        move_calls_task,
        txn_blocks_count_task
    ] >> cleanup_task
