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

    def list_series(self, response_format='csv'):
        response = self._get_lists('series', response_format=response_format)
        if response_format == 'csv':
            df = self._pandafy_response(response, skiprows=4)
            self._reset_url()
            return df
        else:
            raise NotImplementedError("JSON and XML not yet supported")

    def list_groups(self, response_format='csv'):
        response = self._get_lists('groups', response_format=response_format)
        if response_format == 'csv':
            df = self._pandafy_response(response, skiprows=4)
            self._reset_url()
            return df
        else:
            raise NotImplementedError("JSON and XML not yet supported")

    def get_series_detail(self, series, response_format='csv'):
        pass

