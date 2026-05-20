"""
This module specifies the metadata of the project to avoid duplicating
theses values across sources files. It’s one of the technique proposed
in the `Single-sourcing the Project Version`_  of the
`Python Packaging User Guide`_.

The easiest way to use is to import the module as below.

>>> from version import __version__
>>> __version__
'0.1.0-dev.0'

>>> from version import *
>>> __license__
'GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007'

.. _Single-sourcing the Project Version: https://packaging.python.org/en
    /latest/discussions/single-source-version/
.. _Python Packaging User Guide: https://packaging.python.org/en/latest/
"""
__release__ = "0.1.0-dev.0"
__project__ = "DarkBridge"
__author__ = "Frederic MEZOU"
__author_email__ = "frederic.mezou@orange.fr"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__copyright__ = f"2026-%Y, {__author__}"
__description__ = "DarkBridge is a lightweight tool that bridges Nikon "\
                  "NX Studio sidecar files and Darktable workflows by "\
                  "converting `.nksc` adjustments into a compatible "\
                  "format."
__version__ = f"{__release__.split(".")[0]}.{__release__.split(".")[1]}"

__all__ = [
    "__project__",
    "__version__",
    "__release__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__description__"
]

