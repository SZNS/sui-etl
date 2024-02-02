# Overview

If you'd rather not export the blockchain data yourself, we publish all tables as a public dataset in [BigQuery](link).

Data is updated near real-time (~5-minute streaming delay).

Below are instructions to prepare your own BigQuery table for data export.

# Create Tables

The steps below create a BigQuery dataset and tables according to the schema defined by the Sui Analytics Indexer [here](https://github.com/MystenLabs/sui/tree/main/crates/sui-analytics-indexer/src/store/bq/schemas)

1. Create a [BigQuery dataset](https://cloud.google.com/bigquery/docs/datasets)
2. Create the tables
    1. In the GCP UI go to BigQuery and open a query tab
        
        ![bigquerymd-1.png](assets/reference/bigquerymd-1.png)
        
    2. Copy the SQL queries provided above to create a table. Update the dataset name and tables name as needed.
        1. There should be seven tables created:
            1. CHECKPOINT
            2. EVENT
            3. MOVE_CALL
            4. OBJECT
            5. PACKAGE
            6. TRANSACTION
            7. TRANSACTION_OBJECTS
    
    You can also run `createtables.py` found in https://github.com/SZNS/sui-etl/scripts. Make sure you have the gcloud SDK authenticated and run `gcloud auth application-default login`
