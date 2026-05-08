"""
Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files compliant
with Darktable.
This script may be use as a module by a third party offering a new GUI for
example, or as a script with the command line interface::

    python -m nkscexport

Synopsis
--------

``nkscexport.py [-h] [-r] [-f] [-n] FILE``

Command line options
^^^^^^^^^^^^^^^^^^^^

.. program:: nkscexport

.. option:: -h, --help

    show this help message and exit

.. option:: -r, --recursive

    make a recursive search of images files in subfolders.

.. option:: -f, --force

    overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    run in preview mode without any sidecar writing.

.. option:: -v, --version

    show program's version number and exit


Exit code
^^^^^^^^^

==  ============================================================================
0   no error
1   an error occurred (error messages are print on stderr stream console
    and write in a log file).
2   invalid argument. An argument of the command line isn't valid (see Usage).
==  ============================================================================


Public function
---------------
This module has only one public function.

===================================  ===================================
`nkscexport`                          ..
===================================  ===================================

.. _user manual: http://fmezou.github.io/nkscexport/
"""
import argparse
import sys
import os
import glob
from pathlib import Path
from xml.etree import ElementTree as ET
import datetime
import locale

import colorama

# Versioning
__project__ =       "nkscexport"
__author__ =        "Frederic MEZOU"
__author_email__ =  "frederic.mezou@orange.fr"
__license__ =       "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__copyright__ =      f"2026-%Y, {__author__}"
__description__ =   "Convert sidecar files from Nikon NX Studio (.nksc) in "\
                    "sidecar files compliant with Darktable"
__release__ =       "0.1.0-dev.0"
__version__ =       f"{__release__.split(".")[0]}.{__release__.split(".")[1]}"

__all__ = [
    "__project__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__description__",
    "__release__",
    "__version__",
    "NkscExport"
]

NIKON_RATING_MAP = {
    "-1": "-1",# rejeté → -1 en XMP
    "0":  "0", # Aucun
    "1":  "1", # *
    "2":  "2", # **
    "3":  "3", # ***
    "4":  "4", # ****
    "5":  "5", # *****
}
"""Correspondance note Nikon → note XMP (0-5)
Nikon stocke la note sous forme entière 0–5 directement compatible XMP"""

NIKON_LABEL_MAP = {
    "1": "Rouge",
    "2": "Orange",
    "3": "Jaune",
    "4": "Vert",
    "5": "Cyan",
    "6": "Bleu",
    "7": "Violet",
    "8": "Magenta",
    "9": "Rose",
    "0": "(Aucune)",
}
"""Correspondance label couleur Nikon → label XMP (texte)
Nikon encode les labels par numéro dans nksc"""

# Script display name: use in logger and the console UI
_DISPLAY_NAME = "nkscexport ({})".format(__version__)


class NkscExport:
    """
    Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files
    compliant with Darktable.

    **Attributes**
        This class has a number of public attributes listed below in
        alphabetical order.

        .. hlist::
            * :attr:`xxx`

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `build_xmp`                          `parse`
        `process`                            ..
        ===================================  ===================================


    **Using nkscexport...**
        This class is the scheduler and handles elementary operations to
        complete the expected task.

        The easiest way of using this class is to call the `process` method. This
        all-in-one method searches sidecar files in the required folders (and
        subfolders if required), reads the metadata and create or modify the
        sidecar files in XMP format at the same level than the original image
        file.

        To have more control, you must call individually each method. A typical
        use case is to read the metadata by calling the `parse` method then the
        `build_xmp` method.

    **Inside nkscexport...**
        ..to be completed..
    """
    def __init__(self):
        result = True

    def process(self):
        """
        Run the nkscexport application.

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error is written on console.
            log is written.
        """
        notify_start("process")
        result = True
        return result

    def build_xmp(self):
        """
        Run the nkscexport application.

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error is written on console.
            log is written.
        """
        notify_start("build_xmp")
        result = True
        return result

    def parse(self):
        """
        Run the nkscexport application.

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error is written on console.
            log is written.
        """
        notify_start("parse")
        result = True
        return result


def notify_start(verb):
    """
    Notify the user of the task starting.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        verb (str): The action verb of the task
    """
    foreground = "\x1b[1m" # set face text (bold)
    reset = "\x1b[0m" # reset text attribute
    msg = "**** Starting task: {} ****".format(verb)
    print(foreground, msg, reset, sep="")


def main():
    """
    Entry point

    This function call the sys.exit with the appropriate exit code (see
    the section *Exit Code* in :mod:`nkscexport`)
    """
    # Entry point
    # Build the command line parser
    parser = argparse.ArgumentParser(
        description="Convert sidecar files from Nikon NX Studio (.nksc) in "
                    "sidecar files compliant with Darktable")
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="make a recursive search of images files in subfolders.")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="overwrite existing sidecar files without prompting for "
             "confirmation.")
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="run in preview mode without any sidecar writing.")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s version " + __version__)

    # Parse and run.
    result = True
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure
    nkcs = NkscExport()
    dt = datetime.datetime.now()
    print("Starting {} on {:%c}".format(_DISPLAY_NAME, dt))
    result = nkcs.process()
    dt = datetime.datetime.now()
    print("{} completed on {:%c}".format(_DISPLAY_NAME, dt))

    if not result:
        sys.exit(1)


if __name__ == "__main__":
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")
    main()
