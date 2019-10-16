import setuptools

from hub_importer_plugin import __version__

requirements = [
    "cryptography",
    "jinja2",
    "pycodestyle",
    "pylint",
    "pyyaml",
    "rstcheck",
    "virtualenv",
    "voluptuous",
    "yamllint",
]

setuptools.setup(
    version=__version__,
    entry_points={
        "galaxy_importer.post_load_plugin": [
            "hub_importer_plugin = hub_importer_plugin.plugin:process"]},
    install_requires=requirements,
)
