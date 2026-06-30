"""Convert Nikon sidecar files.

This package is the DarkBridge core. It includes all the core classes and
functions to convert the Nikon sidecar files.

.. toctree::
    :name: darkbridge_toc
    :maxdepth: 1

    core
    version
"""
from darkbridge.version import version

__all__ = [
    "core",
    "__version__"
]

# fix the version of core module to have the same value between the
# package (see pyproject.toml) and the runtime (__version__)
# https://packaging.python.org/en/latest/discussions/versioning/#accessing-version-information-at-runtime
__version__ = version