# Overview

Cloud Dataflow is used to ETL Sui blockchain data into BigQuery. Jobs are triggered by PubSub notifications when blockchain data is exported into GCS from the Sui Analytics Indexer. For more information, refer to https://github.com/SZNS/sui-node/

# How to run

Note that since the Sui analytics indexer exports seven data types separately the below needs to run seven times to account for each data type (checkpoint, event, move_call, move_package, object, transaction_object, transaction)

## Prerequisites

This document assumes the [GCP CLI](https://cloud.google.com/sdk/docs/install-sdk) and [Python](https://www.python.org/downloads/) are installed. Also make sure to complete the Dataflow [Environment setup](https://cloud.google.com/dataflow/docs/quickstarts/create-pipeline-python#set-up-your-environment).

### Run an analytics node

Start a Sui full node with the analytics indexer exporting to GCS.

**TODO: update link here to the documentation for running an analytics node**

### Create a temporary directory

Create a GCS bucket or a folder in an existing 

### Create BigQuery tables

**TODO: Link here to bigquery table doc**

### Create a Pub/Sub topic and subscription

1. [Enable the Pub/Sub API](https://cloud.google.com/storage/docs/reporting-changes#before-you-begin)
2. Create a Pub/Sub topic and subscription for the particular data type
    
    ```bash
    gcloud pubsub topics create [TOPIC_ID]
    gcloud pubsub subscriptions create [SUBSCRIPTION_ID]-sub --topic=[TOPIC_ID]
    ```
    

## Deploy a dataflow job

Run the following commands to deploy a dataflow job for a particular pipeline.

```bash
python SuiAnalytics.py --region=[REGION] --type=[TYPE] \
--input_sub=[SUBSCRIPTION_ID] --output_table=[BIGQUERY_TABLE] \
--runner=DataflowRunner --project=[PROJECT_ID] --temp_location=[GCS_TEMP_DIR] \
--diskSizeGb=[DISK_SIZE] --workerMachineType=[MACHINE_TYPE] \
--maxNumWorkers=[MAX_WORKERS] --job_name=[JOB_NAME]
```

| Variable | Description | Recommended value |
| --- | --- | --- |
| REGION | The region where Dataflow clusters will run |  |
| TYPE | The type of data to process. Options include: checkpoint, event, move_call, move_package, object, transaction_object, transaction |  |
| SUBSCRIPTION_ID | The subscription ID created above |  |
| BIGQUERY_TABLE | The BigQuery table to export data. The format for the BigQuery table is: [PROJECT:DATASET.TABLE] |  |
| PROJECT_ID | The GCP project ID |  |
| GCS_TEMP_DIR | A Cloud Storage path for Dataflow to stage temporary job files created during the execution of the pipeline |  |
| DISK_SIZE | The disk size for Dataflow workers | 20, since machines are not utilizing persistent disk space |
| MACHINE_TYPE | The https://cloud.google.com/compute/docs/machine-resource for Dataflow workers | For type object = n2-highcpu-16 <p> For other types = n1-standard-4 |
| MAX_WORKERS | The maximum workers to scale up for a Dataflow pipeline | 10, it tends to be costly and takes time to spin up/down workers. We suggest updating MACHINE_TYPE if the current latency is undesirable |
| JOB_NAME | A uniquer job name for the Dataflow pipeline |  |
