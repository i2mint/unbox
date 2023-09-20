"""Functions to check for dependencies."""

import re


def pypi_package_data(package_name):
    from urllib.request import urlopen
    from urllib.error import HTTPError
    import json

    url = f'https://pypi.org/pypi/{package_name}/json'

    try:
        with urlopen(url) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except HTTPError as e:
        raise ValueError(
            f"Failed to fetch package info for '{package_name}' from PyPI: {e}"
        )


def pypi_requires_dist(package_name: str,) -> dict:
    """
    Fetch dependencies for a package from PyPI.

    Parameters:
        package_name (str): Name of the package to fetch dependencies for.

    Returns:
        dict: Dictionary containing package dependencies.
    """
    package_data = pypi_package_data(package_name)
    return package_data['info'].get('requires_dist', ()) or ()


def dependencies_from_pypi(
    package_name,
    *,
    requirement_filter=lambda x: 'extra == ' not in x,
    requirement_trans=lambda x: re.match('[\w-]+', x).group(0),
    egress=list,
):
    """Simply get a list of dependencies for a package from PyPI.

    >>> dependencies_from_pypi('pandas')  # doctest: +SKIP
    ['numpy', 'numpy', 'python-dateutil', 'pytz', 'tzdata']

    But you have control over the requirements that are returned, 
    and how they are returned:

    >>> it = dependencies_from_pypi(
    ...     'pandas',
    ...     requirement_filter=lambda x: True,  # don't filter any requirements
    ...     requirement_trans=lambda x: x,  # as is
    ...     egress = lambda x: x  # just get the iterator as is
    ... )
    >>> next(it)  # doctest: +SKIP
    'numpy>=1.22.4; python_version < "3.11"'
    >>> list(it)[-1]  # doctest: +SKIP
    'zstandard>=0.17.0; extra == "all"'

    """
    return egress(
        map(
            requirement_trans,
            filter(requirement_filter, pypi_requires_dist(package_name)),
        )
    )
