from datetime import datetime

from airflow.models import Variable

def read_dag_vars(**kwargs):
    vars = {
        'project_id': read_var('project_id', True, **kwargs),
        'dataset_name': read_var('dataset_name', True, **kwargs),
        'bucket_id': read_var('bucket_id', True, **kwargs),
        'notification_emails': read_var('notification_emails', False, **kwargs),
        'skip_load': read_var('skip_load', False, **kwargs)
    }
    
    return vars

def read_var(var_name, required=False, **kwargs):
    var = Variable.get(var_name, '')
    var = var if var != '' else None
    if var is None:
        var = kwargs.get(var_name)
    if required and var is None:
        raise ValueError(f'{var_name} variable is required')
    return var