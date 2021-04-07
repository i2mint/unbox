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
