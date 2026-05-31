"""Convert Nikon sidecar files.

TThis package is the DarkBridge core. It includes all the core classes and
functions to convert the Nikon sidecar files.

The exported modules are as follows:

.. hlist::
    :columns: 2

    * :mod:`core` - Convert Nikon sidecar files
    * :mod:`version` - Store project metadata
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