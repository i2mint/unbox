# unbox.dependencies

Functions to check for dependencies.

### Functions

| [`dependencies_from_pypi`](#unbox.dependencies.dependencies_from_pypi)(package_name, \*[, ...])   | Simply get a list of dependencies for a package from PyPI.   |
|----------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| `pypi_package_data`(package_name)                                                                  |                                                              |
| [`pypi_requires_dist`](#unbox.dependencies.pypi_requires_dist)(package_name)                  | Fetch dependencies for a package from PyPI.                  |

### unbox.dependencies.dependencies_from_pypi(package_name, \*, requirement_filter=<function <lambda>>, requirement_trans=<function <lambda>>, egress=<class 'list'>)

Simply get a list of dependencies for a package from PyPI.

```pycon
>>> dependencies_from_pypi('pandas')
['numpy', 'numpy', 'python-dateutil', 'pytz', 'tzdata']
```

But you have control over the requirements that are returned,
and how they are returned:

```pycon
>>> it = dependencies_from_pypi(
...     'pandas',
...     requirement_filter=lambda x: True,  # don't filter any requirements
...     requirement_trans=lambda x: x,  # as is
...     egress = lambda x: x  # just get the iterator as is
... )
>>> next(it)
'numpy>=1.22.4; python_version < "3.11"'
>>> list(it)[-1]
'zstandard>=0.17.0; extra == "all"'
```

### unbox.dependencies.pypi_requires_dist(package_name)

Fetch dependencies for a package from PyPI.

* **Parameters:**
  **package_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the package to fetch dependencies for.
* **Returns:**
  Dictionary containing package dependencies.
* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)
