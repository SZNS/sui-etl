# Overview

Composer is a GCP product to run [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) for batch jobs. We use Airflow to run scheduled jobs per epoch to validate that ingested BigQuery data is up to date, not duplicated, and not missing.

# Prerequisites

Create a BigQuery instance with the relevant tables. Instructions [here](/docs/bigquery.md)

# Deploying Airflow to Composer

## Create a Composer environment

Please follow [these instructions](https://cloud.google.com/composer/docs/composer-2/create-environments) to create a Composer environment.

## Update Environment Variables

1. In the newly created Composer environment click the “Environment Variables” tab → Click Edit
    
    ![cloudcomposermd-1.png](/assets/reference/cloudcomposermd-1.png)
    
2. Add the following variables
    
    
    | Key | Description |
    | --- | --- |
    | AIRFLOW_VAR_PROJECT_ID | The project ID where the BigQuery data is saved |
    | AIRFLOW_VAR_DATASET_NAME | The table name where the BigQuery data is saved |
    
    ![cloudcomposermd-2.png](/assets/reference/cloudcomposermd-2.png)
    

## Deploy Airflow

1. In the Composer Environment click the “OPEN DAGS FOLDER” link
    
    ![cloudcomposermd-3.png](/assets/reference/cloudcomposermd-3.png)
    
2. Click “UPLOAD FILES”
3. Upload all files in this repository under the `dags` directory into this GCS folder
4. Wait for the Composer environment to rebuild and start running