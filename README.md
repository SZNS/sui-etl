# Sui ETL

Sui ETL uses the [sui-analytics-indexer](https://github.com/MystenLabs/sui/tree/main/crates/sui-analytics-indexer/src) to push Sui blockchain data real-time into the BigQuery public dataset for users to query Sui data.

![sui-etl-architecture.png](./assets/sui_etl_architecture.png)

1. Sui Full Node and Analytics Indexer are deployed. Refer to the below for more details:
    1. Deploying Full Node and Indexer on GCP: https://github.com/SZNS/sui-node
    2. Sui Full Node official documentation: https://docs.sui.io/guides/operator/validator-committee
2. Blockchain data is exported to GCS 
3. Dataflow jobs stream data into BigQuery (currently ~5 minute data liveness). Refer to `[Docs](docs/dataflow.md)` here for more details.
4. Airflow DAGs verify and validate data freshness and correctness on a per epoch (ie: daily) basis. Refer to docs `[Docs](docs/cloudcomposer.md)`  for more details.
