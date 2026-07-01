"""Converts Nikon sidecar files into Darktable sidecars.

Synopsis
--------

usage: :samp:`darkbridge [-h] [-l LOG_LEVEL] [-v] {convert,list,search} ...`

usage: :samp:`darkbridge list [-h] [-a] [-d] [-r] [filename ...]`

usage: :samp:`darkbridge convert [-h] [-f] [-n] [-r] [filename ...]`

usage: :samp:`darkbridge search [-h] (-p PROCESSING | -m META) [-c] [-r]
[filename ...]`

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

.. option:: search

    Search an image adjustment (processing) or a metadata into Nikon
    sidecar files.

.. option:: -h, --help

    Show this help message and exit

.. option:: -l, --log-level LOG_LEVEL

    Logging messages which are less severe than level will be ignored.
    Level may be set to: 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
    'CRITICAL'. Upper case or lower case are accepted and level is set
    to 'NOSET' by default. Log entries are write in a file in the
    current directory. If this option is not present or set to NOSET, no
    logfile is created

.. option::  -v, --verbose

    Increase the verbosity of report. By default, the report is
    a summary with image name and a set of indicators. A single
    ``-v`` lists relevant metadata (i.e. non-empty) and active image
    adjustments. A second ``-v`` (or ``-vv``) list metadata's content
    and image adjustment parameters. A third ``-v`` or ``-vvv``) list
    all metadata and image's adjustment whatever its status.

.. option:: -V, --version

    Show program's version number and exit

.. option:: -f, --force

    Overwrite existing sidecar files without prompting for confirmation.

.. option:: -n, --dry-run

    Run in preview mode without any sidecar writing.


.. option:: -p, --processing PROCESSING

    Name of the image adjustment (processing) to search. The search
    return the processing's name where substring 'PROCESSING' is found
    and if it is an active processing. The search is case-sensitive.

.. option:: -m, --meta META

    Name of the metadata's field to search. The search return the name
    of the field where substring 'META' is found. The search focuses on
    the field name and not the content of the field. The search is
    case-sensitive.

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

List metadata of image files the current directory and all subdirectory
with a verbosity level to show field names and contents::

    darkbridge -vv list --recursive ./*.NEF

Search images files with the metadata ``dc:subject`` entered::

    darkbridge -vv  search -m 'dc:subject' ./*.NEF

Same as above but with a more permisive pattern (i.e. all fields of 'dc'
family will be displayed::

    darkbridge -vv  search -m 'dc:' ./*.NEF

Show the images adjustement ``nikon::PictureControl`` of a particular image
files. Search may be used on a selection of files or one file::

    darkbridge -vv  search -p nikon::PictureControl landscape.NEF

Same as above but with a more permisive pattern (i.e. all image adjustement
relative to noise will be displayed::

    darkbridge -vv  search -p Noise landscape.NEF
"""
import argparse
import datetime
import locale
import logging
import sys
from pathlib import Path

import colorama

from darkbridge.core import DarkBridge
from darkbridge.core import DefaultDisplay
from darkbridge.sidecar.nikon import NikonSideCar
from darkbridge.sidecar.nik_adjustment import NikBaseAdjustment
from darkbridge.version import version


class CLIDisplay(DefaultDisplay):
    """Concrete class for managing display of image's metadata.

    This concrete class implements the default behavior for displaying
    image's metadata. The display is simply based on standard output
    with colored text.

    Note:
        The attributes below are specific to this concrete class. For
        the attributes of the base class, see :class:`DefaultDisplay`
    """
    def __init__(self):
        super().__init__()

    def show_meta(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        match self._verbosity:
            case 1:
                self._show_meta_v1(index, path, nksc)

            case 2:
                self._show_meta_v2(index, path, nksc)

            case 3:
                self._show_meta_v3(index, path, nksc)

            case _:
                self._show_meta_v0(index, path, nksc)


    def ignore(self, path: Path):
        """Indicate that an image's file is ignored.

        An image's files is ignored when it is not a supported image file
        or no sidecar file exists.

        Args:
            path: Path of the current image file.
        """
        print(colorama.Fore.LIGHTRED_EX
              + colorama.Style.BRIGHT
              + f"File '{path.name}' ignored as it is not a supported "
              + f"image file or no sidecar file exists"
              + colorama.Style.RESET_ALL,
              file=sys.stderr)


    def _show_meta_v0(self, index: int, path: Path, nksc: NikonSideCar):
        """Display an overview of sidecar contents (verbosity 0).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        msgs = []
        rate = nksc.get_rating()
        if rate == -1:
            msgs.append(" [XXXXX]")
        else:
            msgs.append(f" [{'*'*rate:5}]")

        label = nksc.get_label()
        if label != -1:
            msgs.append(f" [{label}]")

        if nksc.is_geotagged():
            msgs.append(" [G]")

        if nksc.is_tagged():
            msgs.append(" [T]")

        if nksc.is_protected():
            msgs.append(" [Lck]")

        if nksc.is_adjusted():
            msgs.append(" [F]")

        if nksc.is_exposure_comp():
            msgs.append(".[+/-]")

        if nksc.is_bw():
            msgs.append(".[BW]")

        if nksc.is_cropped():
            msgs.append(".[Crp]")

        if nksc.is_perpective_adj():
            msgs.append(".[H/V]")

        if nksc.is_denoised():
            msgs.append(".[NR]")

        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL
              + ": "
              + colorama.Fore.MAGENTA
              + colorama.Style.BRIGHT
              + f"{"".join(msgs)}"
              + colorama.Style.RESET_ALL)

    def _show_meta_v1(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents (verbosity 1).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        msgs = []
        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL)

        if nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"    Metadata"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.metadata.items():
                if len(v) != 0:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTBLUE_EX
                                + f"      * {k}"
                                + colorama.Style.RESET_ALL)
        else:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTRED_EX
                        + "    No Metadata present"
                        + colorama.Style.RESET_ALL)

        if nksc.processing is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTMAGENTA_EX
                        + f"    Adjustment"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.processing.items():
                if v.active:
                    msgs.append(colorama.Style.BRIGHT
                                + f"      * {k}"
                                + colorama.Style.RESET_ALL)

        print("\n".join(msgs))

    def _show_meta_v2(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents (verbosity 2).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        msgs = []
        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL)

        if nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"    Metadata"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.metadata.items():
                if len(v) != 0:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTBLUE_EX
                                + f"      * {k}"
                                + colorama.Fore.BLACK
                                + f": {v}"
                                + colorama.Style.RESET_ALL)
        else:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTRED_EX
                        + "    No Metadata present"
                        + colorama.Style.RESET_ALL)

        if nksc.processing is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTMAGENTA_EX
                        + f"    Adjustment"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.processing.items():
                if v.active:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTMAGENTA_EX
                                + f"      * {k}"
                                + colorama.Style.RESET_ALL)
                    for n, p in v.params.items():
                        msgs.append(f"          * {n}: {p} ")

        print("\n".join(msgs))

    def _show_meta_v3(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents (verbosity 3).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        msgs = []
        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL)

        if nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"    Metadata"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.metadata.items():
                msgs.append(colorama.Style.BRIGHT
                            + colorama.Fore.LIGHTBLUE_EX
                            + f"      * {k}"
                            + colorama.Fore.BLACK
                            + f": {v}"
                            + colorama.Style.RESET_ALL)
        else:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTRED_EX
                        + "    No Metadata present"
                        + colorama.Style.RESET_ALL)

        if nksc.processing is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTMAGENTA_EX
                        + f"    Adjustment"
                        + colorama.Style.RESET_ALL)
            for k, v in nksc.processing.items():
                if v.active:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTMAGENTA_EX
                                + f"      * [X] {k}"
                                + colorama.Style.RESET_ALL)
                    for n, p in v.params.items():
                        msgs.append(f"          * {n}: {p} ")
                else:
                    msgs.append(colorama.Style.DIM
                                + colorama.Fore.LIGHTMAGENTA_EX
                                + f"      * [ ] {k}"
                                + colorama.Style.RESET_ALL)
                    for n, p in v.params.items():
                        msgs.append(colorama.Style.DIM
                                    + f"          * {n}: {p} "
                                    + colorama.Style.RESET_ALL)

        print("\n".join(msgs))

    def show_findings(self, index: int, path: Path, nksc: NikonSideCar,
                      findings: dict):
        """Display the result of a search (unitary)

        This method is called when the finding should be displayed.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
            findings: Dictionnary of metadata or image's adjustment
                matching the ``pattern``.
        """
        match self._verbosity:
            case 0: # By default, no display
                pass

            case 1:
                self._show_findings_v1(index, path, nksc, findings)

            case _:
                self._show_findings_v2(index, path, nksc, findings)

    def _show_findings_v1(self, index: int, path: Path, nksc: NikonSideCar,
                          findings: dict):
        """Display the result of a search (verbosity 1).

        This method is called when the finding should be displayed.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
            findings: Dictionnary of metadata or image's adjustment
                matching the ``pattern``.
        """
        msgs = []
        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL)

        if nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + f"    Matching"
                        + colorama.Style.RESET_ALL)
            for k, v in findings.items():
                if isinstance(v, NikBaseAdjustment):
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTMAGENTA_EX
                                + f"      * {k}"
                                + colorama.Style.RESET_ALL)
                else:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTBLUE_EX
                                + f"      * {k}"
                                + colorama.Style.RESET_ALL)

        print("\n".join(msgs))

    def _show_findings_v2(self, index: int, path: Path, nksc: NikonSideCar,
                          findings: dict):
        """Display the result of a search (verbosity 2).

        This method is called when the finding should be displayed.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
            findings: Dictionnary of metadata or image's adjustment
                matching the ``pattern``.
        """
        msgs = []
        print(colorama.Fore.GREEN
              + colorama.Style.BRIGHT
              + f"[{index}/{self._total}] Image {path.name:30}"
              + colorama.Style.RESET_ALL)

        if nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + f"    Matching"
                        + colorama.Style.RESET_ALL)
            for k, v in findings.items():
                if isinstance(v, NikBaseAdjustment):
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTMAGENTA_EX +
                                f"      * {k}"
                                + colorama.Style.RESET_ALL)
                    for n, p in v.params.items():
                        msgs.append(f"          * {n}: {p} ")
                else:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTBLUE_EX
                                + f"      * {k}"
                                + colorama.Fore.BLACK
                                + f": {v}"
                                + colorama.Style.RESET_ALL)

        print("\n".join(msgs))


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
        help="Common commands for converting, listing or searching metadata. "
             "'%(prog)s {command} -h' to get help for a specific command."
    )
    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Converts Nikon sidecar files into Darktable sidecar files."
    )
    convert_parser.add_argument(
        "-f", "--force",
        default = False,
        action = "store_true",
        help = "Overwrite existing sidecar files without prompting for "
               "confirmation."
    )
    convert_parser.add_argument(
        "-n", "--dry-run",
        default = False,
        action = "store_true",
        help = "Run in preview mode without any sidecar writing."
    )
    convert_parser.add_argument(
        "-r", "--recursive",
        default = False,
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
    list = subparsers.add_parser(
        "list",
        help="List metadata from Nikon sidecar files. Existance of darktable "
             "sidecar file is ignored when this option is used."
    )
    list.add_argument(
        "-r", "--recursive",
        default = False,
        action = "store_true",
        help = "Make a recursive search of images files in subfolders."
    )
    # Positional arguments
    list.add_argument(
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
    # search command - the search focuses on metadata or processing,
    # but not both
    search = subparsers.add_parser(
        "search",
        help="Search an image adjustment (processing) or a metadata into Nikon "
             "sidecar files."
    )
    group = search.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p", "--processing",
        action = "store",
        help = "Name of the image adjustment (processing) to search. The "
               "search return the processing's name where substring "
               "'PROCESSING' is found and if it is an active processing."
    )
    group.add_argument(
        "-m", "--meta",
        action = "store",
        help = "Name of the metadata's field to search. The search return the "
               "name of the field where substring 'META' is found. The search "
               "focuses on the field name and not the content of the field."
    )
    search.add_argument(
        "-r", "--recursive",
        default = False,
        action = "store_true",
        help = "Make a recursive search of images files in subfolders."
    )
    # Positional arguments
    search.add_argument(
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
        "-v", "--verbose",
        action = "count",
        default = 0,
        help = "Increase the verbosity of report. By default, the report is "
               "a summary with image name and a set of indicators. A single "
               "'-v' lists relevant metadata (i.e. non-empty) and active image "
               "adjustments. A second '-v' (or '-vv') list metadata's content "
               "and image adjustment parameters. A third '-v' or '-vvv') list "
               "all metadata and image's adjustment whatever its status.")
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
        "-V", "--version",
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
    bridge = DarkBridge(args.verbose, args.filename, args.recursive,
                        CLIDisplay())
    match args.verb:
        case 'list':
            result = bridge.list()

        case 'convert':
            result = bridge.convert(args.dry_run, args.force)

        case 'search':
            if args.meta:
                result = bridge.search_meta(args.meta)
            if args.processing:
                result = bridge.search_processing(args.processing)

        case _:
            # impossible case
            raise NotImplementedError (f"Impossible case: "
                                       f"unknown verb '{args.verb}'")

    _logger.info(
        f"{parser.prog} v{version} completed on {datetime.datetime.now():%c}")

    if not result:
        sys.exit(1)

_logger = logging.getLogger(__name__)
if __name__ == "__main__":
    main()
