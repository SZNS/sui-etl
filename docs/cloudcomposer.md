# Overview

Composer is a GCP product to run [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) for batch jobs. We use Airflow to run scheduled jobs per epoch to validate that ingested BigQuery data is up to date, not duplicated, and not missing.

# Prerequisites

Create a BigQuery instance with the relevant tables. Instructions [here](/docs/bigquery.md)

# Deploying Airflow to Composer

## Create a Composer environment

Please follow [these instructions](https://cloud.google.com/composer/docs/composer-2/create-environments) to create a Composer environment.

## Update Environment Variables

1. In the newly created Composer environment click the “Environment Variables” tab → Click Edit
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0a43eda3-718b-4a0c-bb46-015b10c65c2d/0525ef0f-70c0-49aa-8e47-29f49c41fe66/Untitled.png)
    
2. Add the following variables
    
    
    | Key | Description |
    | --- | --- |
    | AIRFLOW_VAR_PROJECT_ID | The project ID where the BigQuery data is saved |
    | AIRFLOW_VAR_DATASET_NAME | The table name where the BigQuery data is saved |
    
    ![Screenshot 2024-01-31 at 3.40.59 PM.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/0a43eda3-718b-4a0c-bb46-015b10c65c2d/2c793e10-d95b-438b-a87b-1fe9e5b8c62e/Screenshot_2024-01-31_at_3.40.59_PM.png)
    

## Deploy Airflow

1. In the Composer Environment click the “OPEN DAGS FOLDER” link
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/0a43eda3-718b-4a0c-bb46-015b10c65c2d/4b04361c-c19c-4ed4-94dd-8fe27a0c94bf/Untitled.png)
    
2. Click “UPLOAD FILES”
3. Upload all files in this repository under the `dags` directory into this GCS folder
4. Wait for the Composer environment to rebuild and start running