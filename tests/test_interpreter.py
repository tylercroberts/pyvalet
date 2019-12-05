import time
import pytest
import pandas as pd
from pyvalet import ValetInterpreter, SeriesException, GroupException


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
    df = vi.list_series(response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.list_series(response_format='csv')

    # Group Lists
    df = vi.list_groups(response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.list_groups(response_format='csv')


def test_details():
    # TODO: Here we just test a sample of handcoded endpoints, may want to look at a broader selection.

    vi = ValetInterpreter()

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_detail('FXUSDCAD', response_format='json')
    with pytest.raises(NotImplementedError):
        vi.get_group_detail("FX_RATES_DAILY", response_format='json')

    # Series Detail
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')

    # Group Detail
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    # Something weird going on here where the dataframes are not instances of dataframes even though they are.
    assert isinstance(df_group, pd.Series)
    assert isinstance(df_series, pd.DataFrame)
    # Need to call it again, to check the caching
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    with pytest.raises(SeriesException):
        # Test with a non-correct series or group name:
        df = vi.get_series_detail("NOTCORRECT", response_format='csv')
    with pytest.raises(GroupException):
        df = vi.get_group_detail("NOTCORRECT", response_format='csv')




def test_observations():
    vi = ValetInterpreter()

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_observations('FXUSDCAD', response_format='json', end_date='2018-12-01')
    # with pytest.raises(NotImplementedError):
    #     vi.get_series_observations("FX_RATES_DAILY", response_format='json', end_date='2018-12-01')

    # Series Lists
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')
    assert isinstance(df_series, pd.Series)
    assert isinstance(df, pd.DataFrame)
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')

    # Try an incorrect series name
    with pytest.raises(SeriesException):
        # Test with a non-correct series or group name:
        df = vi.get_series_observations("NOTCORRECT", response_format='csv')

    # Try without any kwargs:
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv')


