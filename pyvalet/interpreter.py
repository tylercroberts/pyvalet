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


