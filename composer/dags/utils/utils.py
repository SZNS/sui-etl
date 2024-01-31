import os
import logging 

def get_sql_query(file_name) :
    dags_folder = os.environ.get('DAGS_FOLDER', '/home/airflow/gcs/dags')
    sql_path = os.path.join(dags_folder, 'resources/verify/sqls/{name}.sql'.format(name=file_name))
    sql = read_file(sql_path)
    
    return sql

def read_file(filepath):
        with open(filepath) as file_handle:
            content = file_handle.read()
            return content