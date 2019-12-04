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







