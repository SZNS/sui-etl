# Sui Airflow

---

## Setting up DAGS with Google Cloud Composer

- Create datasets using [the following schema](../scripts/sql/bq/)

### Create Google Cloud Composer Environment

Use Composer version 2. This process may take a while for the environment to start up.

```bash

gcloud composer environments create \
    ${ENVIRONMENT_NAME} \
    --location=${REGION} \
    --image-version=composer-2.6.0-airflow-2.6.3 \
    --environment-size=["small"|"medium"|"large"] \
    --scheduler-cpu=2 \
    --scheduler-memory=7.5 \
    --scheduler-storage=5 \
    --scheduler-count=1 \
    --web-server-cpu=1 \
    --web-server-memory=7.5 \
    --web-server-storage=512MB \
    --worker-cpu=4 \
    --worker-memory=7.5 \
    --worker-storage=5 \
    --min-workers=1 \
    --max-workers=5 \
    --env-variables AIRFLOW_VAR_TARGET_PROJECT_ID=${AIRFLOW_VAR_TARGET_PROJECT_ID},AIRFLOW_VAR_TARGET_DATASET_NAME=${AIRFLOW_VAR_TARGET_DATASET_NAME},AIRFLOW_VAR_SOURCE_BUCKET_ID=${AIRFLOW_VAR_SOURCE_BUCKET_ID},AIRFLOW_VAR_SKIP_LOAD=${AIRFLOW_VAR_SKIP_LOAD}
```

For `env-variables` provide the following values

| Key                             | Description                                                                                                                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AIRFLOW_VAR_TARGET_PROJECT_ID   | The target project id where the BigQuery dataset resides                                                                                                                                 |
| AIRFLOW_VAR_TARGET_DATASET_NAME | The target dataset id in BigQuery                                                                                                                                                        |
| AIRFLOW_VAR_SOURCE_BUCKET_ID    | The Google Cloud Storage bucket where analytics exports reside                                                                                                                           |
| AIRFLOW_VAR_SKIP_LOAD           | `True` skips the batch loading, otherwise batch load on every epoch. Setting `True` does per epoch validation still which is useful if there is another streaming workload into BigQuery |
