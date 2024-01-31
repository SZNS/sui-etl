from google.cloud import bigquery
from google.api_core import exceptions  
import os

# Script creates tables according to schema definitions in SQL files found here: https://github.com/MystenLabs/sui/tree/main/crates/sui-analytics-indexer/src/store/bq/schemas

# Set project ID, dataset ID, and directory 
project_id = 'your project id' # replace with your project ID
dataset_id = 'chaindata' # check to make sure dataset name matches with the one defined in the sql files
sql_directory = 'sql' # replace with your directory containing the SQL files

client = bigquery.Client(project=project_id)
dataset_ref = client.dataset(dataset_id)

# Check if the dataset exists and create it if not
dataset_ref = client.dataset(dataset_id)
try:
    client.get_dataset(dataset_ref)  # Check if dataset exists
    print(f"Dataset {dataset_id} already exists.")
except exceptions.NotFound:  # Use the correct exception class
    print(f"Dataset {dataset_id} does not exist. Creating it...")
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = 'US'  # Set dataset location (optional)
    client.create_dataset(dataset)


for filename in os.listdir(sql_directory):
    if filename.endswith('.sql'):
        filepath = os.path.join(sql_directory, filename)
        with open(filepath, 'r') as f:
            sql_query = f.read()

        try:
            print(f"Executing SQL query from {filename}...")
            query_job = client.query(sql_query, location='US')  # Specify a location if needed
            query_job.result()  # Wait for the query to finish
            print(f"Table created successfully in dataset {dataset_id} from {filename}.")
        except Exception as e:
            print(f"Error creating table in dataset {dataset_id} from {filename}: {e}")
