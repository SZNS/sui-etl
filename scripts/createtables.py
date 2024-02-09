import argparse
import os
from google.cloud import bigquery
from google.api_core import exceptions

def get_user_input(prompt, default=None):
    user_input = input(prompt)
    return user_input if user_input else default

def main(project_id, dataset_id, sql_directory):
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)

    # Check if the dataset exists and create it if not. Make sure it matches with dataset defined in the SQL files
    try:
        client.get_dataset(dataset_ref)  
        print(f"Dataset {dataset_id} already exists.")
    except exceptions.NotFound:
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
                query_job = client.query(sql_query, location='US')  
                query_job.result()  # Wait for the query to finish
                print(f"Table created successfully in dataset {dataset_id} from {filename}.")
            except Exception as e:
                print(f"Error creating table in dataset {dataset_id} from {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BigQuery SQL Importer")
    parser.add_argument("--project_id", help="Your Google Cloud project ID")
    parser.add_argument("--dataset_id", help="Your BigQuery dataset ID")
    parser.add_argument("--sql_directory", help="Directory containing SQL files")

    args = parser.parse_args()

    # If arguments are not provided, prompt the user for input
    project_id = args.project_id or get_user_input("Enter your project ID: ")
    dataset_id = args.dataset_id or get_user_input("Enter your dataset ID: ")
    sql_directory = args.sql_directory or get_user_input("Enter your directory containing the SQL files: ")

    main(project_id, dataset_id, sql_directory)