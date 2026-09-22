# unbox.base

Base functionality of unbox

### Module Attributes

| [`ModuleNameFilter`](#unbox.base.ModuleNameFilter)   | an fnmatch pattern for a dotted-name segment, or a predicate on the full dotted module name.   |
|---------------------------------------------------------------------|------------------------------------------------------------------------------------------------|

### Functions

| [`documented_builtin_module_names`](#unbox.base.documented_builtin_module_names)()          | Will yield from a prepopulated list of builtin module (and submodule) names for the environment's python version.   |
|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| [`imports_for`](#unbox.base.imports_for)(root[, post, exclude])         | Get imported strings.                                                                                               |
| `is_importable`(name)                                                                       |                                                                                                                     |
| `modname_to_modobj`(self, modname)                                                          |                                                                                                                     |
| `modobj_to_modname`(self, modobj)                                                           |                                                                                                                     |
| [`resolve_rootpath`](#unbox.base.resolve_rootpath)(obj)                      | Resolve `obj` to an existing filesystem path.                                                                       |
| [`scan_locally_for_standard_lib_names`](#unbox.base.scan_locally_for_standard_lib_names)([...]) | Generates names of standard libs from python environment it was called from.                                        |

### Classes

| [`ModuleImports`](#unbox.base.ModuleImports)                                |                                                |
|-----------------------------------------------------------------------------------------------|------------------------------------------------|
| [`ModuleNamesImportedByModule`](#unbox.base.ModuleNamesImportedByModule)(root[, ...])     | Store of module names imported by some module. |
| [`ModulesColl`](#unbox.base.ModulesColl)(root[, trackUnusedNames, ...])   |                                                |
| [`ModulesImportedByModule`](#unbox.base.ModulesImportedByModule)(root[, ...])         |                                                |
| [`MyModuleGraph`](#unbox.base.MyModuleGraph)(root[, trackUnusedNames, ...]) |                                                |

### unbox.base.ModuleImports

alias of [`ModuleNamesImportedByModule`](#unbox.base.ModuleNamesImportedByModule)

### unbox.base.ModuleNameFilter

an fnmatch pattern for a dotted-name segment, or a
predicate on the full dotted module name.

* **Type:**
  An `exclude` element

alias of [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]

### *class* unbox.base.ModuleNamesImportedByModule(root, trackUnusedNames=False, all_unused=False, external_dependencies=True, warn_about_duplicates=False, verbose=False, ignore_parse_path_warnings=False)

Bases: `Store`

Store of module names imported by some module.

### *class* unbox.base.ModulesColl(root, trackUnusedNames=False, all_unused=False, external_dependencies=True, warn_about_duplicates=False, verbose=False, ignore_parse_path_warnings=False)

Bases: `Collection`

### *class* unbox.base.ModulesImportedByModule(root, trackUnusedNames=False, all_unused=False, external_dependencies=True, warn_about_duplicates=False, verbose=False, ignore_parse_path_warnings=False)

Bases: `KvReader`, [`ModulesColl`](#unbox.base.ModulesColl)

### *class* unbox.base.MyModuleGraph(root, trackUnusedNames=False, all_unused=False, external_dependencies=True, warn_about_duplicates=False, verbose=False, ignore_parse_path_warnings=False)

Bases: `ModuleGraph`

### unbox.base.documented_builtin_module_names()

Will yield from a prepopulated list of builtin module (and submodule) names for the environment’s python version.

These were parsed from `https://docs.python.org/{version}/library/` and saved in package’s data
(this data, for all supported versions, can be found here
too: [https://github.com/i2mint/unbox/tree/master/unbox/data/standard_lib_names](https://github.com/i2mint/unbox/tree/master/unbox/data/standard_lib_names))

Supported python versions: ‘2.7’, ‘3.5’, ‘3.6’, ‘3.7’, ‘3.8’, and ‘3.9’

I python version not supported, will return an empty set (with a warning).

#### SEE ALSO
scan_locally_for_standard_lib_names

### unbox.base.imports_for(root, post=<class 'set'>, \*, exclude=())

Get imported strings.

* **Parameters:**
  * **root** – Module, package, or filepath/folderpath thereof.
  * **post** – Postprocess iterable. For example:
    `set`, when order and repetition doesn’t matter
    `collections.Counter`, to count number of modules where the module is imported,
    `lambda module: set(x.split('.')[0] for x in module)` if you only care about the top level package
  * **exclude** ([`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]]]) – Modules to leave out of the scan, as fnmatch patterns matched
    against each segment of the dotted module name (e.g. `'tests'`,
    `'test_*'`) and/or predicates on the full dotted name. Empty (the
    default) means “scan everything”, which is what `unbox` has always done.
    See `DFLT_TEST_MODULE_PATTERNS` and the `imports_for.runtime` preset.
* **Returns:**

```pycon
>>> import wave
>>> imports = imports_for(wave)
>>> sorted({'collections', 'struct', 'sys'} & imports)
['collections', 'struct', 'sys']
```

#### NOTE
only a version-stable subset of `wave`’s imports is asserted here –
py3.10’s `wave` imports `audioop` and `chunk` (both removed in 3.13),
while py3.12’s imports `uuid` instead.

An in-package `tests/` imports things (`pytest`, `hypothesis`, …) that
the package doesn’t need at runtime; `imports_for.runtime` is the preset that
scopes them out (see `DFLT_TEST_MODULE_PATTERNS`).

### unbox.base.resolve_rootpath(obj)

Resolve `obj` to an existing filesystem path.

`obj` can be a module object, a module name, or a path (in which case it is
returned as-is). A *package* resolves to its directory, while a plain
(non-package) module resolves to its `.py` file.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

```pycon
>>> import wave  # a plain module: has __file__ but no __path__
>>> resolve_rootpath(wave).endswith('wave.py')
True
>>> import unbox  # a package: has a __path__
>>> resolve_rootpath(unbox).endswith('unbox')
True
```

### unbox.base.scan_locally_for_standard_lib_names(include_underscored=True)

Generates names of standard libs from python environment it was called from.

* **Parameters:**
  **include_underscored** – Whether to include names that start with underscore or not.
  :keyword standard lib, builtins

#### SEE ALSO
documented_builtin_module_names

```pycon
>>> standard_lib_names = set(scan_locally_for_standard_lib_names(include_underscored=True))
>>> # verify that a few known libs are there (including three folders and three py files)
>>> assert {'collections', 'asyncio', 'os', 'dis', '__future__'}.issubset(standard_lib_names)
>>> # verify that other unwanted "decoys" are NOT in there
>>> assert {'__pycache__', 'LICENSE.txt', 'config-3.8-darwin', '.DS_Store'}.isdisjoint(standard_lib_names)
```
