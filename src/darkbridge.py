"""
``darkbridge`` is a utility that converts Nikon NX Studio `.nksc`
sidecar files into sidecar files compatible with Darktable. It helps
photographers migrate adjustment data from Nikon’s workflow to Darktable
without manually recreating edits. This script may be used as a module
by a third party offering a new GUI for example, or as a script with the
command line interface::

    python -m darkbridge

Synopsis
--------

``usage: darkbridge.py [-h] [-r] [-f] [-n] [-a] [--list-filters]
[--list-metadata] [--log-level LOG_LEVEL] [-v] [filename ...]``

Command line options
^^^^^^^^^^^^^^^^^^^^

.. program:: darkbridge

.. option:: -h, --help

    show this help message and exit

.. option:: -r, --recursive

    make a recursive search of images files in subfolders.

.. option:: -f, --force

    overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    run in preview mode without any sidecar writing.

.. option:: -a, --all

    include all the metadata or filters in the list, not only the
    active one or not empty

.. option:: --list-filters

    list the active filters (or all if --all option is enabled)
    specified in sidecar files. The transferable filters are colored
    in green.

.. option:: --list-metadata

    list the metadata specified in the sidecar files

.. option:: --log-level LOG_LEVEL

    Logging messages which are less severe than level will be ignored.
    Level may be set to: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    Upper case or lower case are accepted and level is set to INFO by
    default.

.. option:: -v, --version

    show program's version number and exit

.. option:: file ...

    files or directory to parse. For each item that name a supported
    image file, darkbridge parse the associated Nikon sidecar file and
    copy metadata in the darktable sidecar file. For each item that
    name a directory, darkbridge list supported images files contained
    in the directory, and parse each files. If no file are given, the
    content of the current directory is used.

darkbridge ignore files that not macthing the following criteria:

* a Nikon sidecar file is in a ``NKSC_PARAM`` folder
* a Nikon sidecar is named ``<basename>.<extension>.nksc`` where
  ``<basename>.<extension>`` is the image file name
* a supported image file exist with the same name that the sidecar
  file in the parent folder
* a darktable sidecar exist with the same name that the Nikon sidecar
  in the parent folder (this criterion is only checked when options
  `--list-filters` or `--list-metadata` are not enabled)

The script only support image files supported by NX Studio [1]_ :
``.nef``, ``.nrw``, ``.jpg``, ``.jpeg``, ``.tif``, ``.tiff``, ``.hif``,
``.nefx``, ``.mpo``.

.. [1] Nikon, NX Studio Supported Formats,
    https://nikonimglib.com/nxstdo/onlinehelp/en/supported_formats_4.html


Exit code
^^^^^^^^^

==  ====================================================================
0   no error
1   an error occurred (error messages are print on stderr stream
    console and write in a log file).
2   invalid argument. An argument of the command line isn't valid
    (see Usage).
==  ====================================================================

.. _user manual: https://darkbridge.readthedocs.io/

darkbridge reference manual
---------------------------
"""
import argparse
import datetime
import glob
import locale
import logging
import pathlib
import sys
from xml.etree import ElementTree


import colorama

from sidecar import nikon
from version import *


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class DarkBridge(object):
    """
    Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files
    compliant with Darktable.

    Using darkbridge
    ----------------

    This class is the scheduler and handles elementary operations to
    complete the expected task.

    The easiest way of using this class is to call the `run` method.
    This all-in-one method searches sidecar files in the required
    folders (and subfolders if required), reads the metadata and create
    or modify the sidecar files in XMP format at the same level as the
    original image file.

    To have more control, you must call individually each method. A
    typical use case is to build the images files list by calling
    `parse` method and run the conversion by calling `convert`

    Reference
    ---------
    """
    _pathname: list[str]
    _paths: list [pathlib.Path]

    def __init__(self, pathname: list[str]):
        self._pathname = pathname
        self._paths = []

    def list_filters(self, all: bool) -> bool:
        """
        list the image adjustment filters.

        Args:
            all: `True` includes all filters in the list, `False` limits the
                list to only active filters.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def list_metadata(self) -> bool:
        """
        list the metadata specified in the sidecar files.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def convert(self, dry_run: bool, force: bool, recursive:bool) -> bool:
        """
        Run the conversion.

        Args:
            dry_run: `True` runs in preview mode without any sidecar
                writing.
            force: `True` overwrites existing sidecar files without
                prompting for confirmation.
            recursive: `True` make a recursive search of images files in
                subfolders.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def filter(self) -> bool:
        """
        Filter the file list by removing no supported images files or
        images files without sidecar files.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def parse(self, recursive: bool) -> bool:
        """
        Build the images files list based on patterns as defined in
        `glob.glob` functions.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        for pathname in self._pathname:
            names = glob.glob(pathname, recursive=recursive)
            for name in names:
                self._paths.append(pathlib.Path(name).resolve())
        return True

    def run(self, dry_run: bool, force: bool, recursive: bool) -> bool:
        """
        All-in-one entry point to run the conversion

        Args:
            dry_run: `True` runs in preview mode without any sidecar
                writing.
            force: `True` overwrites existing sidecar files without
                prompting for confirmation.
            recursive: `True` make a recursive search of images files in
                subfolders.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self.parse(recursive)
        for path in self._paths:
            _logger.info(f"Parse '{path.name}'...")
            file = path.open()
            tree = ElementTree.parse(file)
            nkcs = nikon.NikonSideCar(tree.getroot())
            nkcs.parse()
            file.close()
        return True


def main():
    """
    Entry point

    This function call the sys.exit with the appropriate exit code (see
    the section *Exit Code* in :mod:`darkbridge`)
    """
    # Entry point
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")

    # Build the command line parser
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "%(prog)s version " + __version__ + "\n"
            "converts Nikon `.nksc` sidecar files into "
            "Darktable-compatible sidecars.",
        epilog = "darkbridge ignore files that not macthing the following "
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
        "--log-level",
        default="INFO",
        action="store",
        help="Logging messages which are less severe than level will be "
             "ignored. Level may be set to: NOTSET, DEBUG, INFO, WARNING, "
             "ERROR, CRITICAL. Upper case or lower case are accepted and "
             "level is set to INFO by default."
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
        type = str, #pathlib.Path,
        help = "files or directory to parse. For each item that name a "
               "supported image file, darkbridge parse the associated Nikon "
               "sidecar file and copy metadata in the darktable sidecar file. "
               "For each item that name a directory, darkbridge list supported "
               "images files contained in the directory, and parse each files. "
               "If no file are given, the content of the current directory is "
               "used."
    )

    # Parse the command line and run.
    result = True
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure

    # Set up the root logging system
    numeric_level = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=numeric_level,
                        style="{",
                        stream=sys.stdout,
                        format="{levelname} {name} {funcName} {message}")

    _logger.info("Starting {} v{} on {:%c}".format(__project__, __release__,
                                            datetime.datetime.now()))

    bridge = DarkBridge(args.filename)
    if args.list_filters:
        result = bridge.parse(args.recursive)
        if result:
            result = bridge.list_filters(args.all)
    if args.list_metadata:
        result = bridge.parse(args.recursive)
        if result:
            result = bridge.list_metadata()
    if not args.list_filters and not args.list_metadata:
        result = bridge.run(args.dry_run, args.force, args.recursive)

    _logger.info("{} v{} completed on {:%c}".format(__project__, __release__,
                                             datetime.datetime.now()))
    if not result:
        sys.exit(1)

if __name__ == "__main__":
    main()
