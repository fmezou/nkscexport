"""
Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files compliant
with Darktable.
This script may be used as a module by a third party offering a new GUI for
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

.. option:: -a, --all

    include all the metadata or filters in the list, not only the active one or
    not empty

.. option:: --list-filters

    list the active filters (or all if --all option is enabled) specified in
    sidecar files. The transferable filters are colored in green.

.. option:: --list-metadata

    list the metadata specified in the sidecar files

.. option:: -v, --version

    show program's version number and exit

.. option:: file ...

    files or directory to parse. For each item that name a supported image file,
    nkscexport parse the associated Nikon sidecar file and copy metadata in the
    darktable sidecar file. For each item that name a directory, nkscexport list
    supported images files contained in the directory, and parse each files. If
    no file are given, the content of the current directory is used.

nkscexport ignore files that not macthing the following criteria:

* a Nikon sidecar file is in a ``NKSC_PARAM`` folder
* a Nikon sidecar is named ``<basename>.<extension>.nksc`` where
  ``<basename>.<extension>`` is the image file name
* a supported image file exist with the same name that the sidecar
  file in the parent folder
* a darktable sidecar exist with the same name that the Nikon sidecar in the
  parent folder (this criterion is only checked when options `--list-filters`
  or `--list-metadata` are not enabled)

The script only support image files supported by NX Studio [1]_ :
``.nef``, ``.nrw``, ``.jpg``, ``.jpeg``, ``.tif``, ``.tiff``, ``.hif``,
``.nefx``, ``.mpo``).

.. [1] Nikon, NX Studio Supported Formats,
    https://nikonimglib.com/nxstdo/onlinehelp/en/supported_formats_4.html


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
:function:`nkscexport`                          ..
===================================  ===================================

.. _user manual: http://fmezou.github.io/nkscexport/
"""
import argparse
import pathlib
import sys
from xml.etree.ElementTree import ElementTree
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

NIKON_SUPPORTED_FORMAT = [
    ".nef", ".nrw",
    ".jpg", ".jpeg",
    ".tif", ".tiff",
    ".hif",
    ".nefx",
    ".mpo"
]
# Script display name: use in logger and the console UI
_DISPLAY_NAME = "nkscexport ({})".format(__version__)

class NikonSideCar (object):
    """
    NIKON Side car file.

    This class parses a ``.nksc`` file to extract the metadata of the image on
    the one hand, and the image processing stack on the other.
    The NKSC files are in XML/XMP, so we walk in the RDF tree.

    Args:
        filename (str): The full path name of the ``.nksc`` file.

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `parse`                              ..
        ===================================  ===================================

    **Using NikonSideCar...**

    """

    def __init__(self, filename=None):
        self._metadata = {}
        self._processing = {}
        self._data = None
        self._tree = ElementTree.parse(filename)

    def dump(self):
        """
        Args:
            source (object): A file name or file object.
            parser (object, optional): An optional parser instance that defaults
                to XMLParser.

        Raises:
            SpecSyntaxError: Spec file is erroneous.
            PADSyntaxError: A tag in a PAD file don't match the PAD Specs

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error log is written on the standard error (``stderr``).
        """

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
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "%(prog)s version " + __version__ + "\n"
                      "Convert sidecar files from Nikon NX Studio (.nksc) in "
                      "sidecar files compliant with Darktable",
        epilog = "nkscexport ignore files that not macthing the following "
                 "criteria:\n"
                 "* a Nikon sidecar file is in a 'NKSC_PARAM' folder\n"
                 "* a Nikon sidecar is named '<basename>.<extension>.nksc' "
                 "where '<basename>.<extension>' is the image file name\n"
                 "* a supported image file exist with the same name that the "
                 "sidecar file in the parent folder\n"
                 "* a darktable sidecar exist with the same name that the "
                 "Nikon sidecar in the parent folder (this criterion is only "
                 "checked when options '--list-filters' or '--list-metadata' "
                 "are not enabled)\n"
                 "\n"
                 "The script only support image files supported by NX "
                 "Studio: .nef, .nrw, .jpg, .jpeg, .tif, .tiff, .hif, .nefx "
                 ".mpo)."
    )
    parser.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "make a recursive search of images files in subfolders."
    )
    parser.add_argument(
        "-f", "--force",
        action = "store_true",
        help = "overwrite existing sidecar files without prompting for "
               "confirmation."
    )
    parser.add_argument(
        "-n", "--dry-run",
        action = "store_true",
        help = "run in preview mode without any sidecar writing."
    )
    parser.add_argument(
        "-a", "--all",
        action = "store_true",
        help = "include all the metadata or filters in the list, not only the "
            "active one or not empty."
    )
    parser.add_argument(
        "--list-filters",
        action = "store_true",
        help = "list the active filters (or all if --all option is enabled) "
               "specified in sidecar files. The transferable filters are "
               "colored in green."
    )
    parser.add_argument(
        "--list-metadata",
        action = "store_true",
        help = "list the metadata specified in the sidecar files"
    )
    parser.add_argument(
        "-v", "--version",
        action = "version",
        version = "%(prog)s version " + __version__
    )
    parser.add_argument(
        "filename",
        default = ".",
        nargs = "*",
        type = pathlib.Path,
        help = "files or directory to parse. For each item that name a "
               "supported image file, nkscexport parse the associated Nikon "
               "sidecar file and copy metadata in the darktable sidecar file. "
               "For each item that name a directory, nkscexport list supported "
               "images files contained in the directory, and parse each files. "
               "If no file are given, the content of the current directory is "
               "used."
    )

    # Parse the command line and run.
    result = True
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure
    nkcs = NkscExport()
    print("Starting {} on {:%c}".format(_DISPLAY_NAME, datetime.datetime.now()))
    # nkcs=NikonSideCar(filename)
    print(args.filename)
    print("{} completed on {:%c}".format(_DISPLAY_NAME, datetime.datetime.now()))

    if not result:
        sys.exit(1)

if __name__ == "__main__":
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")
    main()
