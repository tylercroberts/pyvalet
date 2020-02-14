import json
import pandas
from io import StringIO

from loguru import logger

# Hard coding is bad but it will work barring any significant report changes.
SKIPROWS_MAP = {"list": 4, "details": 4, 'obs': 0}

class ResponseSet(object):
    """Simple class to abstract away output formatting details."""
    def __init__(self, response, response_format: str='csv', kind: str='list'):
        method_map = {'csv': self._to_csv, 
                      'json': self._to_json,
                      'xml': self._to_xml}
        if response_format not in method_map.keys():
            logger.warning(f"{response_format} was passed, but does not have a parsing method registered in the method map.")
            raise NotImplementedError(f"{response_format} is not yet supported, "
                                        f"please use csv, json, xml, or check for updates on GitHub")
        self._response = response
        self._func = method_map[response_format]
        self._skiprows = SKIPROWS_MAP[kind]
    
    def values(self):
        try:
            return self._func()
        except Exception as e:
            logger.error(f"Something went wrong in formatting the response! {e}")

    def _to_json(self):
        return json.loads(response.text)

    def _to_xml(self):
        return self._response.text

    def _to_csv(self):
        sio = StringIO(self._response)
        df = pd.read_csv(sio, skiprows=skiprows)
        return df