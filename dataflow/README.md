# Sui Dataflow

Stream analytic data with Google Dataflow via Apache Beam into BigQuery

## Overview

This sets up a data pipeline that ingests analytic data exported in Google Cloud Storage (GCS) and streams the data into Google BigQuery. Pipeline jobs are triggered by PubSub notifications when new data is exporting into GCS bucket(s).

## Prerequisites

Note this setup requires seven pipelines. There is one pipeline for each exported data type.

This document assumes the [GCP CLI](https://cloud.google.com/sdk/docs/install-sdk) and [Python](https://www.python.org/downloads/) are installed. Also make sure to complete the Dataflow [Environment setup](https://cloud.google.com/dataflow/docs/quickstarts/create-pipeline-python#set-up-your-environment).

### Run an analytics node

Follow this [this guide](https://github.com/SZNS/sui-node/blob/main/docs/analytics-indexer.md) to run a Sui analytisc node.

### Create a temporary directory in GCS

In GCS create a bucket and folder object (eg: gs://dataflow-jobs/temp/) for Dataflow jobs to store temp files.

### Create BigQuery tables

Ensure a BigQuery Table exists with the proper tables. Please visit [this folder](../scripts/sql/bq) to create the tables with the proper schemas.

### Create Pub/Sub topics and subscriptions
This is done 7 times for each data type (checkpoints, events, move-call, move-package, objects, transaction-objects, transactions)
1. [Enable the Pub/Sub API](https://cloud.google.com/storage/docs/reporting-changes#before-you-begin)
2. Create a Pub/Sub topic and subscription for the particular data type
   ```
   gcloud pubsub topics create [TOPIC_ID]
   gcloud pubsub subscriptions create [SUBSCRIPTION_ID]-sub --topic=[TOPIC_ID] --ack-deadline=180
   ```
   
### Create Pub/Sub topics and subscriptions
This is done 7 times for each data type (checkpoints, events, move-call, move-package, objects, transaction-objects, transactions)
1. [Enable the Pub/Sub API](https://cloud.google.com/storage/docs/reporting-changes#before-you-begin)
2. Create a Pub/Sub topic and subscription for the particular data type
   ```
   gcloud pubsub topics create [TOPIC_ID]
   gcloud pubsub subscriptions create [SUBSCRIPTION_ID]-sub --topic=[TOPIC_ID] --ack-deadline=180
   ```

### Attach Pub/Sub topic for GCS updates
From the bucket defined during the [analytics setup](https://github.com/SZNS/sui-node/blob/main/docs/analytics-indexer.md#create-google-cloud-storage-bucket) attach a Pub/Sub topic for each data type.

This is done 7 times for each data type (checkpoints, events, move-call, move-package, objects, transaction-objects, transactions)
```bash
gcloud storage buckets notifications create gs://[BUCKET_NAME] --topic=[TOPIC_NAME] --object-prefix=[PREFIX] --event-types=OBJECT_FINALIZE
```
|Variable|Description
| ------ | ------
|BUCKET_NAME|The bucket created during the [analytics setup](https://github.com/SZNS/sui-node/blob/main/docs/analytics-indexer.md#create-google-cloud-storage-bucket)
TOPIC_NAME| The topic name create in the previous step
|PREFIX| The folder in the GCS bucket. Valid values are [`checkpoints`, `events`, `move-call`, `move-package`, `objects`, `transaction-objects`, `transactions`]

## Deploy a Dataflow job
```bash
python SuiAnalytics.py --region=[REGION] --project=[PROJECT_ID] --runner=DataflowRunner \
--service_account_email=[SERVICE_ACCOUNT_EMAIL] \
--input_sub=[SUBSCRIPTION_ID] \
--target_project=[TARGET_PROJECT_ID] --dataset_name=[DATASET_NAME] \
--table_name=[TABLE_NAME] --temp_location=[GCS_TEMP_DIR] \
--disk_size_gb=[DISK_SIZE] --machine_type=[MACHINE_TYPE] \
--max_num_workers=[MAX_WORKERS] --job_name=[JOB_NAME]
```

| Variable              | Description                                                                                                                 | Recommended value                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| REGION                | The region where Dataflow clusters will run                                                                                 |                                                                                                                                         |
| PROJECT_ID            | GCP project to deploy dataflow job                                                                                          |                                                                                                                                         |
| SERVICE_ACCOUNT_EMAIL | OPTIONAL. The service account for dataflow workers. This is helpful if the dataflow jobs are exporting into another project |                                                                                                                                         |
| SUBSCRIPTION_ID       | The Cloud Pub/Sub subscription to read from. In format `projects/<project_id>/subscriptions<SUB_ID>`                        |                                                                                                                                         |
| TARGET_PROJECT_ID     | Project ID where where BigQuery table exists                                                                                |                                                                                                                                         |
| DATASET_NAME          | Dataset name where where BigQuery table exists                                                                              |                                                                                                                                         |
| TABLE_NAME            | The BigQuery table to export data                                                                                           |                                                                                                                                         |
| GCS_TEMP_DIR          | A Cloud Storage path for Dataflow to stage temporary job files created during the execution of the pipeline                 |                                                                                                                                         |
| DISK_SIZE             | The disk size in GiB for Dataflow workers                                                                                   | 10, since machines are not utilizing persistent disk space                                                                              |
| MACHINE_TYPE          | The [machine type](https://cloud.google.com/compute/docs/machine-resource) for Dataflow workers                             | n1-standard-2                                                                                                                           |
| MAX_WORKERS           | The maximum workers to scale up for a Dataflow pipeline                                                                     | 5, it tends to be costly and takes time to spin up/down workers. We suggest updating MACHINE_TYPE if the current latency is undesirable |
| JOB_NAME              | A uniquer job name for the Dataflow pipeline                                                                                |                                                                                                                                         |
