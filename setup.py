import setuptools

from hub_importer_plugin import __version__

setuptools.setup(
    version=__version__,
    entry_points={
        "galaxy_importer.post_load_plugin": [
            "hub_importer_plugin = hub_importer_plugin.plugin:process"]}
)
