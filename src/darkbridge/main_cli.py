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

    List active image's adjustments (aka. image processing) specified in
    sidecar files. This option list only the active image's adjustments,
    unless if ``--all`` option is specified. Transferable image's
    adjustments are colored in green. If this option is not present,
    A '[F]' is added in metadata to indicate that at least an image's
    adjustment is active. In this case, ``--all`` option is ignored.

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
from darkbridge.core import BaseDisplay
from sidecar.nikon import NikonSideCar
from darkbridge.version import version


class CLIDisplay(BaseDisplay):
    """Concrete class for managing display of image's metadata.

    This concrete class implements the default behavior for displaying
    image's metadata. The display is simply based on standard output.

    Attributes:
        verb: Name of the launched operation.
        total: Number of image files in the processing pipe.
        path: Path of the current image file.
        nksc: Object containing the metadata and processing data of
            the current image.

    Note:
        The attributes below are specific to this concrete class. For
        the attributes of the base class, see :class:`BaseDisplay`

    Reference
    ---------
    """
    total: int
    def __init__(self, filenames: list[str], recursive: bool,
                 dry_run: bool, force: bool,
                 all: bool, detailed: bool):
        super().__init__(filenames, recursive,
                         dry_run, force, all, detailed)
        self.total = 0
        self.path = None
        self.nksc = None

    def show_start(self, verb: str, total: int):
        """Display starting information at the operation launching.

        Args:
            verb: Name of the launched operation.
            total: Number of image files in the processing pipe.
        """
        self.total = total
        self.verb = verb
        match self.verb:
            case 'list':
                modes = ["(mode:"]
                if self.recursive:
                    modes.append("recursive")
                if self.all:
                    modes.append("all")
                if self.detailed:
                    modes.append("detailed")
                if len(modes) > 1:
                    modes.append(")")
                    mode = " ".join(modes)
                else:
                    mode = ""
                print(f"List metadata from '{self.filenames}' {mode}"
                      f" - Number of files: {total}")
                _logger.debug(f"List metadata from '{self.filenames=}' {mode}"
                              f" - Number of files: {total}")

            case 'convert':
                modes = ["(mode:"]
                if self.recursive:
                    modes.append("recursive")
                if self.force:
                    modes.append("forced")
                if self.dry_run:
                    modes.append("dry_run")
                if len(modes) > 1:
                    modes.append(")")
                    mode = " ".join(modes)
                else:
                    mode = ""
                print(f"Convert sidecar files from '{self.filenames}' {mode}"
                      f" - Number of files: {total}")
                _logger.debug(f"Convert sidecar files from '{self.filenames=}'"
                              f" {modes} - Number of files: {total}")

    def show_complete(self, index: int):
        """Display ending information at the operation completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than :arg:`total`.
        """
        match self.verb:
            case 'list':
                print(f"List metadata from '{self.filenames}' completed"
                      f" - Number of files processed: {index}")
                _logger.debug(f"List metadata from '{self.filenames=}' completed"
                              f" - Number of files processed: {index}")

            case 'convert':
                print(f"Convert sidecar files from '{self.filenames}' completed"
                      f" - Number of files processed: {index}")
                _logger.debug(f"Convert sidecar files from '{self.filenames=}' completed"
                              f" - Number of files processed: {index}")

    def show(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents during an operation.

        Args:
            index: Index of the current image files. The index cannot be
                greater than :arg:`total`.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        self.path = path
        self.nksc = nksc
        if self.detailed:
            print(colorama.Fore.GREEN
                  +colorama.Style.BRIGHT
                  +f"[{index}/{self.total}] Image {path.name:30}"
                  +colorama.Style.RESET_ALL)
            print(f"{self._get_metadata(self.all)}")
        else:
            print(colorama.Fore.GREEN
                  +colorama.Style.BRIGHT
                  +f"[{index}/{self.total}] Image {path.name:30}"
                  +colorama.Style.RESET_ALL
                  +": "
                  +colorama.Fore.MAGENTA
                  +colorama.Style.BRIGHT
                  +f"{self._get_summary()}"
                  +colorama.Style.RESET_ALL)

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

    def _get_summary(self) -> str:
        """Return a summary of image metadata

        Returns:
            A string with the metadata summary.
        """
        msgs = []
        rate = self.nksc.get_rating()
        if rate == -1:
            msgs.append(" [XXXXX]")
        else:
            msgs.append(f" [{'*'*rate:5}]")

        label = self.nksc.get_label()
        if label != -1:
            msgs.append(f" [{label}]")

        if self.nksc.is_geotagged():
            msgs.append(" [G]")

        if self.nksc.is_tagged():
            msgs.append(" [T]")

        if self.nksc.is_protected():
            msgs.append(" [Lck]")

        if self.nksc.is_adjusted():
            msgs.append(" [F]")

        if self.nksc.is_exposure_comp():
            msgs.append(".[+/-]")

        if self.nksc.is_bw():
            msgs.append(".[BW]")

        if self.nksc.is_cropped():
            msgs.append(".[Crp]")

        if self.nksc.is_perpective_adj():
            msgs.append(".[H/V]")

        if self.nksc.is_denoised():
            msgs.append(".[NR]")

        return "".join(msgs)

    def _get_metadata(self, all: bool) -> str:
        """Return a summary of image metadata

        Args:
            all: `True` includes all image's adjustments, `False` enumerates only
                active image's adjustments.

        Returns:
             A string with the metadata.
        """
        msgs = []
        if self.nksc.metadata is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"    Metadata"
                        + colorama.Style.RESET_ALL)
            for k, v in self.nksc.metadata.items():
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

        if self.nksc.processing is not None:
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTMAGENTA_EX
                        + f"    Adjustment"
                        + colorama.Style.RESET_ALL)
            for k, v in self.nksc.processing.items():
                if all:
                    if v.active:
                        msgs.append(colorama.Style.BRIGHT
                                    + f"      * {k}"
                                    + colorama.Style.RESET_ALL)
                    else:
                        msgs.append(colorama.Style.DIM
                                    + f"      * {k}"
                                    + colorama.Style.RESET_ALL)
                else:
                    if v.active:
                        msgs.append(colorama.Style.BRIGHT
                                    + f"      * {k}"
                                    + colorama.Style.RESET_ALL)

        return "\n".join(msgs)


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
    list_parser = subparsers.add_parser(
        "list",
        help="List metadata from Nikon sidecar files. Existance of darktable"
             "sidecar file is ignored when this option is used."
    )
    list_parser.add_argument(
        "-a", "--all",
        default = False,
        action = "store_true",
        help = "Include all the metadata, not only the active one or "
               "not empty."
    )
    list_parser.add_argument(
        "-d", "--detailed",
        default = False,
        action = "store_true",
        help = "List active image's adjustments (aka. image processing)"
               "specified in sidecar files. This option list only the active"
               "image's adjustments, unless if ``--all`` option is specified."
               "Transferable image's adjustments are colored in green. If this "
               "option is not present, A '[F]' is added in metadata to indicate "
               "that at least an image's adjustment is active. In this case, "
               "``--all`` option is ignored."
    )
    list_parser.add_argument(
        "-r", "--recursive",
        default = False,
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
    match args.verb:
        case 'list':
            display = CLIDisplay(args.filename, args.recursive,
                                 False, False,
                                 args.all, args.detailed)
            bridge = DarkBridge(args.filename, args.recursive,
                                False, False,
                                args.all, args.detailed,
                                display)
            result = bridge.list()

        case 'convert':
            display = CLIDisplay(args.filename, args.recursive,
                                 args.dry_run, args.force,
                                 False, False)
            bridge = DarkBridge(args.filename, args.recursive,
                                args.dry_run, args.force,
                                False, False,
                                display)
            result = bridge.convert()

    _logger.info(
        f"{parser.prog} v{version} completed on {datetime.datetime.now():%c}")

    if not result:
        sys.exit(1)

_logger = logging.getLogger(__name__)
if __name__ == "__main__":
    main()
