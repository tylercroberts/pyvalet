"""
Interpreter module for `pyvalet`

This module defines the base class, and concrete implementation for our API wrapper.
"""

import requests

from io import StringIO
from pathlib import Path
import pandas as pd
from .exceptions import *


class BaseInterpreter(object):

    def __init__(self, logger=None):
        """
        In any subclass, base_url should be set to whatever the root URL would be, and self.url will be
        set temporarily to be the same.

        Args:
            logger : Logging Handler. I tested with `loguru`, but a configured Handler from `logging` should also work.
        """

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
    def _pandafy_response(response: str, skiprows: int = 0,) -> pd.DataFrame:
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
        #self.series_list = None
        #self.groups_list = None
        #needs to be in correct format
        self.series_list = {}
        self.groups_list = {}
        self.series_list['csv']=None
        self.series_list['json']=None
        self.series_list['xml']=None
        self.groups_list['csv']=None
        self.groups_list['json']=None
        self.groups_list['xml']=None


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
        if self.series_list[response_format] is not None:
            return self.series_list[response_format]
        else:
            if response_format == 'csv':
                response = self._get_lists('series', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} series in this list.")
                self._reset_url()
                self.series_list[response_format] = df
                return df
            elif response_format == 'json':
                response = self._get_lists('series', response_format=response_format)
                js = response.json(strict=False)
                #print("series_list: ",js)
                if self.logger is not None:
                    self.logger.debug(f"There are {len(js)} series in this list.")
                self._reset_url()
                self.series_list[response_format] = js
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
        if self.groups_list[response_format] is not None:
            return self.groups_list[response_format]
        else:
            if response_format == 'csv':
                response = self._get_lists('groups', response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                if self.logger is not None:
                    self.logger.debug(f"There are {df.shape[0]} groups in this list.")
                self._reset_url()
                self.groups_list[response_format] = df
                return df
            elif response_format == 'json':
                response = self._get_lists('groups', response_format=response_format)
                self._reset_url()
                js = response.json(strict=False)
                self.groups_list[response_format] = js
                return js
            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please check for updates on GitHub")
                raise NotImplementedError("XML not yet supported")


    def _get_lists(self, endpoint: str, response_format='csv'):

        #/lists/listName/json
        self._prepare_requests('lists', endpoint, response_format)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} lists returned code {response.status_code}")

        return response

    def _get_details(self, detail_type: str, endpoint: str, response_format='csv'):
        '''
        /series/seriesName or /groups/groupName

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


        '''


        self._prepare_requests(detail_type, endpoint, response_format)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {detail_type}/{endpoint} details returned code {response.status_code}")

        return response

    def _get_observations(self, endpoint: str, response_format='csv', **kwargs):
        # response_format must be positional because of how _prepare_requests works.
        #/observations/seriesNames/format?query
        #/observations/group/groupName/format?query
        self._prepare_requests('observations', endpoint, response_format, **kwargs)
        response = requests.get(self.url)

        if self.logger is not None:
            self.logger.debug(f"Query for {endpoint} observations returned code {response.status_code}")

        return response


    def _get_series_detail(self, series, response_format='csv'):
        if response_format=='csv':
            if series in self.series_list[response_format]['name'].unique():
                response = self._get_details('series', series, response_format=response_format)
                df = self._pandafy_response(response.text, skiprows=4)
                return df
            else:
                if self.logger is not None:
                    self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
                raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                      "check your spelling and try again.")

        elif response_format=='json':
            if series in self.series_list[response_format]['series']:
                response = self._get_details('series', series, response_format=response_format)
                return response.json(strict=False)
            else:
                if self.logger is not None:
                    self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
                raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                      "check your spelling and try again.")

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")


    def get_series_detail(self, series, response_format='csv'):
        """
        /series/seriesName
        Series Details: The details for the requested series
            name: The id of the requested series
            label: The title of the requested series
            description: The description of the requested series

        Interface to get details on a specified series.
        Performs another query to ensure that the group actually exists.

        Args:
            series (str): Series name. You can find a list of these by calling `.list_series()`
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            'csv': (pd.DataFrame) with columns: name, label, description
            'json': (dict)
        """
        if response_format == 'csv':
            if self.series_list[response_format] is None:
                self.list_series(response_format=response_format)
                self._reset_url()

            df = self._get_series_detail(series, response_format=response_format)
            self._reset_url()
            return df

        elif response_format == 'json':
            if self.series_list[response_format] is None:
                self.list_series(response_format=response_format)
                self._reset_url()

            js = self._get_series_detail(series, response_format=response_format)
            self._reset_url()
            return js
        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")


    def _get_group_detail(self, group, response_format='csv'):
        '''
            /groups/groupName
            Group Details: The details for the requested series group
                name: The id of the requested group
                label: The title of the requested group
                description: The description of the requested group
                groupSeries: The series within the requested group
                    name: The id of the series
                        label: The title of the series
                        link: The link to the series details


        '''
        groups_list = []
        if response_format == 'csv':
            groups_list = self.groups_list[response_format]['name'].unique()
        elif response_format == 'json':
            groups_list = self.groups_list[response_format]['groups'].keys()
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
                js=response.json(strict=False)
                js_group = js['groupDetails']
                js_series = js['groupDetails']['groupSeries']
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {len(js_series)} series contained within it.")
                return js_group, js_series

            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please check for updates on GitHub")
                raise NotImplementedError("XML not yet supported")


        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet groups list")
            raise GroupException("The group passed does not lead to a Valet endpoint, "
                                     "check your spelling and try again.")


    def get_group_detail(self, group, response_format='csv'):
        """
        Interface for a user to get details about a group.
        Performs another query to ensure that the group actually exists.

        Args:
            group (str): Comes from `name` column of the `.groups_list` attribute.
            response_format (str): Currently only 'csv' and 'json' are supported and xml potentially in the future.

        Returns:
            'csv': (pd.Series, pd.DataFrame) Both outputs have 3 columns: name, label, description.
            'json': (dict of group, dict of group series)

        """
        if response_format == 'csv':
            if self.groups_list[response_format] is None:
                self.list_groups(response_format=response_format)
                self._reset_url()

            df_group, df_series = self._get_group_detail(group, response_format=response_format)
            self._reset_url()
            return df_group, df_series
        elif response_format == 'json':
            if self.groups_list[response_format] is None:
                self.list_groups(response_format=response_format)
                self._reset_url()

            js_group, js_series = self._get_group_detail(group, response_format=response_format)
            self._reset_url()
            #print("js_group: ",js_group)
            #print("js_series: ", js_series)
            return js_group, js_series

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("JSON and XML not yet supported")

    def _get_series_observations(self, series, response_format='csv', **kwargs):
        all_series=[]
        if response_format == 'csv':
            all_series = list(self.series_list[response_format]['name'].unique())
        elif response_format == 'json':
            all_series = list(self.series_list[response_format]['series'].keys())

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
            # For passed single string.
            if response_format=='csv':
                response = self._get_observations(series, response_format=response_format, **kwargs)
                df = self._pandafy_response(response.text, skiprows=4)  # TODO: This will not work with comma sep series.
                df_series = df.iloc[0:n_series]
                df = df.iloc[1+n_series:]
                headers = df.iloc[0]
                df = pd.DataFrame(df.values[1:], columns=headers)
                if self.logger is not None:
                    self.logger.debug(f"The {series} series has {df.shape[0]} observations")

                #print("df_series: ",df_series)
                #print("df: ",df)

                return df_series, df

            elif response_format=='json':
                response = self._get_observations(series, response_format=response_format, **kwargs)
                js=response.json(strict=False)
                js_series = js["observations"]
                if self.logger is not None:
                    self.logger.debug(f"The {series} series has {len(js_series)} observations")

                return js_series, series

        else:

            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")


    def get_series_observations(self, series, response_format='csv', **kwargs):
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
            if self.series_list[response_format] is None:
                self.list_series(response_format=response_format)
                self._reset_url()

            df, _ = self._get_series_observations(series, response_format=response_format, **kwargs)
            self._reset_url()
            #print("df: ",df)
            return df #only getting observations and returning observations df_series
        elif response_format == 'json':
            if self.series_list[response_format] is None:
                self.list_series(response_format=response_format)
                self._reset_url()

            js, _ = self._get_series_observations(series, response_format=response_format, **kwargs)
            self._reset_url()
            #print("js: ",js)
            return js

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")


    @staticmethod
    def _parse_group_observations(response: requests.Response) -> (str, str):
        split1 = response.text.split('\n"SERIES"')
        of_interest = split1[1]
        split2 = of_interest.split("OBSERVATIONS")
        # Remove the unnecessary line at the end of the first split, return both csv strings.
        return "".join(split2[0].split("\n\n")[:-1]), split2[1]

    def _get_group_observations(self, group: str, response_format: str='csv', **kwargs):
        # Make sure that the series exists before bothering to send request.
        group_list=[]
        if response_format == 'csv':
            group_list=self.groups_list[response_format]['name'].unique()
        if response_format == 'json':
            group_list=self.groups_list[response_format]['groups'].keys()

        if group in group_list:
            response = self._get_observations(f"group/{group}", response_format=response_format, **kwargs)
            if response_format == 'csv':
                series_str, obs_str = self._parse_group_observations(response)
                df_series = self._pandafy_response(series_str, skiprows=0)
                df = self._pandafy_response(obs_str, skiprows=0)
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {df.shape[0]} observations")
                #print("group df_series: ", df_series )
                #print("group dfs: ", df )
                return df_series, df
            elif response_format == 'json':
                js=response.json(strict=False)
                js_series = js["seriesDetail"]
                js = js["observations"]
                if self.logger is not None:
                    self.logger.debug(f"The {group} group has {len(js_series)} observations")
                #print("group js_series: ", js_series )
                #print("group js: ", js )

                return js_series, js

            else:
                if self.logger is not None:
                    self.logger.debug(f"{response_format} is not yet supported, "
                                      f"please use csv or check for updates on GitHub")
                raise NotImplementedError("JSON and XML not yet supported")

        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise GroupException("The series passed does not lead to a Valet endpoint, "
                                 "check your spelling and try again.")



    def get_group_observations(self, group: str, response_format: str = 'csv', **kwargs):
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
            if self.groups_list[response_format] is None:
                self.list_groups(response_format='csv')
                self._reset_url()

            df_series, df = self._get_group_observations(group, response_format=response_format, **kwargs)
            self._reset_url()
            return df_series, df
        elif response_format == 'json':
            if self.groups_list[response_format] is None:
                self.list_groups(response_format='json')
                self._reset_url()

            js_series, js = self._get_group_observations(group, response_format=response_format, **kwargs)
            self._reset_url()
            return js_series, js

        else:
            if self.logger is not None:
                self.logger.debug(f"{response_format} is not yet supported, "
                                  f"please check for updates on GitHub")
            raise NotImplementedError("XML not yet supported")




    def _get_fx_rss(self, endpoint):

        # response_format must be positional because of how _prepare_requests works.
        self._prepare_requests('fx_rss', endpoint)
        response = requests.get(self.url)
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
        # Make sure that the series exists before bothering to send request.
        response_format='csv'
        if self.series_list[response_format] is None:
            self.list_series(response_format='csv')
            self._reset_url()

        all_series = list(self.series_list[response_format]['name'].unique())

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
            self._reset_url()
            return response.text

        else:
            if self.logger is not None:
                self.logger.debug(f"The endpoint: {self.url} does not exist in the current Valet series list")
            raise SeriesException("The series passed does not lead to a Valet endpoint, "
                                  "check your spelling and try again.")
