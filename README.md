# unbox
Finding imports in code

To install:	```pip install unbox```

# What's here

Lots of little goodies to help you analyze the imports of your, or others' code. 

## A dict-like interface

The base of `unbox` is just the `py2store` interface to `findimports`, which then allows us to 
offer a bunch of functionalities easily. 

Say you wanted to know what py2store was made of. 
The py2store way of doing this is to make a `Mapping` (i.e. a key-value dict-like interface), 
and then do what you do with dicts...

```python
>>> import py2store
>>> len(s)
['py2store.__init__',
 'py2store.access',
 'py2store.appendable',
 'py2store.base',
 'py2store.caching',
 'py2store.core',
 'py2store.dig',
 'py2store.errors',
 'py2store.examples.__init__',
 'py2store.examples.kv_walking',
 'py2store.examples.last_key_inserted',
 'py2store.examples.python_code_stats',
 'py2store.examples.write_caches',
  ...
 'py2store.filesys',
 'py2store.key_mappers.__init__',
 'py2store.key_mappers.naming',
 'py2store.key_mappers.paths',
 'py2store.key_mappers.str_utils',
 'py2store.key_mappers.tuples',
 'py2store.misc',
 'py2store.mixins',
 'py2store.my.__init__',
 'py2store.my.grabbers',
 'py2store.utils.sliceable',
 'py2store.utils.timeseries_caching',
 'py2store.utils.uri_utils']
 
>>> 'py2store.appendable' in s
>>> s['py2store.appendable']
{'collections.abc', 'py2store.trans', 'time', 'types', 'typing'}
```

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


