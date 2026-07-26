###############################################################################
# This file is a part of DarkBridge, to convert Nikon sidecars to Darktable.
# Copyright (C) 2026 DarkBridge developper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
###############################################################################
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


