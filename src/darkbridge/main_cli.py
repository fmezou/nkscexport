"""Converts Nikon sidecar files into Darktable sidecars.

Synopsis
--------

usage: :samp:`darkbridge [-h] [-l LOG_LEVEL] [-v] {convert,list} ...`

usage: :samp:`darkbridge list [-h] [-a] [-d] [-r] [filename ...]`

usage: :samp:`darkbridge convert [-h] [-f] [-n] [-r] [filename ...]`

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

.. option:: convert

    Converts Nikon sidecar files into Darktable sidecar files.

.. option:: list

    List metadata from Nikon sidecar files. Existance of darktable
    sidecar file is ignored when this option is used.

.. option:: -h, --help

    Show this help message and exit

.. option:: -l, --log-level LOG_LEVEL

    Logging messages which are less severe than level will be ignored.
    Level may be set to: 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
    'CRITICAL'. Upper case or lower case are accepted and level is set
    to 'NOSET' by default. Log entries are write in a file in the
    current directory. If this option is not present or set to NOSET, no
    logfile is created

.. option:: -v, --version

    Show program's version number and exit

.. option:: -a, --all

    Include all the metadata, not only the active one or not empty.

.. option:: -d, --detailed

    List active filters (aka. image processing adjustment)specified in
    sidecar files. This option list only the activefilters, unless if
    ``--all`` option is specified. Transferablefilters are colored in
    green. If this option is not present, A '[F]' is added app in
    metadata to indicate that at least a filter is active. In this case,
    ``--all`` option is ignored.

.. option:: -f, --force

    Overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    Run in preview mode without any sidecar writing.

.. option:: -r, --recursive

    Make a recursive search of images files in subfolders.

.. option:: filename

    Files or directories to parse. For each item that name a supported
    image file, darkbridge parses the associated Nikon sidecar file and
    copy metadata in the darktable sidecar file. For each item that name
    a directory, darkbridge list supported images files contained in the
    directory, and parses each files. If no file are given, the content
    of the current directory is used.

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

    darkbridge convert landscape.NEF

Same as above but converting all the sidecar files in the current directory.::

    darkbridge convert ./*.NEF

List metadata of image files the current directory and all subdirectory::

    darkbridge list --recursive ./**/*.NEF

"""
import argparse
import datetime
import locale
import logging
import sys
from pathlib import Path

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
    # Sub commands
    subparsers = parser.add_subparsers(
        required = True,
        dest = 'verb',
        help="Common commands for converting or listing metadata. "
             "'%(prog)s {command} -h' to get help for a specific command."
    )
    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help='Converts Nikon sidecar files into Darktable sidecar files.'
    )
    convert_parser.add_argument(
        "-f", "--force",
        action = "store_true",
        help = "Overwrite existing sidecar files without prompting for "
               "confirmation."
    )
    convert_parser.add_argument(
        "-n", "--dry-run",
        action = "store_true",
        help = "Run in preview mode without any sidecar writing."
    )
    convert_parser.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "Make a recursive search of images files in subfolders."
    )
    # Positional arguments
    convert_parser.add_argument(
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
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List metadata from Nikon sidecar files. Existance of darktable"
             "sidecar file is ignored when this option is used."
    )
    list_parser.add_argument(
        "-a", "--all",
        action = "store_true",
        help = "Include all the metadata, not only the active one or "
               "not empty."
    )
    list_parser.add_argument(
        "-d", "--detailed",
        action = "store_true",
        help = "List active filters (aka. image processing adjustment)"
               "specified in sidecar files. This option list only the active"
               "filters, unless if ``--all`` option is specified. Transferable"
               "filters are colored in green. If this option is not present, "
               "A '[F]' is added app in metadata to indicate that at least a "
               "filter is active. In this case, ``--all`` option is ignored."
    )
    list_parser.add_argument(
        "-r", "--recursive",
        action = "store_true",
        help = "Make a recursive search of images files in subfolders."
    )
    # Positional arguments
    list_parser.add_argument(
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
    # common options
    parser.add_argument(
        "-l", "--log-level",
        default = "NOTSET",
        action = "store",
        help = "Logging messages which are less severe than level will "
               "be ignored. Level may be set to: 'NOTSET', 'DEBUG', "
               "'INFO', 'WARNING', 'ERROR', 'CRITICAL'. Upper case or "
               "lower case are accepted and level is set to 'NOSET' by "
               "default. Log entries are write in a file in the current "
               "directory. If this option is not present or set to "
               "NOSET, no logfile is created"
    )
    parser.add_argument(
        "-v", "--version",
        action = "version",
        version = "%(prog)s version " + version
    )

    # Parse the command line and run.
    result = True
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure

    # Set up the root logging system
    numeric_level = getattr(logging, args.log_level.upper(), None)
    match numeric_level:
        case None:
            print(f"{parser.prog}: error: argument -d/--log-level: invalid choice: "
                  f"'{args.log_level}' (choose from NOTSET, DEBUG, INFO, WARNING, "
                  f"ERROR, CRITICAL)",
                  file=sys.stderr)
            sys.exit(1)

        case 0:
            # No log required
            pass

        case _:
            logging.basicConfig(
                level = numeric_level,
                style = "{",
                filename = Path(".") / f"{parser.prog}.log",
                filemode = "w",
                format = "{levelname} {name} {funcName}:{lineno} {message}")

    _logger.info(
        f"Starting {parser.prog} v{version} on {datetime.datetime.now():%c}")
    bridge = DarkBridge(args.filename, args.recursive)
    match args.verb:
        case 'list':
            mode: str = f""
            if args.recursive:
                mode = mode + f" recursive"
            if args.all:
                mode = mode + f" all"
            if args.detailed:
                mode = mode + f" detailed"
            if mode != "":
                mode = "(mode:" + mode + ")"
            _logger.debug(f"List metadata from '{args.filename=}' {mode}")
            result = bridge.list(args.all, args.detailed)

        case 'convert':
            mode: str = f""
            if args.recursive:
                mode = mode + f" recursive"
            if args.force:
                mode = mode + f" force"
            if args.dry_run:
                mode = mode + f" dry_run"
            if mode != "":
                mode = "(mode:" + mode + ")"
            _logger.debug(f"Convert sidecar files from '{args.filename=}' {mode}")
            result = bridge.convert(args.all, args.detailed)

    _logger.info(
        f"{parser.prog} v{version} completed on {datetime.datetime.now():%c}")

    if not result:
        sys.exit(1)

_logger = logging.getLogger(__name__)
if __name__ == "__main__":
    main()
