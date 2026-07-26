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
"""Convert Nikon sidecar files.

This package is the DarkBridge core. It includes all the core classes and
functions to convert the Nikon sidecar files.

.. toctree::
    :name: darkbridge_toc
    :maxdepth: 1

    __main__
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