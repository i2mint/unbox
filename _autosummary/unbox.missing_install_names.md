# unbox.missing_install_names

Finding missing install names

For doing things like:

```pycon
>>> from unbox import print_missing_names
>>> import unbox
>>> print_missing_names(unbox)
bs4
requests
```

#### NOTE
These missing dependencies are real, unpurpose, but don’t affect you.

You can get the set of missing install names as well as the set of install names
that are not used.

What does this mean?

Install names are those you have declared you needed to install the packages: the
`[project] dependencies` of your `pyproject.toml`, or the `[options]
install_requires` of your `setup.cfg` if that’s what you use. Both are read
(`pyproject.toml` first) – see `find_install_names`.

Why are the missing or unused? It has to do with imports. If you declared you needed a
package to be installed (a dependency) but never import it, it’s unused.
More importantly, if you use (that is import) a package, but haven’t listed it in the
names to be installed, that’s a problem for your users.

There’s several problems to solve here (and you have function here to solve them).

One problem: finding the names that are imported. That’s solved by `import_for` and
the many subfunctions like `import_for.third_party`.

Another problem is that the names that are imported are not necessarily the names that
should be installed.
For example, you `import sklearn` but you `pip install scikit-learn`.
That’s annoying. So we need a mapping between import names and install names.

So we provide a default mapping (which we will expand as users notify us, or we
encounter more of those aggravating cases.

That said, we provide ways for users to specify their own map.

You can specify an explicit mapping from import name to install name in the form of a
dict or any other valid `Mapping` instance. You can also add a
`IMPORT_TO_INSTALL_NAME_MAP_FILE` environmental variable pointing to a JSON file path
that will be used if this explicit mapping is not given.
If you do none of those, the system will use the default mapping, which is expressed by
the `unbox/data/dflt_import_to_install_name_map.json` file in the packaged data.

Besides the import vs install name discrepency, there are other reasons you may want
to specify your own map.
You may want to depend on a particular version of a third-party package,
or ensure that the version is greater than a minimum version. So the import names
you extracted need to be mapped to a fuller specification. For example, instead
of just requiring `numpy` you may want to have `numpy >= 1.3` in your
`setup.cfg` or `requirements.txt`.

### Module Attributes

| [`DFLT_INSTALL_NAMES_FINDERS`](#unbox.missing_install_names.DFLT_INSTALL_NAMES_FINDERS)   | Sources of declared install names, tried in order by `find_install_names`.   |
|-------------------------------------------------------------------------------|------------------------------------------------------------------------------|

### Functions

| [`dependencies_from_pyproject_content`](#unbox.missing_install_names.dependencies_from_pyproject_content)(...[, ...])     | Extract the declared dependencies from `pyproject.toml` text (PEP 621).                                                           |
|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| [`dependencies_from_setup_configs`](#unbox.missing_install_names.dependencies_from_setup_configs)(setup_configs)      | Generate all dependencies from a mapping of setup.cfg files.                                                                      |
| [`dependencies_from_setup_configs_content`](#unbox.missing_install_names.dependencies_from_setup_configs_content)(...)        | Extract dependencies from a single setup.cfg file content.                                                                        |
| [`dependency_diff`](#unbox.missing_install_names.dependency_diff)(install_names[, ...])               | Diff declared install names against the install names the imports call for.                                                       |
| [`dependency_diff_for_pkg`](#unbox.missing_install_names.dependency_diff_for_pkg)(pkg[, ...])                 | Get the imported names that are not declared to be installed those names declared to be installed that are not actually imported. |
| [`find_install_names`](#unbox.missing_install_names.find_install_names)(pkg, \*[, finders])              | Find the install names (dependencies) a package declares.                                                                         |
| [`get_import_names`](#unbox.missing_install_names.get_import_names)(import_names[, imports_finder])    | Get the import names from the given input.                                                                                        |
| `get_import_to_install_name_map`(...)                                                                |                                                                                                                                   |
| `get_install_names`(install_names[, ...])                                                            |                                                                                                                                   |
| `get_module_obj`(module)                                                                             |                                                                                                                                   |
| [`get_pyproject_path`](#unbox.missing_install_names.get_pyproject_path)(x)                               | Flexible search for the `pyproject.toml` path for an object x                                                                     |
| [`get_setupcfg_path`](#unbox.missing_install_names.get_setupcfg_path)(x)                                | Flexible search for the `setup.cfg` path for an object x                                                                          |
| [`install_names_for_imports`](#unbox.missing_install_names.install_names_for_imports)(import_names[, ...])      | Get a set of install names, i.e. names that are used in `pip install PKG_NAME`.                                                   |
| [`install_names_from_pyproject_file`](#unbox.missing_install_names.install_names_from_pyproject_file)(pkg, \*[, ...])   | Get dependencies from a package's `pyproject.toml`.                                                                               |
| [`install_names_from_setup_cfg_file`](#unbox.missing_install_names.install_names_from_setup_cfg_file)(pkg)              | Get dependencies from setup.cfg file(s).                                                                                          |
| [`install_requires_of_module`](#unbox.missing_install_names.install_requires_of_module)(pkg)                     | Get dependencies from setup.cfg file(s).                                                                                          |
| `map_if_found`(mapping, to_map[, strict])                                                            |                                                                                                                                   |
| [`module_requirements_according_to_pyproject`](#unbox.missing_install_names.module_requirements_according_to_pyproject)(pkg, \*) | Get dependencies from a package's `pyproject.toml`.                                                                               |
| [`module_requirements_according_to_setupcfg`](#unbox.missing_install_names.module_requirements_according_to_setupcfg)(pkg)      | Get dependencies from setup.cfg file(s).                                                                                          |
| `pkg_root_dir_name`(pkg)                                                                             |                                                                                                                                   |
| [`print_missing_names`](#unbox.missing_install_names.print_missing_names)(pkg[, ...])                     | See `dependency_diff_for_pkg` for more info (including `exclude_tests`).                                                          |

### Exceptions

| [`ProbablyPythonPathError`](#unbox.missing_install_names.ProbablyPythonPathError)   | To raise when a module requested is probably not on the python path   |
|----------------------------------------------------------------------------|-----------------------------------------------------------------------|

### unbox.missing_install_names.DFLT_INSTALL_NAMES_FINDERS *= (<function module_requirements_according_to_pyproject>, <function module_requirements_according_to_setupcfg>)*

Sources of declared install names, tried in order by `find_install_names`.

### *exception* unbox.missing_install_names.ProbablyPythonPathError

Bases: [`ValueError`](https://docs.python.org/3/builtins/exceptions.html#ValueError)

To raise when a module requested is probably not on the python path

### unbox.missing_install_names.dependencies_from_pyproject_content(pyproject_content, , extras=False)

Extract the declared dependencies from `pyproject.toml` text (PEP 621).

By default only the required `[project] dependencies` are yielded:

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

```pycon
>>> content = '''
... [project]
... name = "proj"
... dependencies = ["requests", "numpy>=1.20"]
... [project.optional-dependencies]
... dev = ["pytest>=7.0"]
... docs = ["sphinx"]
... '''
>>> list(dependencies_from_pyproject_content(content))
['requests', 'numpy>=1.20']
```

Pass `extras=True` to also yield every `[project.optional-dependencies]`
group, or an iterable of group names to pick specific ones:

```pycon
>>> list(dependencies_from_pyproject_content(content, extras=True))
['requests', 'numpy>=1.20', 'pytest>=7.0', 'sphinx']
>>> list(dependencies_from_pyproject_content(content, extras=['dev']))
['requests', 'numpy>=1.20', 'pytest>=7.0']
```

Absent or empty sections simply yield nothing (note that `[build-system]
requires` are build-time requirements, not dependencies, so are ignored):

```pycon
>>> list(dependencies_from_pyproject_content(
...     '[build-system]\nrequires = ["hatchling"]'
... ))
[]
```

### unbox.missing_install_names.dependencies_from_setup_configs(setup_configs)

Generate all dependencies from a mapping of setup.cfg files.

* **Parameters:**
  **setup_configs** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path), [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – Mapping of filepath to setup.cfg file contents
* **Yields:**
  Individual dependency strings from all setup.cfg files
* **Return type:**
  [*Iterator*](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[*str*](https://docs.python.org/3/builtins/stdtypes.html#str)]

### Example

```pycon
>>> configs = {
...     'proj1/setup.cfg': '[options]\ninstall_requires =\n    requests\n    numpy>=1.20'
... }
>>> list(dependencies_from_setup_configs(configs))
['requests', 'numpy>=1.20']
```

### unbox.missing_install_names.dependencies_from_setup_configs_content(setup_cfg_content)

Extract dependencies from a single setup.cfg file content.

* **Parameters:**
  **setup_cfg_content** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The text content of a setup.cfg file
* **Yields:**
  Individual dependency strings
* **Return type:**
  [*Iterator*](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[*str*](https://docs.python.org/3/builtins/stdtypes.html#str)]

### unbox.missing_install_names.dependency_diff(install_names, import_names=None, import_to_install_name_map=None, strict=False, install_names_finder=<function find_install_names>, \*, imports_finder=functools.partial(<function imports_for>, post=<function \_third_party_first_level_names>))

Diff declared install names against the install names the imports call for.

See `dependency_diff_for_pkg`, which is the same thing for a package.

* **Parameters:**
  **imports_finder** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)]], [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – How to extract import names from `import_names` when it
  is a module/package/path. Defaults to `imports_for.third_party`; pass
  `imports_for.runtime` to leave out imports made only by the package’s tests.

### unbox.missing_install_names.dependency_diff_for_pkg(pkg, import_to_install_name_map=None, strict=False, install_names_finder=<function find_install_names>, \*, exclude_tests=False)

Get the imported names that are not declared to be installed those names declared
to be installed that are not actually imported.

* **Parameters:**
  * **pkg** – An imported package or path to one.
  * **import_to_install_name_map** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – The mapping between import names and install
    names. This is because import names are not always what you need/want to install.

Options (you won’t have to deal with most of the time):

* **Parameters:**
  * **strict** – Whether you want to allow only those names that are explicitly
    declared in `import_to_install_name_map` or not. (Default is False).
  * **install_names_finder** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)]], [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – A function that takes the package and finds the
    declared install names (by default looks in `pyproject.toml`, then
    `setup.cfg`, but you can make it look for `requirements.txt`, or where-ever).
  * **exclude_tests** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – Whether to ignore the imports made only by the package’s
    own tests (an in-package `tests/`, `test_*.py`, `conftest.py`: see
    `unbox.DFLT_TEST_MODULE_PATTERNS`). Those imports (`pytest`, `hypothesis`,
    …) are needed to *develop* the package, not to *run* it, so counting them
    reports them as missing *install* requirements. Default is `False`, which
    keeps the historical (whole-source-tree) behavior.
* **Returns:**
  The {import_names - install_names} and {install_names - import_names} sets.

The typical use would be when you want to add missing dependencies in your
install instructions. You would then do:

```pycon
>>> import unbox
>>> missing =  dependency_diff_for_pkg(unbox)[0]
>>> print(*sorted(missing), sep='\n')
bs4
requests
```

#### NOTE
These packages were purposely omitted in the install instructions of
`unbox` because they’re only needed in the internal module
`_acquire_builtin_names` that is for development purporses only.

### unbox.missing_install_names.find_install_names(pkg, \*, finders=(<function module_requirements_according_to_pyproject>, <function module_requirements_according_to_setupcfg>))

Find the install names (dependencies) a package declares.

Tries `pyproject.toml` (PEP 621 `[project] dependencies`) first, then
falls back to `setup.cfg` (`[options] install_requires`) for legacy
projects.

* **Parameters:**
  * **pkg** – An imported package, or a path to one.
  * **finders** – The sources to try, in order. Each is called with `pkg`
    and should return `None` when it has nothing to say.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/builtins/exceptions.html#ValueError) – if none of the `finders` found any declared names.
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### unbox.missing_install_names.get_import_names(import_names, imports_finder=functools.partial(<function imports_for>, post=<function \_third_party_first_level_names>))

Get the import names from the given input.

* **Parameters:**
  * **import_names** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType), [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – The input import names, which can be a string, an iterable,
    or a module/package object.
  * **imports_finder** – A function to find imports in the given input.
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  A set of import names.

### unbox.missing_install_names.get_pyproject_path(x)

Flexible search for the `pyproject.toml` path for an object x

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

```pycon
>>> import unbox
>>> get_pyproject_path(unbox).endswith('pyproject.toml')
True
```

### unbox.missing_install_names.get_setupcfg_path(x)

Flexible search for the `setup.cfg` path for an object x

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

```pycon
>>> import unbox
>>> get_setupcfg_path(unbox).endswith('setup.cfg')
True
```

### unbox.missing_install_names.install_names_for_imports(import_names, import_to_install_name_map=None, strict=False, \*, imports_finder=functools.partial(<function imports_for>, post=<function \_third_party_first_level_names>))

Get a set of install names, i.e. names that are used in `pip install PKG_NAME`.

There are a few use cases for this.

First, the install names can be different from the names that are used to import
a package. For example, you `import sklearn` but you `pip install scikit-learn`.

Secondly, you may want to depend on a particular version of a third-party package,
or ensure that the version is greater than a minimum version. So the import names
you extracted need to be mapped to a fuller specification. For example, instead
of just requiring `numpy` you may want to have `numpy >= 1.3` in your
`setup.cfg` or `requirements.txt`.

* **Parameters:**
  * **import_names** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType), [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – An iterable of import names, or a module, package,
    or filepath/folderpath thereof, to be able to extract them
  * **import_to_install_name_map** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – A dict mapping import names (keys) to install
    names
  * **strict** – Whether to assert that all import_names are in the map
  * **imports_finder** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)]], [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – How to extract import names when `import_names` is a
    module/package/path rather than an iterable of names. Defaults to
    `imports_for.third_party` (every module under the root); pass
    `imports_for.runtime` to leave out imports made only by the package’s tests.
* **Return type:**
  [`set`](https://docs.python.org/3/builtins/stdtypes.html#set)
* **Returns:**

### unbox.missing_install_names.install_names_from_pyproject_file(pkg, , extras=False)

Get dependencies from a package’s `pyproject.toml`.

* **Parameters:**
  * **pkg** – A module/package object, or a path to a project folder, a package’s
    `__init__.py`, or a `pyproject.toml` file.
  * **extras** (`Union`[[`bool`](https://docs.python.org/3/builtins/functions.html#bool), [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – Whether to also include `[project.optional-dependencies]`
    (see `dependencies_from_pyproject_content`).
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
* **Returns:**
  The list of dependency strings, or `None` if there is no
  `pyproject.toml` to read – so that callers can fall back to another
  source (see `find_install_names`).

### unbox.missing_install_names.install_names_from_setup_cfg_file(pkg)

Get dependencies from setup.cfg file(s).

* **Parameters:**
  **pkg** – 

  Can be:
  - A module/package object
  - A string path to setup.cfg or directory containing it
  - A Mapping of {filepath: setup.cfg_content} for batch processing
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
* **Returns:**
  List of dependency strings for single files, Iterator for Mappings, None if not found

### Example

```pycon
>>> # For batch processing multiple setup.cfg contents:
>>> configs = {
...     'proj1/setup.cfg': '[options]\ninstall_requires =\n    requests\n    numpy>=1.20'
... }
>>> list(module_requirements_according_to_setupcfg(configs))
['requests', 'numpy>=1.20']
```

### unbox.missing_install_names.install_requires_of_module(pkg)

Get dependencies from setup.cfg file(s).

* **Parameters:**
  **pkg** – 

  Can be:
  - A module/package object
  - A string path to setup.cfg or directory containing it
  - A Mapping of {filepath: setup.cfg_content} for batch processing
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
* **Returns:**
  List of dependency strings for single files, Iterator for Mappings, None if not found

### Example

```pycon
>>> # For batch processing multiple setup.cfg contents:
>>> configs = {
...     'proj1/setup.cfg': '[options]\ninstall_requires =\n    requests\n    numpy>=1.20'
... }
>>> list(module_requirements_according_to_setupcfg(configs))
['requests', 'numpy>=1.20']
```

### unbox.missing_install_names.module_requirements_according_to_pyproject(pkg, , extras=False)

Get dependencies from a package’s `pyproject.toml`.

* **Parameters:**
  * **pkg** – A module/package object, or a path to a project folder, a package’s
    `__init__.py`, or a `pyproject.toml` file.
  * **extras** (`Union`[[`bool`](https://docs.python.org/3/builtins/functions.html#bool), [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – Whether to also include `[project.optional-dependencies]`
    (see `dependencies_from_pyproject_content`).
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
* **Returns:**
  The list of dependency strings, or `None` if there is no
  `pyproject.toml` to read – so that callers can fall back to another
  source (see `find_install_names`).

### unbox.missing_install_names.module_requirements_according_to_setupcfg(pkg)

Get dependencies from setup.cfg file(s).

* **Parameters:**
  **pkg** – 

  Can be:
  - A module/package object
  - A string path to setup.cfg or directory containing it
  - A Mapping of {filepath: setup.cfg_content} for batch processing
* **Return type:**
  [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
* **Returns:**
  List of dependency strings for single files, Iterator for Mappings, None if not found

### Example

```pycon
>>> # For batch processing multiple setup.cfg contents:
>>> configs = {
...     'proj1/setup.cfg': '[options]\ninstall_requires =\n    requests\n    numpy>=1.20'
... }
>>> list(module_requirements_according_to_setupcfg(configs))
['requests', 'numpy>=1.20']
```

### unbox.missing_install_names.print_missing_names(pkg, import_to_install_name_map=None, strict=False, install_names_finder=<function find_install_names>, \*, exclude_tests=False)

See `dependency_diff_for_pkg` for more info (including `exclude_tests`).

```pycon
>>> import unbox
>>> print_missing_names(unbox)
bs4
requests
```
