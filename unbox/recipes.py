import os
import importlib
from py2store import LocalTextStore, filt_iter, wrap_kvs, cached_keys


# TODO: Replace wasteful LocalTextStore base with file collection base and key->importlib.import_module(key) def of values
@wrap_kvs(
    key_of_id=lambda k: k.replace('.py', '').replace(os.path.sep, '.'),
    id_of_key=lambda k: k.replace('.', os.path.sep) + '.py',
    postget=lambda k, v: importlib.import_module(k)
)
class ModuleStrings(LocalTextStore):
    """Keys are module dotpaths and values are modules"""


import unbox
from types import ModuleType


def imports_of_package(
        package,
        module_dotpath_filt=None,
        imported_module_dotpath_filt=None,
        depth=None):
    """Generates (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.

    :param package: Module, file, folder, or dotpath of package to root the generation from
    :param module_dotpath_filt: Filter function for module dotpaths
    :param imported_module_dotpath_filt: Filter function for imported module dotpaths
    :param depth: How deep the recursion should be
    :return: A generator of (module_dotpath, imported_module_dotpaths) pairs

    >>> import unbox
    >>> for module_dotpath, imported_module_dotpaths in imports_of_package(
    ...                          unbox,
    ...                          module_dotpath_filt = lambda x: '__init__' not in x,
    ...                          depth=1):
    ...     print(f"{module_dotpath}: {imported_module_dotpaths[:3]}")
    unbox.recipes: ['importlib', 'os', 'py2store']
    unbox.base: ['builtins', 'collections', 'findimports']

    """
    if isinstance(package, str):
        if os.path.exists(package):
            rootdir = package
        else:
            package = importlib.import_module(package)
            rootdir = os.path.dirname(package.__file__)
    elif isinstance(package, ModuleType):
        rootdir = os.path.dirname(package.__file__)
    else:
        raise TypeError(f"Couldn't resolve {package}")

    s = ModuleStrings(rootdir + '{}.py', depth)
    for module_dotpath, imported_module_dotpaths in s.items():
        if (module_dotpath_filt or (lambda x: True))(module_dotpath):
            imported_module_dotpaths = sorted(
                filter(
                    imported_module_dotpath_filt,
                    set(
                        unbox.imports_for(imported_module_dotpaths))))
            yield module_dotpath, imported_module_dotpaths


def print_imports_of_package(
        package,
        module_dotpath_filt=None,
        imported_module_dotpath_filt=None,
        depth=None):
    """Prints (module_dotpath, imported_module_dotpaths) pairs from a package, recursively.

    :param package: Module, file, folder, or dotpath of package to root the generation from
    :param module_dotpath_filt: Filter function for module dotpaths
    :param imported_module_dotpath_filt: Filter function for imported module dotpaths
    :param depth: How deep the recursion should be
    :return: prints the (module_dotpath, imported_module_dotpaths) pairs
    """
    for module_dotpath, imported_module_dotpaths in imports_of_package(
            package, module_dotpath_filt, imported_module_dotpath_filt, depth):
        t = '\n\t'.join(imported_module_dotpaths)
        print(f"{module_dotpath}:\n\t{t}")


########################################################################################################################
import re
from typing import Mapping, Union
from types import ModuleType
from py2store import LocalTextStore

Files = Union[str, Mapping, ModuleType]
path_sep = os.path.sep


def get_py_files(files: Files):
    if isinstance(files, ModuleType):
        files = os.path.dirname(files.__file__)
    if isinstance(files, str) and os.path.isdir(files):
        if files.endswith(path_sep):
            files = files[:-1]
        files = LocalTextStore(files + path_sep + '{}.py')
    assert isinstance(files, Mapping)
    return files


def key_and_pattern_counts(files: Files, pattern: Union[str, re.Pattern]):
    """Generates (k, pattern_counts) pairs from scanning a store of .py files it scans, counting pattern matches

    :param files: A source of py files (e.g. module, root directory, or a Mapping itself)
    :param pattern: A string or re.Pattern to match and count
    :return: A generator of (k, pattern_counts) pairs

    In order to be able to replicate this test we'll mention a word that has little chance of showing up in an
    uncontrolled matter in this this unbox package. This word: supercalifragilisticexpialidocious
    It should appear only twice in this current recipes.py -- once above, and once when we ask for
    key_and_pattern_counts to match it.

    Now, let's see:

    >>> import unbox
    >>> sorted(key_and_pattern_counts(unbox, 'supercalifragilisticexpialidocious'))
    [('__init__.py', 0), ('base.py', 0), ('recipes.py', 2)]

    """
    files = get_py_files(files)
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    for k, contents in files.items():
        pattern_count = len(pattern.findall(contents))
        yield k, pattern_count


def print_py_files_containing_pattern(files: Files, pattern: Union[str, re.Pattern]):
    for key, pattern_count in key_and_pattern_counts(files, pattern):
        if pattern_count > 0:
            print(f"{key}: {pattern_count}")
