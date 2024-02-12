from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.models import Variable
from airflow.hooks.base import BaseHook

import requests
import logging


class EpochSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, endpoint, http_conn_id, request_params, headers, *args, **kwargs):
        super(EpochSensor, self).__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.http_conn_id = http_conn_id
        self.request_params = request_params
        self.headers = headers

    def poke(self, context):
        # Get connection URL from Airflow connection
        connection = BaseHook.get_connection(self.http_conn_id)
        url = f"{connection.host}{self.endpoint}"
        
        response = requests.post(url, json=self.request_params, headers=self.headers)
        if response.status_code == 200:
            response_json = response.json()
            observed_epoch = int(response_json.get('result', {}).get('epoch', 0))

            logging.info('The current epoch on chain is: {epoch}'.format(epoch=observed_epoch))

            # True if the epoch is greater to confirm the previous epoch closed out
            # Make sure to parse each as an int()
            return observed_epoch > int(Variable.get("epoch_run_index", default_var=0))
        else:
            return False