# unbox.recipes

Recipes using unbox

### Functions

| `get_py_files`(files)                                                                        |                                                                                                           |
|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| [`imports_of_package`](#unbox.recipes.imports_of_package)(package[, ...])          | Generates (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.                   |
| [`key_and_matched_lines`](#unbox.recipes.key_and_matched_lines)(files, pattern)       | Generates (k, line) pairs for every line of every k that has a pattern match                              |
| [`key_and_pattern_counts`](#unbox.recipes.key_and_pattern_counts)(files, pattern)      | Generates (k, pattern_counts) pairs from scanning a store of .py files it scans, counting pattern matches |
| [`print_imports_of_package`](#unbox.recipes.print_imports_of_package)(package[, ...])    | Prints (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.                      |
| [`print_key_and_matched_lines`](#unbox.recipes.print_key_and_matched_lines)(files, pattern) | Print (k, line) pairs for every line of every k that has a pattern match                                  |
| `print_py_files_containing_pattern`(files, pattern)                                          |                                                                                                           |
| [`signature_less_builtin_obj_names`](#unbox.recipes.signature_less_builtin_obj_names)([caller])  | Generator of builtin names that don't have a signature                                                    |

### Classes

| [`ModuleStrings`](#unbox.recipes.ModuleStrings)(rootdir[, subpath, ...])   | Keys are module dotpaths and values are modules   |
|-------------------------------------------------------------------------------------------|---------------------------------------------------|

### *class* unbox.recipes.ModuleStrings(rootdir, subpath='', pattern_for_field=None, max_levels=None, , include_hidden=False, assert_rootdir_existence=False)

Bases: `Store`

Keys are module dotpaths and values are modules

#### is_valid_key(k, \*args, \_\_name='is_valid_key', \*\*kwargs)

`is_valid_key` on the inner key – see `mk_relative_path_store`.

#### validate_key(k, \*args, \_\_name='validate_key', \*\*kwargs)

`validate_key` on the inner key – see `mk_relative_path_store`.

### unbox.recipes.imports_of_package(package, module_dotpath_filt=None, imported_module_dotpath_filt=None, depth=None)

Generates (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.

* **Parameters:**
  * **package** – Module, file, folder, or dotpath of package to root the generation from
  * **module_dotpath_filt** – Filter function for module dotpaths
  * **imported_module_dotpath_filt** – Filter function for imported module dotpaths
  * **depth** – How deep the recursion should be
* **Returns:**
  A generator of (module_dotpath, imported_module_dotpaths) pairs

```pycon
>>> import unbox
>>> for module_dotpath, imported_module_dotpaths in imports_of_package(
...                          unbox,
...                          module_dotpath_filt = lambda x: '__init__' not in x,
...                          depth=1):
...     print(f"{module_dotpath}: {sorted(imported_module_dotpaths)[:3]}"
... )
_acquire_builtin_names: ['bs4', 'contextlib', 'dol.filesys']
missing_install_names: ['collections', 'config2py', 'json']
recipes: ['dol', 'dol.filesys', 'importlib']
base: ['builtins', 'collections', 'contextlib']
```

### unbox.recipes.key_and_matched_lines(files, pattern)

Generates (k, line) pairs for every line of every k that has a pattern match

* **Parameters:**
  * **files** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)]) – A source of py files (e.g. module, root directory, or a Mapping itself)
  * **pattern** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)) – A string or re.Pattern to match and count
* **Returns:**
  A generator of (k, pattern_counts) pairs

#### SEE ALSO
key_and_pattern_counts

### unbox.recipes.key_and_pattern_counts(files, pattern)

Generates (k, pattern_counts) pairs from scanning a store of .py files it scans, counting pattern matches

* **Parameters:**
  * **files** (`Union`[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping), [`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)]) – A source of py files (e.g. module, root directory, or a Mapping itself)
  * **pattern** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)) – A string or re.Pattern to match and count
* **Returns:**
  A generator of (k, pattern_counts) pairs

In order to be able to replicate this test we’ll mention a word that has little chance of showing up in an
uncontrolled matter in this this unbox package. This word: supercalifragilisticexpialidocious
It should appear only twice in this current recipes.py – once above, and once when we ask for
key_and_pattern_counts to match it.

Now, let’s see:

```pycon
>>> import unbox
>>> sorted(key_and_pattern_counts(unbox, 'supercalifragilisticexpialidocious'))
[('__init__.py', 0), ('_acquire_builtin_names.py', 0), ('base.py', 0),
('dependencies.py', 0), ('missing_install_names.py', 0), ('recipes.py', 2)]
```

### unbox.recipes.print_imports_of_package(package, module_dotpath_filt=None, imported_module_dotpath_filt=None, depth=None)

Prints (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.

* **Parameters:**
  * **package** – Module, file, folder, or dotpath of package to root the generation from
  * **module_dotpath_filt** – Filter function for module dotpaths
  * **imported_module_dotpath_filt** – Filter function for imported module dotpaths
  * **depth** – How deep the recursion should be
* **Returns:**
  prints the (module_dotpath, imported_module_dotpaths) pairs

### unbox.recipes.print_key_and_matched_lines(files, pattern)

Print (k, line) pairs for every line of every k that has a pattern match

### unbox.recipes.signature_less_builtin_obj_names(caller='signature')

Generator of builtin names that don’t have a signature
