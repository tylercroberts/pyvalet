"""
Interpreter module for `pyvalet`

This module defines the base class, and concrete implementation for our API wrapper.
"""
import re
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
from typing import Tuple, Any, Dict, List
from requests.exceptions import Timeout, HTTPError
import re
from .exceptions import *


class BaseInterpreter(object):

    def __init__(self, logger=None, timeout=10):
        """
        In any subclass, base_url should be set to whatever the root URL would be, and self.url will be
        set temporarily to be the same.

        Args:
            logger : Logging Handler. I tested with `loguru`, but a configured Handler from `logging` should also work.
        """

        self.base_url = ''
        self.url = self.base_url
        self.timeout = timeout
        self._enable_logging(logger)

    def _enable_logging(self, logger):
        self.logger = logger

    def update_url(self, addition: str, base_url=None):
        if base_url is None:
            return f"{self.base_url}/{addition}"
        else:
            return f"{base_url}/{addition}"


    def _prepare_request(self, *args, **kwargs):
        """All args are taken to be part of the endpoint, and all kwargs are taken to be the query."""
        request_url = self.base_url
        for arg in args:
            if isinstance(arg, str):
                request_url = self.update_url(arg, base_url=request_url)
            else:
                raise ValueError('Arguments to prepare_requests must be a string')

        query_str = ""
        for k, v in kwargs.items():
            query_str += f"{k}={v}&"
        request_url += f"?{query_str}"

        if self.logger is not None:
            self.logger.debug(f"Finished preparing request to: {self.url}")
        return request_url

    def requests_get(self, url):
        try:
            response = requests.get(url,timeout=self.timeout)
            response.raise_for_status()
            return response

        except Exception as e:
            # should be: except Timeout
            # bug in requests
            # https://github.com/psf/requests/issues/5430
            # work-around?
            if re.search('Read timed out', str(e), re.IGNORECASE):
                if self.timeout < 1000:  # try again
                    self.timeout = self.timeout * 10
                    if self.logger is not None:
                        self.logger.info(f'Retrying with timeout: {self.timeout}')
                    response = self.requests_get(url)
                    return response
                elif self.logger is not None:
                    self.logger.error(f'Timeout error occurred: {e}.\nThe request timed out with timeout: {self.timeout}')
            elif self.logger is not None:
                self.logger.error(f'Other error occurred: {e}')

            raise BOCException(f'BOC Exception - {e}')

    @staticmethod
    def _pandafy_response(response: str, skiprows: int = 0,) -> pd.DataFrame:
        """TODO: This maybe shouldn't be static and should try to figure out types based on the `details_df`"""
        sio = StringIO(response)
        df = pd.read_csv(sio, skiprows=skiprows)
        df = df.dropna(axis=1, how='all')  # Drop any cols where all value are na
        for column in df.columns:
            # Specifically for FRX, will parse into float
            if re.match("FX[A-Z]{3}[A-Z]{3}", str(column)) is not None:
                df.loc[:, column] = df.loc[:, column].astype(float)

        return df


class ValetInterpreter(BaseInterpreter):

    def __init__(self, logger=None, timeout=10, check=True):
        # super doesn't do much in our case.
        super(ValetInterpreter, self).__init__(logger=logger, timeout=timeout )

        self.base_url = 'https://www.bankofcanada.ca/valet'
        self.timeout = timeout
        self.check = check

        # These provide a cached version of results
        # need to be in correct format
        self.series_dict = dict()
        self.groups_dict = dict()
        self.series_dict['csv'] = None
        self.series_dict['json'] = None
        self.series_dict['xml'] = None
        self.groups_dict['csv'] = None
        self.groups_dict['json'] = None
        self.groups_dict['xml'] = None

    def list_series(self, response_format='csv'):
        """
        Provides a list of all valid series endpoints.

        Args:
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            if 'csv':
            (pd.DataFrame) with columns: name, label, description.
            if 'json':
            (dict)

        """
        if self.series_dict[response_format] is not None:
            return self.series_dict[response_format]

        else:
            if response_format == 'csv':
                response = self._get_lists('series', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} series in this list.")
                self.series_dict[response_format] = df
                return df

            elif response_format == 'json':
                response = self._get_lists('series', response_format=response_format)
                js = response.json(strict=False)
                if self.logger is not None:
                    self.logger.debug(f"There are {len(js)} series in this list.")
                self.series_dict[response_format] = js
                return js

            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please check for updates on GitHub")

                raise NotImplementedError(" XML not yet supported")

    def list_groups(self, response_format='csv'):
        """

        Provides a list of all valid series endpoints.

        Args:
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            'cvs': (pd.DataFrame) with columns: name, label, description.
            'json': (dict): {name:{label,description}}
        """
        if self.groups_dict[response_format] is not None:
            return self.groups_dict[response_format]

        else:
            if response_format == 'csv':
                response = self._get_lists('groups', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} groups in this list.")
                self.groups_dict[response_format] = df
                return df

            elif response_format == 'json':
                response = self._get_lists('groups', response_format=response_format)
                js = response.json(strict=False)
                self.groups_dict[response_format] = js
                return js

            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please check for updates on GitHub")
                raise NotImplementedError("XML not yet supported")

    def _get_lists(self, endpoint: str, response_format='csv'):

        # /lists/listName/json
        request_url = self._prepare_request('lists', endpoint, response_format)
        response = self.requests_get(request_url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} lists returned code {response.status_code}")

        return response

    def _get_details(self, detail_type: str, endpoint: str, response_format='csv'):
        """
        Makes query to /series/seriesName or /groups/groupName

        Args:
            detail_type:
            endpoint:
            response_format:

        Returns:
            Series Details: The details for the requested series
                name: The id of the requested series
                    label: The title of the requested series
                    description: The description of the requested series
            or

            Group Details: The details for the requested series group
                name: The id of the requested group
                label: The title of the requested group
                description: The description of the requested group
                groupSeries: The series within the requested group
                    name: The id of the series
                        label: The title of the series
                        link: The link to the series details
        """
        request_url = self._prepare_request(detail_type, endpoint, response_format)
        response = self.requests_get(request_url)


        if self.logger is not None:
            self.logger.debug(f"Query for {detail_type}/{endpoint} details returned code {response.status_code}")

        return response

    def _get_observations(self, endpoint: str, response_format, **kwargs):
        """
         Makes request to: /observations/seriesNames/format?query or /observations/group/groupName/format?query

        Args:
            endpoint:
            response_format:
            **kwargs: This will be a dict any query arguments you want to pass.

        Returns:
            Observations from the series, or all series in the group. Format will depend on what you're querying.
            See BoC Valet documentation for more details
        """

        # response_format must be positional because of how _prepare_requests works.
        request_url = self._prepare_request('observations', endpoint, response_format, **kwargs)
        response = self.requests_get(request_url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} observations returned code {response.status_code}")

        return response

    def _get_series_detail(self, series, response_format='csv'):
        series_list = [series]
        if self.check:
            if response_format == 'csv':
                series_list = self.series_dict[response_format]['name'].unique()
            elif response_format == 'json':
                series_list = self.series_dict[response_format]['series'].keys()

        if series in series_list:
            if response_format == 'csv':
                response = self._get_details('series', series, response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                return df

            elif response_format == 'json':
                response = self._get_details('series', series, response_format=response_format)
                return response.json(strict=False)
        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")

    def get_series_detail(self, series, response_format='csv'):
        """
        Makes request to: /series/seriesName


        Interface to get details on a specified series.
        Performs another query to ensure that the group actually exists.

        Args:
            series (str): Series name. You can find a list of these by calling `.list_series()`
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            'csv': (pd.DataFrame)
            'json': (dict)
                name: The id of the requested series
                label: The title of the requested series
                description: The description of the requested series
        """
        if self.series_dict[response_format] is None:
            if self.check:
                self.list_series(response_format=response_format)

        if response_format == 'csv':
            df = self._get_series_detail(series, response_format=response_format)
            return df

        elif response_format == 'json':
            js = self._get_series_detail(series, response_format=response_format)
            return js

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")

    def _get_group_detail(self, group, response_format='csv'):
        groups_list = [group]
        if self.check:
            if response_format == 'csv':
                groups_list = self.groups_dict[response_format]['name'].unique()
            elif response_format == 'json':
                groups_list = self.groups_dict[response_format]['groups'].keys()

        if group in groups_list:
            if response_format == 'csv':
                response = self._get_details('groups', group, response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                df_group = df.iloc[0]
                df_series = df.iloc[3:]
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {df_series.shape[0]} series contained within it.")
                return df_group, df_series

            elif response_format == 'json':
                response = self._get_details('groups', group, response_format=response_format)
                js = response.json(strict=False)
                js_group = js['groupDetails']
                js_series = js['groupDetails']['groupSeries']
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {len(js_series)} series contained within it.")
                return js_group, js_series

        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet groups list")
            raise GroupException("The group passed does not lead to a Valet endpoint, "
                                 "check your spelling and try again.")

    def get_group_detail(self, group, response_format='csv') -> Tuple[Any, Any]:
        """
        Interface for a user to get details about a group.
        Performs another query to ensure that the group actually exists.

        Args:
            group (str): Comes from `name` column of the `.groups_list` attribute.
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            'csv': Tuple[pd.Series, pd.DataFrame]
            'json': Tuple[Dict[str, Any], Dict[str,Any]]

            Group Details: The details for the requested series group
                name: The id of the requested group
                label: The title of the requested group
                description: The description of the requested group

            Group Series: The series within the requested group
                name: The id of the series
                label: The title of the series
                link: The link to the series details

        """
        if response_format == 'csv':
            if self.check and self.groups_dict[response_format] is None:
                self.list_groups(response_format=response_format)
            df_group, df_series = self._get_group_detail(group, response_format=response_format)
            return df_group, df_series
        elif response_format == 'json':
            if self.check and self.groups_dict[response_format] is None:
                self.list_groups(response_format=response_format)
            js_group, js_series = self._get_group_detail(group, response_format=response_format)
            return js_group, js_series

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")

    def _get_series_observations(self, series, response_format, **kwargs):

        all_series = []
        all_series.extend(series)
        if self.check:
            # Make sure that the series exists before bothering to send request.
            if response_format == 'csv':
                all_series = list(self.series_dict[response_format]['name'].unique())
            elif response_format == 'json':
                all_series = list(self.series_dict[response_format]['series'].keys())

        if (series in all_series) or isinstance(series, list):
            if isinstance(series, list):  # For passed list of strings.
                if all([s in all_series for s in series]):
                    n_series = len(series)
                    series = ",".join(series)
                else:
                    if self.logger is not None:
                        self.logger.debug(f"The endpoint: {self.url} contains a series which is not valid")
                    raise SeriesException("One of the series passed does not lead to a Valet endpoint, "
                                          "check your spelling and try again.")
            else:
                n_series = 1
            # For passed single string.
            if response_format == 'csv':
                response = self._get_observations(series, response_format, **kwargs)
                df = self._pandafy_response(response.text, skiprows=4)  # TODO: Will not work with comma sep series.
                df_series = df.iloc[0:n_series]
                df_obs = df.iloc[1+n_series:]
                headers = df_obs.iloc[0]
                df_obs = pd.DataFrame(df_obs.values[1:], columns=headers)
                df_obs.dropna()
                if self.logger is not None:
                    self.logger.debug(f"The {series} series has {df_obs.shape[0]} observations")

                return df_series, df_obs

            elif response_format == 'json':
                response = self._get_observations(series, response_format, **kwargs)
                js = response.json(strict=False)
                js_obs = js["observations"]
                if self.logger is not None:
                    self.logger.debug(f"The {series} series has {len(js_obs)} observations")

                return series, js_obs

        else:

            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")

    def get_series_observations(self, series, response_format, **kwargs):
        """
        Interface to pull observations for a given series.
        Performs another query to ensure the series exists on Valet

        Args:
            series (str or list): Series name. Currently only supports a single series.
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.
            **kwargs: Key word arguments can include; `start_date`, `end_date`, `recent`, `recent_weeks`, `recent_days`,
            `recent_months`, `recent_years`,

        Returns:
            'csv' :(pd.DataFrame) of observations for series
            'json' : (list) of observations for series

        """
        if response_format == 'csv':
            if self.series_dict[response_format] is None:
                self.list_series(response_format=response_format)

            _, df_obs = self._get_series_observations(series, response_format, **kwargs)
            return df_obs
        elif response_format == 'json':
            if self.series_dict[response_format] is None:
                self.list_series(response_format=response_format)

            _, js_obs = self._get_series_observations(series, response_format, **kwargs)
            return js_obs

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")

    @staticmethod
    def _parse_group_observations(response: requests.Response) -> (str, str):

        split1 = response.text.replace("\ufeff", "").split('\n"SERIES"')
        of_interest = split1[1]
        split2 = of_interest.split("OBSERVATIONS")
        # Remove the unnecessary line at the end of the first split, return both csv strings.
        return ",".join(split2[0].split("\r\n")[:-1]), split2[1]

    def _get_group_observations(self, group: str, response_format: str, **kwargs):

        group_list=[group]
        if self.check:
            if self.groups_dict.get(response_format, None) is None:
                self.list_groups(response_format)
            # Make sure that the series exists before bothering to send request.
            if response_format == 'csv':
                group_list = self.groups_dict[response_format]['name'].unique()
            if response_format == 'json':
                group_list = self.groups_dict[response_format]['groups'].keys()

        if group in group_list:
            response = self._get_observations(f"group/{group}", response_format, **kwargs)
            if response_format == 'csv':
                series_str, obs_str = self._parse_group_observations(response)
                df_series = self._pandafy_response(series_str, skiprows=0)
                df = self._pandafy_response(obs_str, skiprows=0)
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {df.shape[0]} observations")

                return df_series, df
            elif response_format == 'json':
                js = response.json(strict=False)
                js_series = js["seriesDetail"]
                js = js["observations"]
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {len(js_series)} observations")
                return js_series, js

            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please use csv or check for updates on GitHub")
                raise NotImplementedError("XML not yet supported")

        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise GroupException(f"The group passed ({group}) does not lead to a Valet endpoint, "
                                 "check your spelling and try again.")

    def get_group_observations(self, group: str, response_format: str, **kwargs):
        """
        Interface to pull observations for all series in a group.
        Performs another query to ensure the group exists as an endpoint on Valet

        Args:
            group (str): Group name. Can get a list of valid groups with `.list_groups()`
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.
            **kwargs:

        Returns:
            'csv': (pd.DataFrame, pd.DataFrame) : first is group series description, second are the observations
            'json': (dict, list)
        """
        if response_format == 'csv':
            if self.check and self.groups_dict[response_format] is None:
                self.list_groups(response_format='csv')

            df_series, df = self._get_group_observations(group, response_format, **kwargs)
            return df_series, df

        elif response_format == 'json':
            if self.check and self.groups_dict[response_format] is None:
                self.list_groups(response_format='json')

            js_series, js = self._get_group_observations(group, response_format, **kwargs)
            return js_series, js

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")

    def _get_fx_rss(self, endpoint):
        # response_format must be positional because of how _prepare_requests works.
        request_url = self._prepare_request('fx_rss', endpoint)
        response = self.requests_get(request_url)
        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} observations returned code {response.status_code}")
        return response

    def get_fx_rss(self, series: str or list):
        """
        Interface for accessing the RSS feeds offered by Valet.

        Args:
            series (str or list): Series name, or list of names.
                                  You can find a list of valid names by calling `.list_series()`

        Returns:
            (str) String containing xml documents text for the RSS feed.
        """

        response_format = 'csv'
        if self.series_dict[response_format] is None:
            self.list_series(response_format='csv')

        all_series = list(self.series_dict[response_format]['name'].unique())

        # Make sure that the series exists before bothering to send request.
        if (series in all_series) or isinstance(series, list):
            if isinstance(series, list):  # For passed list of strings.
                if all([s in all_series for s in series]):
                    n_series = len(series)
                    series = ",".join(series)
                else:
                    if self.logger is not None:
                        self.logger.debug(f"The endpoint: {self.url} contains a series which is not valid")
                    raise SeriesException("One of the series passed does not lead to a Valet endpoint, "
                                          "check your spelling and try again.")

            else:
                n_series = 1
            response = self._get_fx_rss(series)
            return response.text

        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")
