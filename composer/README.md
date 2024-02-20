# Sui Airflow

Batch analytics export with Google Cloud Composer via Apache Airflow

---

## Setting up DAGS with Google Cloud Composer

- Create datasets using [the following schema](../scripts/sql/bq/)

### Create Google Cloud Composer Environment

Use Composer version 2.

Create a `.env` file and add the following values

| Key                             | Description                                                                                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ENVIRONMENT_NAME                | The name of the Composer environment                                                                                                                                                 |
| REGION                          | The GCP region to host composer environment                                                                                                                                          |
| ENVIRONMENT_SIZE                | Size of the Composer environment [small, medium, large ]                                                                                                                             |
| AIRFLOW_VAR_TARGET_PROJECT_ID   | The target project id where the BigQuery dataset resides                                                                                                                             |
| AIRFLOW_VAR_TARGET_DATASET_NAME | The target dataset id in BigQuery                                                                                                                                                    |
| AIRFLOW_VAR_SOURCE_BUCKET_ID    | The Google Cloud Storage bucket where analytics exports reside                                                                                                                       |
| AIRFLOW_VAR_SKIP_LOAD           | True skips the batch loading, otherwise batch load on every epoch. Setting True does per epoch validation still which is useful if there is another streaming workload into BigQuery |

Create the Composer environment. This process may take a while for the environment to start up.

```bash
source .env

gcloud composer environments create \
    ${ENVIRONMENT_NAME} \
    --location=${REGION} \
    --image-version=composer-2.6.0-airflow-2.6.3 \
    --environment-size=${ENVIRONMENT_SIZE} \
    --scheduler-cpu=2 \
    --scheduler-memory=8 \
    --scheduler-storage=5 \
    --scheduler-count=1 \
    --web-server-cpu=1 \
    --web-server-memory=4 \
    --web-server-storage=1 \
    --worker-cpu=4 \
    --worker-memory=8 \
    --worker-storage=5 \
    --min-workers=1 \
    --max-workers=5 \
    --env-variables AIRFLOW_VAR_TARGET_PROJECT_ID=${AIRFLOW_VAR_TARGET_PROJECT_ID},AIRFLOW_VAR_TARGET_DATASET_NAME=${AIRFLOW_VAR_TARGET_DATASET_NAME},AIRFLOW_VAR_SOURCE_BUCKET_ID=${AIRFLOW_VAR_SOURCE_BUCKET_ID},AIRFLOW_VAR_SKIP_LOAD=${AIRFLOW_VAR_SKIP_LOAD}
```

## Create a connection ID

Once the environment is created go to the airflow UI.

1. Go to Admin -> Connections
2. Click + (Add New Record)
3. Add the following fiels
   - Connection Id: sui-mainnet_api
   - Connection Type: HTTP
   - Host: https://fullnode.mainnet.sui.io
   - Port: 443
4. Click Save

## Upload DAGs folder

Once the environment is create upload the `dags` folder to the Composer environment. `airflow_bucket` is the Google Cloud Storage bucket created in the Composer environment.

```
gcloud storage rsync -x 'airflow_monitoring|.*\.pyc$' -c -r dags/ gs://${airflow_bucket}/dags
```
