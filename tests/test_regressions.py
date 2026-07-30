"""Regression tests pinning bugs that were only caught by (fragile) doctests.

Each of the three bugs covered here was interpreter-version-sensitive: two of
them presented differently on py3.10 and py3.12, and one was invisible on the
development machine and only failed in CI. Doctests alone were not enough to
keep them fixed, hence these explicit, environment-independent assertions.
"""

import os

import pytest

from unbox.base import builtin_module_names, imports_for, resolve_rootpath
from unbox.missing_install_names import (
    _dist_name,
    dependencies_from_pyproject_content,
    dependency_diff,
    find_install_names,
    get_pyproject_path,
    get_setupcfg_path,
    module_requirements_according_to_pyproject,
)

# --------------------------------------------------------------------------------------
# Bug 1: resolve_rootpath crashed on every non-package module.
#
# `root.__path__` was read unguarded, so any module without a __path__ (i.e. any
# module that is not a package) raised AttributeError. The fallback meant to
# handle it was unreachable, and did `root = root.__file__` on a None root.


def test_resolve_rootpath_of_plain_module():
    """A non-package module resolves to its (existing) .py file."""
    import dataclasses  # a single-file stdlib module: __file__ but no __path__

    assert not hasattr(dataclasses, '__path__')
    rootpath = resolve_rootpath(dataclasses)
    assert rootpath.endswith('dataclasses.py')
    assert os.path.isfile(rootpath)


def test_resolve_rootpath_of_package():
    """A package resolves to its (existing) directory, not its __init__.py."""
    import unbox

    rootpath = resolve_rootpath(unbox)
    assert os.path.isdir(rootpath)
    assert os.path.isfile(os.path.join(rootpath, '__init__.py'))


def test_resolve_rootpath_of_module_without_file():
    """A module with neither __path__ nor __file__ raises the intended ValueError.

    Before the fix this path was dead code that would itself have raised
    AttributeError.
    """
    import sys  # a builtin module: no __path__, and no __file__ either

    assert not hasattr(sys, '__file__')
    with pytest.raises(ValueError):
        resolve_rootpath(sys)


def test_imports_for_accepts_a_plain_module():
    """The public entry point works on a non-package module (the original symptom)."""
    import dataclasses

    imports = imports_for(dataclasses)
    assert isinstance(imports, set) and imports  # non-empty


# --------------------------------------------------------------------------------------
# Bug 2: declared requirements were diffed against import names WITHOUT stripping
# PEP 508 version specifiers.
#
# So 'dol>=0.3.49' never matched the import-derived 'dol', and every pinned
# dependency of every analysed package was reported both missing AND unused.


@pytest.mark.parametrize(
    'requirement, expected',
    [
        ('dol', 'dol'),
        ('dol>=0.3.49', 'dol'),
        ('pandas>=1.0,<2.0', 'pandas'),
        ('scikit-learn == 1.2.0', 'scikit-learn'),
        ('importlib_resources', 'importlib_resources'),
        ('tomli ; python_version < "3.11"', 'tomli'),
        ('requests[socks]>=2.0', 'requests'),
        ('  numpy  ', 'numpy'),
    ],
)
def test_dist_name_strips_specifiers(requirement, expected):
    assert _dist_name(requirement) == expected


def test_dependency_diff_matches_pinned_requirement():
    """A pinned declared dep must match the bare imported name."""
    missing, unused = dependency_diff(
        install_names=['dol>=0.3.49'], import_names=['dol']
    )
    assert (missing, unused) == (set(), set())


def test_dependency_diff_still_reports_genuinely_missing_names():
    """The fix must not make everything match."""
    missing, unused = dependency_diff(
        install_names=['dol>=0.3.49'], import_names=['dol', 'requests']
    )
    assert missing == {'requests'}
    assert unused == set()


def test_dependency_diff_still_reports_genuinely_unused_names():
    missing, unused = dependency_diff(
        install_names=['dol>=0.3.49', 'numpy>=1.20'], import_names=['dol']
    )
    assert missing == set()
    assert unused == {'numpy'}


# --------------------------------------------------------------------------------------
# Bug 3: `builtins` was classified as a third-party package on py3.10.
#
# builtin_module_names was built only from the packaged standard_lib_names CSVs,
# and 3.10.csv is missing 'builtins'. This failed in CI only.


@pytest.mark.parametrize(
    'name', ['builtins', 'sys', 'os', 'collections', 'itertools', 'json', 're']
)
def test_stdlib_names_are_classified_as_builtin(name):
    """Guards the incomplete-CSV bug on every python version."""
    assert name in builtin_module_names


def test_third_party_filter_excludes_builtins():
    """`imports_for.third_party` must not report stdlib names as third party."""
    import dataclasses

    third_party = imports_for.third_party(dataclasses)
    assert 'builtins' not in third_party
    assert third_party.isdisjoint(builtin_module_names)


# --------------------------------------------------------------------------------------
# The pyproject.toml reader added so this repo could drop setup.cfg at all.


PYPROJECT = """
[build-system]
requires = ["hatchling"]

[project]
name = "someproj"
dependencies = ["dol>=0.3.49", "requests"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
"""

SETUP_CFG = """
[options]
install_requires =
\tdol>=0.3.49
\trequests
"""


def test_find_install_names_reads_pyproject_only_project(tmp_path):
    """A project with ONLY a pyproject.toml must resolve (used to raise ValueError)."""
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT)
    assert list(find_install_names(str(tmp_path))) == ['dol>=0.3.49', 'requests']


def test_find_install_names_still_reads_setup_cfg_only_project(tmp_path):
    """Legacy setup.cfg projects must keep working (back-compat)."""
    (tmp_path / 'setup.cfg').write_text(SETUP_CFG)
    assert list(find_install_names(str(tmp_path))) == ['dol>=0.3.49', 'requests']


def test_find_install_names_prefers_pyproject_over_setup_cfg(tmp_path):
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT)
    (tmp_path / 'setup.cfg').write_text('[options]\ninstall_requires =\n\tnumpy\n')
    assert 'numpy' not in list(find_install_names(str(tmp_path)))


def test_find_install_names_raises_when_nothing_declared(tmp_path):
    with pytest.raises(ValueError):
        find_install_names(str(tmp_path))


def test_optional_dependencies_are_opt_in(tmp_path):
    """Extras must not leak into the required deps by default."""
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT)
    required = module_requirements_according_to_pyproject(str(tmp_path))
    assert 'pytest>=7.0' not in required
    with_extras = module_requirements_according_to_pyproject(
        str(tmp_path), extras=True
    )
    assert 'pytest>=7.0' in with_extras
    assert module_requirements_according_to_pyproject(
        str(tmp_path), extras=['dev']
    ) == with_extras


def test_build_system_requires_are_not_dependencies():
    """`[build-system] requires` are build-time, not install, requirements."""
    assert 'hatchling' not in list(dependencies_from_pyproject_content(PYPROJECT))


def test_pyproject_reader_returns_none_when_absent(tmp_path):
    """None (not an exception) so callers can fall back to setup.cfg."""
    assert module_requirements_according_to_pyproject(str(tmp_path)) is None


def test_project_file_lookup_is_symmetric(tmp_path):
    """Pointing at one project file must still locate the other."""
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT)
    (tmp_path / 'setup.cfg').write_text(SETUP_CFG)
    assert get_pyproject_path(str(tmp_path / 'setup.cfg')) == str(
        tmp_path / 'pyproject.toml'
    )
    assert get_setupcfg_path(str(tmp_path / 'pyproject.toml')) == str(
        tmp_path / 'setup.cfg'
    )


def test_unbox_finds_its_own_declared_dependencies():
    """unbox introspects its own packaging metadata in its doctests -- pin that."""
    import unbox

    declared = list(find_install_names(unbox))
    assert 'dol>=0.3.49' in declared
    assert get_pyproject_path(unbox).endswith('pyproject.toml')
