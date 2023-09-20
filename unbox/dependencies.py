"""Functions to check for dependencies."""


def pypi_package_data(package_name):
    from urllib.request import urlopen
    from urllib.error import HTTPError
    import json

    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        with urlopen(url) as response:
            data = response.read()
            return json.loads(data.decode("utf-8"))
    except HTTPError as e:
        raise ValueError(
            f"Failed to fetch package info for '{package_name}' from PyPI: {e}"
        )


def pypi_requires_dist(
    package_name: str,
) -> dict:
    """
    Fetch dependencies for a package from PyPI.

    Parameters:
        package_name (str): Name of the package to fetch dependencies for.

    Returns:
        dict: Dictionary containing package dependencies.
    """
    package_data = pypi_package_data(package_name)
    return package_data["info"].get("requires_dist", ()) or ()


def dependencies_from_pypi(
    package_name,
    *,
    requirement_filter=lambda x: "extra == " not in x,
    requirement_trans=lambda x: re.match("[\w-]+", x).group(0),
    egress=list,
):
    return egress(
        map(
            requirement_trans,
            filter(requirement_filter, pypi_requires_dist(package_name)),
        )
    )
