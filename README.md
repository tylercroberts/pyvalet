# pyvalet
![](https://travis-ci.com/tylercroberts/pyvalet.svg?branch=master) ![](https://img.shields.io/badge/Python-3.6-blue)

Simple, pandas integrated API wrapper for the Bank of Canada Valet API

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
vi.get_series_detail("FXUSDCAD", response_format='csv')

vi.get_group_detail("FX_RATES_DAILY", response_format='csv')
```
