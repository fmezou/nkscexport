"""Store project metadata.

This module defines the project metadata to avoid duplicating these
values across sources files [pypa1]_.

The exported data are as follows:

.. hlist::
    :columns: 2

    * :data:`name` - the name of the project
    * :data:`version` - the version of the project

The easiest way to use is to import the module as below.

>>> from darkbridge.version import version
>>> version
'0.1.0-dev0'

.. [pypa1] PyPA, `Single-sourcing the Project Version
    <https://packaging.python.org/en/latest/discussions/single-source-
    version/#single-sourcing-the-project-version>`_
"""
__all__ = [
    "name",
    "version"
]

name = "DarkBridge"
"""The name of the project"""
version = "0.1.0.dev0"
"""The version of the project, as defined in the `Version specifier 
specification <https://packaging.python.org/en/latest/specifications/
version-specifiers/#version-specifiers>`_"""


