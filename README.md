# pyvalet
![](https://travis-ci.com/tylercroberts/pyvalet.svg?branch=master)
![](tests/results/coverage.svg)
![](https://img.shields.io/badge/Python-3.6-blue)

Simple, pandas integrated API wrapper for the Bank of Canada Valet API.

Their documentation page can be found [here](https://www.bankofcanada.ca/valet/docs)

### Installation:
To install this package

### Getting Started:

To get started using `pyvalet`, simply open up a new python file and type:
```python
from pyvalet import ValetInterpreter

vi = ValetInterpreter()
```

This will be your interface with all the features of pyvalet.

To see what sort of data is available, try running one of the following commands:

```python
vi.list_series()

vi.list_groups()
```

These two commands will provide you with a `pandas` DataFrame containing all possible series, 
or groups to explore using the Valet API. The three fields output are 'name', 'label' and 'link'.

The first time you run these commands, the ValetInterpreter will cache them 
so there is no need to assign the output, unless you plan to filter these lists.

They can be accessed through:
```python
vi.series_list

vi.groups_list
```


To get more details about these series or groups, the `get_series_detail()` 
or `get_group_detail()` methods are available
```python
df = vi.get_series_detail("FXUSDCAD", response_format='csv')

df_group, df_series = vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
```

The output of `.get_series_detail()` is  a `pandas` DataFrame containing, among other things, 
the name and description of a given series.

The output of `.get_group_detail()` is one `pandas` Series, and one DataFrame. The Series containing details
about the group itself, and the DataFrame containing the same information about all series in the group.

Diving even deeper, you can pull observations from these series or groups using the `get_series_observations()`
and `get_groups_observations()` methods.

```python
df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv')
```

Additional keyword arguments can be passed to alter the query. See the docstrings for more information.

Like the methods for group details, the output of `get_series_observations()` is one `pandas` Series, 
and one DataFrame. The Series contains the details for the series queries, 
and the DataFrame contains the observations themselves.