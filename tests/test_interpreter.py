import time
import pytest
import pandas as pd
from pyvalet import ValetInterpreter


def test_endpoints():
    vi = ValetInterpreter()
    # Test that the list endpoints are still valid. This may make debugging easier if they change, or become outdated.
    response = vi._get_lists('series', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()
    response = vi._get_lists('groups', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()

    with pytest.raises(ValueError):
        vi._prepare_requests('a', 2, 'c')


def test_lists():

    vi = ValetInterpreter()

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.list_series(response_format='json')
    with pytest.raises(NotImplementedError):
        vi.list_groups(response_format='json')

    # Time it so we can test that caching is working correctly.
    # Series Lists
    series_list_start = time.time()
    df = vi.list_series(response_format='csv')
    series_list_time = time.time() - series_list_start
    assert isinstance(df, pd.DataFrame)
    series_list_start2 = time.time()
    df = vi.list_series(response_format='csv')
    series_list_time2 = time.time() - series_list_start2
    assert series_list_time2 < series_list_time

    # Group Lists
    groups_list_start = time.time()
    df = vi.list_groups(response_format='csv')
    groups_list_time = time.time() - groups_list_start
    assert isinstance(df, pd.DataFrame)
    groups_list_start2 = time.time()
    df = vi.list_groups(response_format='csv')
    groups_list_time2 = time.time() - groups_list_start2
    assert groups_list_time2 < groups_list_time


def test_details():

    # TODO: Here we just test a sample of handcoded endpoints, may want to look at a broader selection.

    vi = ValetInterpreter()

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_detail('FXUSDCAD', response_format='json')
    with pytest.raises(NotImplementedError):
        vi.get_group_detail("FX_RATES_DAILY", response_format='json')

    # Time it so we can test that caching is working correctly.
    # Series Lists
    series_detail_start = time.time()
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')
    series_detail_time = time.time() - series_detail_start
    assert isinstance(df, pd.DataFrame)
    series_detail_start2 = time.time()
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')
    series_detail_time2 = time.time() - series_detail_start2
    assert series_detail_time2 < series_detail_time

    # Group Lists
    group_detail_start = time.time()
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    group_detail_time = time.time() - group_detail_start
    # Something weird going on here where the dataframes are not instances of dataframes even though they are.
    assert isinstance(df_group, pd.Series)
    assert isinstance(df_series, pd.DataFrame)
    group_detail_start2 = time.time()
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    group_detail_time2 = time.time() - group_detail_start2
    assert group_detail_time2 < group_detail_time


def test_observations():

    vi = ValetInterpreter()

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_observations('FXUSDCAD', response_format='json', end_date='2018-12-01')
    # with pytest.raises(NotImplementedError):
    #     vi.get_series_observations("FX_RATES_DAILY", response_format='json', end_date='2018-12-01')

    # Time it so we can test that caching is working correctly.
    # Series Lists
    series_obs_start = time.time()
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')
    series_obs_time = time.time() - series_obs_start
    assert isinstance(df_series, pd.Series)
    assert isinstance(df, pd.DataFrame)
    series_obs_start2 = time.time()
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')
    series_obs_time2 = time.time() - series_obs_start2
    assert series_obs_time2 < series_obs_time

