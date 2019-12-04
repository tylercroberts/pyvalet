import time
import pytest
import pandas as pd
from pyvalet import ValetInterpreter


def test_lists():

    vi = ValetInterpreter()
    # Test that the list endpoints are still valid. This may make debugging easier if they change, or become outdated.
    response = vi._get_lists('series', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()
    response = vi._get_lists('groups', response_format='csv')
    assert response.status_code == 200
    vi._reset_url()

    df = vi.list_series(response_format='csv')
    assert isinstance(df, pd.DataFrame)
    df = vi.list_groups(response_format='csv')
    assert isinstance(df, pd.DataFrame)

    with pytest.raises(NotImplementedError):
        vi.list_series(response_format='json')
    with pytest.raises(NotImplementedError):
        vi.list_groups(response_format='json')




