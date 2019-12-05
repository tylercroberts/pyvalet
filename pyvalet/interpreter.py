from io import StringIO
import requests
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import pandas as pd
from .exceptions import *


class BaseInterpreter(object):
    def __init__(self, logger=None):
        # These two attributes are the used to as the basis for all queries made to the Interpreter.
        self.base_url = ''
        self.url = self.base_url
        self._enable_logging(logger)

    def _enable_logging(self, logger):
        self.logger = logger

    def _reset_url(self):
        self.url = self.base_url

    def _set_endpoint(self, endpoint: str):
        self.url = f"{self.url}/{endpoint}"

    def _set_query(self, query: str):
        self.url = f"{self.url}?{query}"

    def _prepare_requests(self, *args, **kwargs):
        """All args are taken to be part of the endpoint, and all kwargs are taken to be the query."""
        for arg in args:
            if isinstance(arg, str):
                self._set_endpoint(arg)
            else:
                self._reset_url()
                raise ValueError('Arguments to prepare_requests must be a string')

        query_str = ""
        for k, v in kwargs.items():
            query_str += f"{k}={v}&"
        self._set_query(query_str)

        if self.logger is not None:
            self.logger.debug(f"Finished preparing request to: {self.url}")

    @staticmethod
    def _pandafy_response(response: str, skiprows: int = 0) -> pd.DataFrame:
        sio = StringIO(response)
        df = pd.read_csv(sio, skiprows=skiprows)
        return df


class ValetInterpreter(BaseInterpreter):

    def __init__(self, logger=None):
        # super doesn't do much in our case.
        super(ValetInterpreter, self).__init__(logger=logger)

        self.base_url = 'https://www.bankofcanada.ca/valet'
        self.url = self.base_url

        # These provide a cached version of results
        self.series_list = None
        self.groups_list = None

    def _get_lists(self, endpoint: str, response_format='csv'):
        self._prepare_requests('lists', endpoint, response_format)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} lists returned code {response.status_code}")

        return response

    def _get_details(self, detail_type: str, endpoint: str, response_format='csv'):
        self._prepare_requests(detail_type, endpoint, response_format)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {detail_type}/{endpoint} details returned code {response.status_code}")

        return response

    def _get_observations(self, endpoint: str, response_format='csv', **kwargs):
        # response_format must be positional because of how _prepare_requests works.
        self._prepare_requests('observations', endpoint, response_format, **kwargs)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} observations returned code {response.status_code}")

        return response

    def list_series(self, response_format='csv'):
        """

        Args:
            response_format (str): Currently only 'csv' is supported, json and xml potentially in the future.

        Returns:

        """
        if self.series_list is not None:
            return self.series_list
        else:
            if response_format != 'csv':

                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please use csv or check for updates on GitHub")

                raise NotImplementedError("JSON and XML not yet supported")
            else:
                response = self._get_lists('series', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} series in this list.")
                self._reset_url()
                self.series_list = df
                return df

    def list_groups(self, response_format='csv'):
        """

        Args:
            response_format (str): Currently only 'csv' is supported, json and xml potentially in the future.

        Returns:

        """
        if self.groups_list is not None:
            return self.groups_list
        else:
            if response_format != 'csv':
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please use csv or check for updates on GitHub")
                raise NotImplementedError("JSON and XML not yet supported")
            else:
                response = self._get_lists('groups', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} groups in this list.")
                self._reset_url()
                self.groups_list = df
                return df

    def _get_series_detail(self, series, response_format='csv'):
        if series in self.series_list['name'].unique():
            response = self._get_details('series', series, response_format=response_format)
            df = self._pandafy_response(response.text, skiprows=4)
        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")
        return df

    def get_series_detail(self, series, response_format='csv'):
        """

        Args:
            series (str):
            response_format (str): Currently only 'csv' is supported, json and xml potentially in the future.

        Returns:

        """
        if response_format != 'csv':
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please use csv or check for updates on GitHub")
            raise NotImplementedError("JSON and XML not yet supported")
        else:
            if self.series_list is None:
                self.list_series(response_format=response_format)
                self._reset_url()

            df = self._get_series_detail(series, response_format=response_format)
            self._reset_url()
            return df

    def _get_group_detail(self, group, response_format='csv'):
        if group in self.groups_list['name'].unique():
            response = self._get_details('groups', group, response_format=response_format)
            df = self._pandafy_response(response.text, skiprows=4)
            df_group = df.iloc[0]
            df_series = df.iloc[3:]
            if self.logger is not None:
                self.logger.debug(f"The {group} group has {df_series.shape[0]} series contained within it.")
        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet groups list")
            raise GroupException("The group passed does not lead to a Valet endpoint, "
                                 "check your spelling and try again.")
        return df_group, df_series

    def get_group_detail(self, group, response_format='csv'):
        """
        Interface for a user to get details about a group.
        Performs another query to ensure that the group actually exists.
        Args:
            group (str): Comes from `name` column of the `.groups_list` attribute.
            response_format (str): Currently only 'csv' is supported, json and xml potentially in the future.

        Returns:

        """
        if response_format != 'csv':
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please use csv or check for updates on GitHub")
            raise NotImplementedError("JSON and XML not yet supported")
        else:
            if self.groups_list is None:
                self.list_groups(response_format='csv')
                self._reset_url()

            df_group, df_series = self._get_group_detail(group, response_format='csv')
            self._reset_url()
            return df_group, df_series

    def _get_series_observations(self, series, response_format='csv', **kwargs):
        # Make sure that the series exists before bothering to send request.
        if series in self.series_list['name'].unique():
            response = self._get_observations(series, response_format=response_format, **kwargs)
            df = self._pandafy_response(response.text, skiprows=4)  # TODO: This will not work with comma sep series.
            df_series = df.iloc[0]
            df = df.iloc[3:]
            if self.logger is not None:
                self.logger.debug(f"The {series} series has {df.shape[0]} observations")
        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")

        return df_series, df

    def get_series_observations(self, series, response_format='csv', **kwargs):
        """
        # TODO: Add support for series as comma separated lists, as allowed by the API.
        Args:
            series (str):
            response_format (str): Currently only 'csv' is supported, json and xml potentially in the future.
            **kwargs: Key word arguments can include; `start_date`, `end_date`, `recent`, `recent_weeks`, `recent_days`,
            `recent_months`, `recent_years`,

        Returns:

            Terms and Conditions:
                url: The url to the terms and conditions for using content produced by the Bank of Canada
            Series Detail:
                id: The id of the specific series
                    label: The label of the series
                    description: The description of the series
                    dimension: The dimension for this series e.g. date, category, etc.
                        key: Short name for the dimension
                        name: Name for the dimension
            Observations:
                dimension: The dimension of the observation. Short key is used to define the field.
                value: The value of the observation

        """
        if response_format != 'csv':
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please use csv or check for updates on GitHub")
            raise NotImplementedError("JSON and XML not yet supported")
        else:
            if self.series_list is None:
                self.list_series(response_format='csv')
                self._reset_url()

            df = self._get_series_observations(series, response_format=response_format, **kwargs)
            self._reset_url()
            return df

    @staticmethod
    def _parse_group_observations(response):
        # TODO: Should really do some more splitting to get the details for the group & all series to be consistent
        splits = response.text.split("OBSERVATIONS")
        return splits[1]

    def _get_group_observations(self, group, response_format='csv', **kwargs):
        # Make sure that the series exists before bothering to send request.
        if group in self.groups_list['name'].unique():
            response = self._get_observations(f"group/{group}", response_format=response_format, **kwargs)
            cleaned = self._parse_group_observations(response)
            df = self._pandafy_response(cleaned, skiprows=0)  # TODO: This will not work with comma sep series.
            if self.logger is not None:
                self.logger.debug(f"The {group} group has {df.shape[0]} observations")
        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise GroupException("The series passed does not lead to a Valet endpoint, "
                                 "check your spelling and try again.")

        return df

    def get_group_observations(self, group, response_format='csv', **kwargs):
        if response_format != 'csv':
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please use csv or check for updates on GitHub")
            raise NotImplementedError("JSON and XML not yet supported")
        else:
            if self.groups_list is None:
                self.list_groups(response_format='csv')
                self._reset_url()

            df = self._get_group_observations(group, response_format=response_format, **kwargs)
            self._reset_url()
            return df