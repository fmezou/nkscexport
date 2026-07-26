"""Converts Nikon sidecar files into Darktable sidecars.

The :mod:`darkbridge.__main__` module is the command line interface entry
point

Reference
---------

Entry point
^^^^^^^^^^^
.. autofunction:: main

Display objects
^^^^^^^^^^^^^^^
.. autoclass:: CLIDisplay
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:
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
        the attributes of the base class, see
        :class:`darkbridge.core.DefaultDisplay`
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
            msgs.append(f" [{label}]".ljust(13))
        else:
            msgs.append(" "*13)

        if nksc.is_geotagged():
            msgs.append(" [G]")
        else:
            msgs.append(" "*4)

        if nksc.is_tagged():
            msgs.append(" [T]")
        else:
            msgs.append(" "*4)

        if nksc.is_adjusted():
            msgs.append(" [F]")
        else:
            msgs.append(" " * 4)

        if nksc.is_exposure_comp():
            msgs.append(".[+/-]")
        else:
            msgs.append(" " * 6)

        if nksc.is_monochrome():
            msgs.append(".[BW]")
        else:
            msgs.append(" " * 5)

        if nksc.is_cropped():
            msgs.append(".[Crp]")
        else:
            msgs.append(" " * 6)

        if nksc.is_perspective_adj():
            msgs.append(".[H/V]")
        else:
            msgs.append(" " * 6)

        if nksc.is_denoised():
            msgs.append(".[NR]")
        else:
            msgs.append(" " * 4)

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
        if nksc.is_geotagged():
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"      * GPS"
                        + colorama.Style.RESET_ALL)

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
        if nksc.is_geotagged():
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"      * GPS"
                        + colorama.Fore.BLACK
                        + f": {nksc.geolocation}"
                        + colorama.Style.RESET_ALL)

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
                    if isinstance(p, bytes):
                        dump = self._dump_data(p, "            " )
                        msgs.append(f"          * {n}: {dump}")
                    else:
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
        for k, v in nksc.geolocation.props.items():
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLUE_EX
                        + f"      * {k}"
                        + colorama.Fore.BLACK
                        + f": {v}"
                        + colorama.Style.RESET_ALL)

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
                    if isinstance(p, bytes):
                        dump = self._dump_data(p, "            " )
                        msgs.append(f"          * {n}: {dump}")
                    else:
                        msgs.append(f"          * {n}: {p} ")
            else:
                msgs.append(colorama.Style.DIM
                            + colorama.Fore.LIGHTMAGENTA_EX
                            + f"      * [ ] {k}"
                            + colorama.Style.RESET_ALL)
                for n, p in v.params.items():
                    if isinstance(p, bytes):
                        dump = self._dump_data(p, "            " )
                        msgs.append(colorama.Style.DIM
                                    + f"          * {n}: {dump}"
                                    + colorama.Style.RESET_ALL)
                    else:
                        msgs.append(colorama.Style.DIM
                                    + f"          * {n}: {p} "
                                    + colorama.Style.RESET_ALL)

        print("\n".join(msgs))

    def _dump_data(self, data: bytes, prefix:str):
        """Dump an obscure data structure.

        This method returns a human-readable representation of an obscure
        data (unknown or obfuscated data structure). The representation
        is a common one based on standard hexadecimal dump (left part
        with bytes expressed in hexadecimal and right part as character
        if possible).

        Args:
            data: Obscure data expressed as binary array.
            prefix: String starting output lines to indent the output if
                needed
        """
        msgs = []
        buffer = data
        msgs.append(f"Obscure data ({len(data)} bytes)")
        head = f"00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F"
        msgs.append(colorama.Style.BRIGHT
                    + colorama.Fore.LIGHTBLACK_EX
                    + f"{prefix}....  {head}"
                    + colorama.Style.RESET_ALL)
        i = 0
        while len(buffer) != 0:
            lpart = buffer[0:8]
            rpart = buffer[8:16]
            hexa = f"{lpart.hex(" ")}  {rpart.hex(" ")}".ljust(len(head))
            lascii = str(lpart.translate(self._data_trans), encoding='ascii')
            rascii = str(rpart.translate(self._data_trans), encoding='ascii')
            ascii = f"{lascii}{rascii}".ljust(16)
            msgs.append(colorama.Style.BRIGHT
                        + colorama.Fore.LIGHTBLACK_EX
                        + f"{prefix}{i:04x}  "
                        + colorama.Style.NORMAL
                        + f"{hexa}  |{ascii}|"
                        + colorama.Style.RESET_ALL)
            buffer = buffer[16:]
            i += 16

        return "\n".join(msgs)


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
                        if isinstance(p, bytes):
                            dump = self._dump_data(p, "            " )
                            msgs.append(f"          * {n}: {dump}")
                        else:
                            msgs.append(f"          * {n}: {p} ")
                else:
                    msgs.append(colorama.Style.BRIGHT
                                + colorama.Fore.LIGHTBLUE_EX
                                + f"      * {k}"
                                + colorama.Fore.BLACK
                                + f": {v}"
                                + colorama.Style.RESET_ALL)

        print("\n".join(msgs))


def main() -> int:
    """Entry point of the DarkBridge package.

    See the user guide ":ref:`user_guide/darkbridge:DarkBridge`" for a
    full description of options and usage example.
    """
    exitcode = 0
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
        default = ["./*"],
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
        default = ["./*"],
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
        default = ["./*"],
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
            exitcode = 1

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

    if exitcode == 0:
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

    return exitcode

# Entry point
# Autodoc imports modules to be documented (including this one). So main
# routine is protected by an ``if __name__ == "__main__":``.
_logger = logging.getLogger(__name__)
if __name__ == "__main__":
    sys.exit(main())
