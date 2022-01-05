"""
Finding missing install names

For doing things like:

>>> from unbox import print_missing_names
>>> import unbox
>>> print_missing_names(unbox)
bs4
requests

Note: These missing dependencies are real, unpurpose, but don't affect you.

You can get the set of missing install names as well as the set of install names
that are not used.

What does this mean?

Install names are those you have declared you needed to install the packages (like
what you put in the ```` section of your ``setup.cfg`` if that's what you use.

Why are the missing or unused? It has to do with imports. If you declared you needed a
package to be installed (a dependency) but never import it, it's unused.
More importantly, if you use (that is import) a package, but haven't listed it in the
names to be installed, that's a problem for your users.

There's several problems to solve here (and you have function here to solve them).

One problem: finding the names that are imported. That's solved by ``import_for`` and
the many subfunctions like ``import_for.third_party``.

Another problem is that the names that are imported are not necessarily the names that
should be installed.
For example, you ``import sklearn`` but you ``pip install scikit-learn``.
That's annoying. So we need a mapping between import names and install names.

So we provide a default mapping (which we will expand as users notify us, or we
encounter more of those aggravating cases.

That said, we provide ways for users to specify their own map.

You can specify an explicit mapping from import name to install name in the form of a
dict or any other valid ``Mapping`` instance. You can also add a
``IMPORT_TO_INSTALL_NAME_MAP_FILE`` environmental variable pointing to a JSON file path
that will be used if this explicit mapping is not given.
If you do none of those, the system will use the default mapping, which is expressed by
the ``unbox/data/dflt_import_to_install_name_map.json`` file in the packaged data.

Besides the import vs install name discrepency, there are other reasons you may want
to specify your own map.
You may want to depend on a particular version of a third-party package,
or ensure that the version is greater than a minimum version. So the import names
you extracted need to be mapped to a fuller specification. For example, instead
of just requiring ``numpy`` you may want to have ``numpy >= 1.3`` in your
``setup.cfg`` or ``requirements.txt``.

"""

# TODO: Better handling of the pkg -> file -> names mesh

import os
from pathlib import Path
from typing import Iterable, Mapping, Optional, Union, Callable
import json
from pathlib import PosixPath
from types import ModuleType

from unbox.base import files, data_files
from unbox import IMPORT_NAMES, imports_for, NAMES, INSTALL_NAMES, ROOT
from config2py import ConfigStore

name_map_envvar = 'IMPORT_TO_INSTALL_NAME_MAP_FILE'

# import to install name: What requirement should be used for a given import name?
DFLT_NAME_MAP_FILE = str(data_files / 'dflt_import_to_install_name_map.json')

import_to_install_name_map_file = os.getenv(name_map_envvar, DFLT_NAME_MAP_FILE)

with open(import_to_install_name_map_file, 'r') as fp:
    dflt_import_to_install_name_map = json.load(fp)


def get_import_names(
    import_names: IMPORT_NAMES, imports_finder=imports_for.third_party
) -> NAMES:
    if isinstance(import_names, str) or not isinstance(import_names, Iterable):
        return imports_finder(import_names)
    else:
        assert isinstance(import_names, Iterable)
        return import_names


def get_import_to_install_name_map(import_to_install_name_map):
    if import_to_install_name_map is None:
        import_to_install_name_map = dflt_import_to_install_name_map
    assert isinstance(
        import_to_install_name_map, Mapping
    ), f'Not a mapping: {import_to_install_name_map}'
    return import_to_install_name_map


def map_if_found(mapping: Mapping, to_map: Iterable, strict=False):
    # return [mapping[x] if x in to_map else x for x in mapping]
    for x in to_map:
        if x in mapping:
            yield mapping[x]
        else:
            if not strict:
                yield x
            else:
                raise AssertionError(f'{x} not in mapping')


def install_names_for_imports(
    import_names: IMPORT_NAMES,
    import_to_install_name_map: Optional[dict] = None,
    strict=False,
) -> set:
    """
    Get a set of install names, i.e. names that are used in ``pip install PKG_NAME``.

    There are a few use cases for this.

    First, the install names can be different from the names that are used to import
    a package. For example, you ``import sklearn`` but you ``pip install scikit-learn``.

    Secondly, you may want to depend on a particular version of a third-party package,
    or ensure that the version is greater than a minimum version. So the import names
    you extracted need to be mapped to a fuller specification. For example, instead
    of just requiring ``numpy`` you may want to have ``numpy >= 1.3`` in your
    ``setup.cfg`` or ``requirements.txt``.

    :param import_names: An iterable of import names, or a module, package,
        or filepath/folderpath thereof, to be able to extract them
    :param import_to_install_name_map: A dict mapping import names (keys) to install
        names
    :param strict: Whether to assert that all import_names are in the map
    :return:
    """
    import_names = get_import_names(import_names)
    import_to_install_name_map = get_import_to_install_name_map(
        import_to_install_name_map
    )
    return set(map_if_found(import_to_install_name_map, import_names, strict))


def pkg_root_dir_name(pkg):
    return Path(pkg.__file__).parent.name


def module_requirements_according_to_setupcfg(pkg) -> Union[NAMES, None]:
    cfg_path = get_setupcfg_path(pkg)

    if os.path.isfile(cfg_path):
        from config2py import ConfigReader
        from collections import ChainMap

        configs = ConfigReader(cfg_path)
        install_requires = configs.get('options', {}).get(
            'install_requires', ''
        ) or ChainMap(  # try getting it in options section
            *configs.values()
        ).get(
            'install_requires', ''
        )
        return [x.strip() for x in install_requires.split()]

    return None


class ProbablyPythonPathError(ValueError):
    """To raise when a module requested is probably not on the python path"""


def get_setupcfg_path(x) -> str:
    """Flexible search for the setupcfg path for an object x"""
    if isinstance(x, ModuleType):
        if x.__file__ is None:
            raise ProbablyPythonPathError(
                f"Sorry, but this module type ({x}) didn't have a __file__: "
                "This often happens when you're pointing to a namespace module or "
                "builtin. If it's not a builtin, it's probably that you don't have the "
                'package on your python path.'
            )
        return str(PosixPath(x.__file__).parent.parent / 'setup.cfg')
    elif isinstance(x, str):
        path = PosixPath(x)
        if path.is_dir():
            if (path / 'setup.cfg').is_file():  # proj/setup.cfg
                return str(path / 'setup.cfg')
            elif (path.parent / 'setup.cfg').is_file():  # proj/proj
                return str(path.parent / 'setup.cfg')
        elif path.name.endswith('__init__.py'):
            return str(path.parent.parent / 'setup.cfg')
        else:
            assert path.name.endswith('setup.cfg')
            return str(path)


def get_module_obj(module) -> ModuleType:
    if isinstance(module, str):
        module = __import__(module)
    if not isinstance(module, ModuleType):
        import inspect

        module = inspect.getmodule(module)
    return module


# Simple version
# def module_requirements_according_to_setupcfg(module):
#     """Get the list of required packages for the module, taken from setup.cfg file"""
#     module = get_module_obj(module)
#     s = ConfigStore(module_to_setup_cfg_filepath(module))
#     return list(filter(None, s['options']['install_requires'].split('\n')))


install_requires_of_module = (
    module_requirements_according_to_setupcfg  # backcompa alias
)

install_names_from_setup_cfg_file = install_requires_of_module  # backcompa alias


def find_install_names(pkg) -> NAMES:
    install_names = install_names_from_setup_cfg_file(pkg)
    if install_names is not None:
        return install_names
    else:
        raise ValueError(f"Can't find install names for {pkg=}")


def get_install_names(
    install_names: INSTALL_NAMES,
    install_names_finder: Callable[[ROOT], NAMES] = find_install_names,
) -> NAMES:
    if isinstance(install_names, str) or not isinstance(install_names, Iterable):
        return install_names_finder(install_names)
    else:
        assert isinstance(install_names, Iterable)
        return install_names


def dependency_diff(
    install_names: INSTALL_NAMES,
    import_names: IMPORT_NAMES = None,
    import_to_install_name_map: Optional[dict] = None,
    strict=False,
    install_names_finder: Callable[[ROOT], NAMES] = find_install_names,
):
    install_names = set(get_install_names(install_names, install_names_finder))
    install_names_needed_for_imports = set(
        install_names_for_imports(import_names, import_to_install_name_map, strict)
    )
    missing_install_names = install_names_needed_for_imports - install_names
    unused_install_names = install_names - install_names_needed_for_imports
    return missing_install_names, unused_install_names


def dependency_diff_for_pkg(
    pkg,
    import_to_install_name_map: Optional[dict] = None,
    strict=False,
    install_names_finder: Callable[[ROOT], NAMES] = find_install_names,
):
    r"""
    Get the imported names that are not declared to be installed those names declared 
    to be installed that are not actually imported. 

    :param pkg: An imported package or path to one.
    :param import_to_install_name_map: The mapping between import names and install 
    names. This is because import names are not always what you need/want to install.

    Options (you won't have to deal with most of the time):

    :param strict: Whether you want to allow only those names that are explicitly 
    declared in ``import_to_install_name_map`` or not. (Default is False).
    :param install_names_finder: A function that takes the package and finds the 
    declared install names (By default only looks in ``setup.cfg``, but you can make 
    it look for ``requirements.txt``, or where-ever.
    :return: The {import_names - install_names} and {install_names - import_names} sets.

    The typical use would be when you want to add missing dependencies in your 
    install instructions. You would then do:

    >>> import unbox
    >>> missing =  dependency_diff_for_pkg(unbox)[0]
    >>> print(*sorted(missing), sep='\n')
    bs4
    requests

    Note: These packages were purposely omitted in the install instructions of 
    ``unbox`` because they're only needed in the internal module 
    ``_acquire_builtin_names`` that is for development purporses only.

    """
    missing_install_names, unused_install_names = dependency_diff(
        install_names=pkg,
        import_names=pkg,
        import_to_install_name_map=import_to_install_name_map,
        strict=strict,
        install_names_finder=install_names_finder,
    )
    missing_install_names = missing_install_names - {pkg_root_dir_name((pkg))}
    return missing_install_names, unused_install_names


def print_missing_names(
    pkg,
    import_to_install_name_map: Optional[dict] = None,
    strict=False,
    install_names_finder: Callable[[ROOT], NAMES] = find_install_names,
):
    """
    See ``dependency_diff_for_pkg`` for more info.

    >>> import unbox
    >>> print_missing_names(unbox)
    bs4
    requests

    """
    missing_install_names, unused_install_names = dependency_diff_for_pkg(
        pkg=pkg,
        import_to_install_name_map=import_to_install_name_map,
        strict=strict,
        install_names_finder=install_names_finder,
    )
    print(*sorted(missing_install_names), sep='\n')
