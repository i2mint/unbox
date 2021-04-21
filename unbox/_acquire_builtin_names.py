"""
Utils to download and parse python library list pages, to collect standard lib names.
For internal use -- not meant to actually be used by you (but you can anyway if you want).
"""
from contextlib import suppress

with suppress(ModuleNotFoundError):
    import requests
    from bs4 import BeautifulSoup
    from dol.filesys import RelPathFileStringPersister
    from unbox.base import python_versions, is_importable, standard_lib_names_data_dir

    python_standard_lib_url_template = "https://docs.python.org/{version}/library/"


    def html_of_python_standard_lib_page(version: str = '3.9', validate_version: bool = True):
        version = str(version)
        if validate_version and version not in python_versions:
            raise ValueError(f"Not a version that is validated by this code: {version}")
        return requests.get(python_standard_lib_url_template.format(version=version)).content


    def names_from_html_of_library_page(html: str):
        b = BeautifulSoup(html)
        for item in b.find_all(name='li', attrs={'class': 'toctree-l2'}):
            t = item.find(name='span')
            if t is not None:
                name = t.text
                if name:
                    yield name.split('.')[0]  # [0] because only want root module (e.g. not xml.sax.handler: just xml)


    def documented_names_for_python_version(version: str = '3.9', validate_version: bool = True):
        html = html_of_python_standard_lib_page(version, validate_version)
        yield from names_from_html_of_library_page(html)


    def acquire_and_save_standard_lib_names(python_versions=python_versions):

        s = RelPathFileStringPersister(standard_lib_names_data_dir)

        for version in python_versions:
            names = documented_names_for_python_version(version)
            s[version + '.csv'] = "\n".join(sorted(set(names)))
