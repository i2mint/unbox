# unbox

Finding imports in code etc.

`get_import_names`: Getting the names that are imported.

`install_names_for_imports`: pip_install name for given import name (if different
and listed in our data)

`find_install_names`: Getting a package’s declared deps, from its
`pyproject.toml` or (legacy) `setup.cfg`

`module_requirements_according_to_pyproject`: Getting deps from pyproject.toml file

`module_requirements_according_to_setupcfg`: Getting deps from setup.cfg file

`print_missing_names`: Print the difference between required names and imported (
install) names

### Modules

| [`base`](unbox.base.html.md#module-unbox.base)                                   | Base functionality of unbox          |
|-----------------------------------------------------------------------------------------------------------|--------------------------------------|
| [`dependencies`](unbox.dependencies.html.md#module-unbox.dependencies)                   | Functions to check for dependencies. |
| [`missing_install_names`](unbox.missing_install_names.html.md#module-unbox.missing_install_names) | Finding missing install names        |
| [`recipes`](unbox.recipes.html.md#module-unbox.recipes)                             | Recipes using unbox                  |
