from datetime import datetime

from airflow.models import Variable

def read_dag_vars(**kwargs):
    vars = {
        'project_id': read_var('project_id', False, **kwargs),
        'dataset_name': read_var('dataset_name', False, **kwargs),
        'notification_emails': read_var('notification_emails', False, **kwargs)
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