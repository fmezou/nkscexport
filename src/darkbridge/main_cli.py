"""Converts Nikon sidecar files into Darktable sidecars.

Synopsis
--------

usage: :samp:`darkbridge.py [-h] [-r] [-f] [-n] [-a] [--list-filters]
[--list-metadata] [--log-level LOG_LEVEL] [-v] [filename ...]`

Description
-----------

:program:`darkbridge` is a utility that converts Nikon NX Studio :file:`.nksc`
sidecar files into sidecar files compatible with Darktable. It helps
photographers migrate adjustment data from Nikon’s workflow to Darktable
without manually recreating edits.

Darkbridge ignores files that not matching following criteria:

* a Nikon sidecar file is in a :file:`NKSC_PARAM` folder
* a Nikon sidecar is named :file:`{basename}.{extension}.nksc` where
  :file:`{basename}.{extension}` is the image file name
* a darktable sidecar exists with the same name that the Nikon sidecar
  in the parent folder.

The script only supports image files supported by NX Studio [1]_ :
:file:`.nef`, :file:`.nrw`, :file:`.jpg`, :file:`.jpeg`, :file:`.tif`,
:file:`.tiff`, :file:`.hif`, :file:`.nefx`, :file:`.mpo`.

The options are as follows:

.. program:: darkbridge

.. option:: -h, --help

    Show this help message and exit.

.. option:: -r, --recursive

    Make a recursive search of images files in subfolders.

.. option:: -f, --force

    Overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    Run in preview mode without any sidecar writing.

.. option:: -a, --all

    Include all the metadata or filters in the list, not only the
    active one or not empty.

.. option:: --list-filters

    List the active filters (or all if --all option is enabled)
    specified in sidecar files. The transferable filters are colored
    in green. Existance of darktable sidecar file is ignored when this
    option is used.

.. option:: --list-metadata

    List the metadata specified in the sidecar files. Existance of
    darktable sidecar file is ignored when this option is used.

.. option:: --log-level LOG_LEVEL

    Logging messages which are less severe than level will be ignored.
    Level may be set to: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL.
    Upper case or lower case are accepted and level is set to INFO by
    default.

.. option:: -v, --version

    Show program's version number and exit.

.. option:: file ...

    Files or directory to parse. For each item that name a supported
    image file, darkbridge parse the associated Nikon sidecar file and
    copy metadata in the darktable sidecar file. For each item that
    name a directory, darkbridge lists supported images files contained
    in the directory, and parses each files. If no file are given, the
    content of the current directory is used.

.. [1] Nikon, NX Studio Supported Formats,
    https://nikonimglib.com/nxstdo/onlinehelp/en/supported_formats_4.html

Exit status
-----------

==  ====================================================================
0   No error
1   An error occurred (error messages are print on stderr stream
    console).
2   Invalid argument. An argument of the command line isn't valid
    (see Usage).
==  ====================================================================

Example
-------
Convert the sidecar file :file:`./NKSC_PARAM/landscape.NEF.nkcs` into
:file:`./landscape.NEF.xmp`::

    darkbridge landscape.NEF

Same as above but converting all the sidecar files in the current directory.::

    darkbridge ./*.NEF

Same as above but converting all the sidecar files in the current directory
and all subdirectory::

    darkbridge --recursive ./**/*.NEF
"""
import argparse
import datetime
import locale
import logging
import sys

import colorama

from darkbridge.core import DarkBridge
from darkbridge.version import version
from darkbridge.version import name


def main():
    """Analyze the command line option and launch the conversion.

    This function call the sys.exit with the appropriate exit code.
    """
    # Entry point
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")

    # Build the command line parser
    # The prog name should be identical to that declared in the file
    # 'pyproject.toml' (see section [project.scripts])
    parser = argparse.ArgumentParser(
        prog = "darkbridge",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "%(prog)s version " + version + "\n"
            "converts Nikon sidecar files into Darktable sidecars.",
        epilog = "%(prog)s ignores files that not matching following "
            "criteria:\n"
            "* a Nikon sidecar file is in a 'NKSC_PARAM' folder\n"
            "* a Nikon sidecar is named '<basename>.<extension>.nksc' "
            "where '<basename>.<extension>' is the image file name\n"
            "* a darktable sidecar exists with the same name that the "
            "Nikon sidecar in the parent folder\n"
            "\n"
            "The script only supports image files supported by NX "
            "Studio: .nef, .nrw, .jpg, .jpeg, .tif, .tiff, .hif, .nefx "
            ".mpo."
    )
    parser.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "Make a recursive search of images files in subfolders."
    )
    parser.add_argument(
        "-f", "--force",
        action = "store_true",
        help = "Overwrite existing sidecar files without prompting for "
               "confirmation."
    )
    parser.add_argument(
        "-n", "--dry-run",
        action = "store_true",
        help = "Run in preview mode without any sidecar writing."
    )
    parser.add_argument(
        "-a", "--all",
        action = "store_true",
        help = "Include all the metadata or filters in the list, not only the "
            "active one or not empty."
    )
    parser.add_argument(
        "--list-filters",
        action = "store_true",
        help = "List the active filters (or all if --all option is enabled) "
               "specified in sidecar files. The transferable filters are "
               "colored in green. Existance of darktable sidecar file is "
               "ignored when this option is used."
    )
    parser.add_argument(
        "--list-metadata",
        action = "store_true",
        help = "List the metadata specified in the sidecar files. Existance "
               "of darktable sidecar file is ignored when this option is used."
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
        version = "%(prog)s version " + version
    )
    parser.add_argument(
        "filename",
        default = "./*",
        nargs = "*",
        type = str, #pathlib.Path,
        help = "Files or directories to parse. For each item that name a "
               "supported image file, darkbridge parses the associated Nikon "
               "sidecar file and copy metadata in the darktable sidecar file. "
               "For each item that name a directory, darkbridge list supported "
               "images files contained in the directory, and parses each files. "
               "If no file are given, the content of the current directory is "
               "used."
    )

    # Parse the command line and run.
    result = True
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure

    # Set up the root logging system
    numeric_level = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(
        level=numeric_level,
        style="{",
        stream=sys.stdout,
        format="{levelname} {name} {funcName} {message}")

    _logger.info(
        f"Starting {name} v{version} on {datetime.datetime.now():%c}")

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

    _logger.info(
        f"{name} v{version} completed on {datetime.datetime.now():%c}")
    if not result:
        sys.exit(1)

_logger = logging.getLogger(__name__)
if __name__ == "__main__":
    main()
