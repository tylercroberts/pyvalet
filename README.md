# pyvalet
![](https://travis-ci.com/tylercroberts/pyvalet.svg?branch=master)
![](https://img.shields.io/pypi/v/pyvalet)
[![Coverage Status](https://coveralls.io/repos/github/tylercroberts/pyvalet/badge.svg?branch=master)](https://coveralls.io/github/tylercroberts/pyvalet?branch=master)
![](https://img.shields.io/badge/Python-3.6%2C%203.7-blue)

Simple, pandas integrated API wrapper for the Bank of Canada Valet API.

The Valet API provides programmatic access to all of the data made publicly available by the Bank of Canada, 
including daily foreign exchange rates, measures of geopolitical risk, mortgage refinancing information 
and bond rates, just to name a few.

The full Valet API documentation page can be found [here](https://www.bankofcanada.ca/valet/docs).

### Installation:
To install this package, you can find the latest stable release on PyPi
```sh
pip install pyvalet
```

Otherwise, you can install from source by first cloning the GitHub repo:
```sh
git clone https://github.com/tylercroberts/pyvalet.git

cd pyvalet
pip install -e .
```

If you wish to run tests, or build documentation, be sure to put `[tests]`, or `[docs]` after the `.`.
```sh
pip install -e ".[tests]"
pip install -e ".[docs]"
```

### Getting Started:

To get started using `pyvalet`, simply open up a new python file and type:
```python
from pyvalet import ValetInterpreter

vi = ValetInterpreter()
```

This will be your interface with all the features of pyvalet.

### Series and Group Lists:
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

### Series and Group Details:

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

### Series and Group Observations:

Diving even deeper, you can pull observations from these series or groups using the `get_series_observations()`
and `get_groups_observations()` methods.

```python**
df_series, df = vi.get_series_observations("FXUSDCAD", response_format='csv')
df = vi.get_group_observations("FX_RATES_DAILY", response_format='csv')
```

Additional keyword arguments can be passed to alter the query. See the docstrings for more information.

Like the methods for group details, the output of `get_series_observations()` and `get_groups_observations` 
is two `pandas` DataFrames, 
The first contains the details for either the series or group queried, 
and the second contains the observations themselves.


### RSS Feed for FX Rates:
`pyvalet` also offers an interface for pulling RSS feeds from the Valet API.

```python
vi.get_fx_rss("FXUSDCAD")
```
This command will accept any series name as an argument, and returns an XML string containing the RSS feed.

### Logging:
If you are encountering issues with `pyvalet`. 
You can enable debugging mode by passing a logging handler to the `logger` argument when instantiating the
ValetInterpreter object. This will output DEBUG level messages. It was tested using the `loguru` package, but
the base `logging` package, configured with a handler should work as well.


## Contributing:
You can run tests from the directory root with `pytest`. This will also generate a coverage report. 
Please be sure to write tests to cover any new code.

The documentation can be built from within the `docs` directory. 
It will use any `.rst` files found within the `source` subfolder to generate doc pages. 
If any new pages are added, you will need to also update `index.rst` so they will show up in the generated HTML.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for more details.