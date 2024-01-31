# To deploy a dataflow pipeline
python SuiAnalytics.py --region=[REGION] --type=[TYPE] \
--input_sub=[SUBSCRIPTION_ID] --output_table=[BIGQUERY_TABLE] \
--runner=DataflowRunner --project=[PROJECT_ID] --temp_location=[GCS_TEMP_DIR] \
--diskSizeGb=[DISK_SIZE] --workerMachineType=[MACHINE_TYPE] \
--maxNumWorkers=[MAX_WORKERS] --job_name=[JOB_NAME]