from io import StringIO
import requests
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import pandas as pd


class BaseInterpreter(object):
    def __init__(self):
        self.base_url = ''
        self.url = self.base_url

    def _reset_url(self):
        self.url = self.base_url

    def _set_endpoint(self, endpoint: str):
        self.url = f"{self.url}/{endpoint}"

    @staticmethod
    def _pandafy_response(response: requests.Response, skiprows: int = 0) -> pd.DataFrame:
        sio = StringIO(response.text)
        df = pd.read_csv(sio, skiprows=skiprows)
        return df


class ValetInterpreter(BaseInterpreter):

    def __init__(self):
        # super doesn't od much in our case.
        super(ValetInterpreter, self).__init__()

        self.base_url = 'https://www.bankofcanada.ca/valet'
        self.url = self.base_url

    def _get_lists(self, list_type, response_format='csv'):
        self._set_endpoint('lists')
        self._set_endpoint(list_type)
        self._set_endpoint(response_format)
        response = requests.get(self.url)
        return response


