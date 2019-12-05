import time
import pytest
import pandas as pd
from pyvalet import ValetInterpreter, SeriesException, GroupException
from loguru import logger
logger.add('logs/test_logs.log')


def test_interpreter():
    vi = ValetInterpreter()
    vi._enable_logging(logger=logger)


def test_endpoints():
    vi = ValetInterpreter(logger=logger)
    # Test that the list endpoints are still valid. This may make debugging easier if they change, or become outdated.
    response = vi._get_lists('series', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()
    response = vi._get_lists('groups', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()
    logger.info("Confirmed that endpoints are still valid for series list and groups list.")

    with pytest.raises(ValueError):
        vi._prepare_requests('a', 2, 'c')
    with pytest.raises(ValueError):
        vi._prepare_requests('a', ['hi'], 'c')
    with pytest.raises(ValueError):
        vi._prepare_requests('a', {'a':1}, 'c')
    with pytest.raises(ValueError):
        vi._prepare_requests('a', (1,2), 'c')

    logger.info("Confirmed that only strings will work for _prepare_requests()")
    logger.info("Completed tests for endpoints")


def test_lists():

    vi = ValetInterpreter(logger=logger)
    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.list_series(response_format='json')
    with pytest.raises(NotImplementedError):
        vi.list_groups(response_format='json')

    logger.info("Passed check for unsupported formats")

    # Series Lists
    df = vi.list_series(response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.list_series(response_format='csv')

    # Group Lists
    df = vi.list_groups(response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.list_groups(response_format='csv')
    logger.info("Checked that the lists are accessible, are cached correctly.")

    logger.info("Completed tests for lists")


def test_details():
    # TODO: Here we just test a sample of handcoded endpoints, may want to look at a broader selection.

    vi = ValetInterpreter(logger=logger)
    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_detail('FXUSDCAD', response_format='json')
    with pytest.raises(NotImplementedError):
        vi.get_group_detail("FX_RATES_DAILY", response_format='json')

    logger.info("Passed check for unsupported formats")

    # Series Detail
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.get_series_detail("FXUSDCAD", response_format='csv')

    # Group Detail
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    assert isinstance(df_group, pd.Series)
    assert isinstance(df_series, pd.DataFrame)
    df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
    logger.info("Checked that the details are accessible, are cached correctly.")


    with pytest.raises(SeriesException):
        # Test with a non-correct series or group name:
        df = vi.get_series_detail("NOTCORRECT", response_format='csv')
    with pytest.raises(GroupException):
        df = vi.get_group_detail("NOTCORRECT", response_format='csv')

    logger.info("Checked that the correct exceptions are raised when a series or group is not recognized.")
    logger.info("Completed tests for details")


def test_observations():
    vi = ValetInterpreter(logger=logger)

    # Check that the json/xml formats return correct error
    with pytest.raises(NotImplementedError):
        vi.get_series_observations('FXUSDCAD', response_format='json', end_date='2018-12-01')
    with pytest.raises(NotImplementedError):
        vi.get_group_observations("FX_RATES_DAILY", response_format='json', end_date='2018-12-01')
    logger.info("Passed check for unsupported formats")


    # Series Lists
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')
    assert isinstance(df_series, pd.DataFrame)
    assert isinstance(df, pd.DataFrame)
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv', end_date='2018-12-01')

    df_series, df = vi.get_group_observations("FX_RATES_DAILY", response_format='csv', end_date='2018-12-01')
    assert isinstance(df_series, pd.DataFrame)
    assert isinstance(df, pd.DataFrame)
    df_series, df = vi.get_group_observations("FX_RATES_DAILY", response_format='csv', end_date='2018-12-01')

    logger.info("Checked that the observations are accessible, lists are being cached")

    # Try an incorrect series name
    with pytest.raises(SeriesException):
        # Test with a non-correct series or group name:
        df_series, df = vi.get_series_observations("NOTCORRECT", response_format='csv')
    with pytest.raises(GroupException):
        # Test with a non-correct series or group name:
        df_series, df = vi.get_group_observations("NOTCORRECT", response_format='csv')

    logger.info("Passed check that the correct exceptions are raised when a series or group is not recognized.")

    # Try without any kwargs:
    df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv')

    # Try without any kwargs:
    df_series, df = vi.get_group_observations("FX_RATES_DAILY", response_format='csv')
    logger.info("Passed run of observations without kwargs")

    # Test multiple series:
    df_series, df = vi.get_series_observations(['FXUSDCAD', 'A.AGRI'],
                                               response_format='csv', end_date='2018-12-01')

    assert isinstance(df_series, pd.DataFrame)
    assert isinstance(df, pd.DataFrame)
    with pytest.raises(SeriesException):
        # One incorrect
        df_series, df = vi.get_series_observations(['FXUSDCAD', 'INCORRECT'],
                                                   response_format='csv', end_date='2018-12-01')


    logger.info("Completed tests for observations")


def test_fx_rss():
    vi = ValetInterpreter(logger=logger)
    rss = vi.get_fx_rss('FXUSDCAD')
    assert isinstance(rss, str)
    rss = vi.get_fx_rss('FXUSDCAD')  # Call again to check that caching works.

    # Check multiple series
    rss = vi.get_fx_rss(['FXUSDCAD', 'FXEURCAD'])
    assert isinstance(rss, str)

    with pytest.raises(SeriesException):
        rss = vi.get_fx_rss('INCORRECT')
    with pytest.raises(SeriesException):
        rss = vi.get_fx_rss(['FXUSDCAD', 'INCORRECT'])
