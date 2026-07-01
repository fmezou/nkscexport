"""Store project metadata.

This module defines the project metadata to avoid duplicating these
values across sources files [pypa1]_. The project metadata are the
project name (:data:`name`) and the version identifier (:data:`version`).

Using ``version``
-----------------

For this short tutorial, we simply import the data.

>>> from darkbridge.version import version
>>> version
'0.1.0'

Reference
---------

.. autodata:: name

.. autodata:: version


.. [pypa1] PyPA, `Single-sourcing the Project Version
    <https://packaging.python.org/en/latest/discussions/single-source-
    version/#single-sourcing-the-project-version>`_
"""
__all__ = [
    "name",
    "version"
]

#: The name of the project
name: str = "DarkBridge"

#: The version identifier of the project, as defined in the `Version
#: specifier specification <https://packaging.python.org/en/latest/
#: specifications/version-specifiers/#version-specifiers>`_
version: str = "0.1.0a1"


