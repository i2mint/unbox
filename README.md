# unbox
Finding imports in code

To install:	```pip install unbox```

# What's here

Lots of little goodies to help you analyze the imports of your, or others' code. 

## Getting a list of missing dependencies

```python
>>> from unbox import print_missing_names
>>> import some_module  # doctest: +SKIP
>>> print_missing_names(some_module)  # doctest: +SKIP
SoundFile
i2
librosa
pyttsx3
slink
```

## Seeing what the dependencies of a package are, before installing it

Simply get a list of dependencies for a package from PyPI.

```python
>>> import unbox
>>> unbox.dependencies_from_pypi('pandas')
['numpy', 'numpy', 'python-dateutil', 'pytz', 'tzdata']
```

But you have control over the requirements that are returned, 
and how they are returned:

```python
>>> it = unbox.dependencies_from_pypi(
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


## A dict-like interface

The base of `unbox` is just the `dol` interface to `findimports`, which then allows us to offer a bunch of functionalities easily. 

Say you wanted to know what dol was made of. 
The dol way of doing this is to make a `Mapping` (i.e. a key-value dict-like interface), 
and then do what you do with dicts...

```python
>>> import dol
>>> import unbox
>>> s = unbox.ModuleNamesImportedByModule(dol)  # make a store containing the modules of the `dol` package
>>> # Now wee how you can do things you do with dicts
>>> len(s)
15
>>> list(s)
['dol.__init__',
 'dol.appendable',
 'dol.base',
 'dol.caching',
 'dol.core',
 'dol.dig',
 'dol.errors',
 'dol.filesys',
 'dol.mixins',
 'dol.naming',
 'dol.paths',
 'dol.signatures',
 'dol.sources',
 'dol.trans',
 'dol.util']
>>> 'dol.appendable' in s
>>> # The values of `s` are sets of modules imported by a module.
>>> s['dol.appendable']  # what does dol.appendable import?
{'collections.abc', 'dol.trans', 'time', 'types', 'typing'}
```

Check out `ModulesImportedByModule` also, which gives you a `Mapping` with module objects 
as keys, and `findimports.ImportInfo` instances as values.

## imports_for

As an example of what you can do with this set up, have a look at `imports_for`. 
Or don't have a look; just use it, since it's quite useful.

```python
from unbox import imports_for 
import wave
assert imports_for(wave) == {'warnings', 'builtins', 'sys', 'audioop', 'chunk', 'struct', 'collections'}
```

At it's base, imports_for gives you a generator of import names. 
With the `post` argument (defaulted to `set`) you can specify a callable that can produce the output 
you want; whether you want to filter the items, count them, order them, etc.

We curried a few common ones for you, for your convenience:

```python
from unbox import imports_for
imports_for.counter  # imported names and their counts
imports_for.most_common  # imported names and their counts, ordered by most common
imports_for.first_level  # set for imported first level names (e.g. 'os' instead of 'os.path.etc.)
imports_for.first_level_count  # count of imported first level names (e.g. 'os' instead of 'os.path.etc.)
imports_for.third_party  # imported (first level) names that are not builtin names (most probably third party packages)"
```

## Collections of python names

Check out the contents of these collections:

```python
from unbox import (
    builtin_module_names,
    scanned_standard_lib_names,
    all_accessible_modules,
    all_accessible_pkg_names,
    all_accessible_non_pkg_module_names,
    builtin_obj_names,
    python_names
)
```

For example, `builtin_module_names` will be a set of names that are 
[documented](`https://docs.python.org/3.8/library/`) **and** importable on your system.

The `scanned_standard_lib_names` set is similar, but the names are obtained by scanning 
the local standard library file names -- so include things like easter eggs (`this`, `antigravity`).

`all_accessible_modules` will be the list of all modules accessible in your python path.

And so on...

