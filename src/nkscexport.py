"""
``nkcsexport`` convert sidecar files from Nikon NX Studio (``.nksc``) in
sidecar files compliant with Darktable. This script may be used as a
module by a third party offering a new GUI for example, or as a script
with the command line interface::

    python -m nkscexport

Synopsis
--------

``nkscexport.py [-h] [-r] [-f] [-n] [-a] [--list-filters]
[--list-metadata] [-v] [filename ...]``

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

    include all the metadata or filters in the list, not only the
    active one or not empty

.. option:: --list-filters

    list the active filters (or all if --all option is enabled)
    specified in sidecar files. The transferable filters are colored
    in green.

.. option:: --list-metadata

    list the metadata specified in the sidecar files

.. option:: -v, --version

    show program's version number and exit

.. option:: file ...

    files or directory to parse. For each item that name a supported
    image file, nkscexport parse the associated Nikon sidecar file and
    copy metadata in the darktable sidecar file. For each item that
    name a directory, nkscexport list supported images files contained
    in the directory, and parse each files. If no file are given, the
    content of the current directory is used.

nkscexport ignore files that not macthing the following criteria:

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
``.nefx``, ``.mpo``).

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

.. _user manual: http://fmezou.github.io/nkscexport/

nkscexport reference manual
---------------------------
"""
import argparse
import datetime
import locale
import pathlib
import sys

import colorama

from sidecar import nikon
from version import *


class NkscExport:
    """
    Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files
    compliant with Darktable.

    Using nkscexport
    ----------------

    This class is the scheduler and handles elementary operations to
    complete the expected task.

    The easiest way of using this class is to call the `process` method.
    This all-in-one method searches sidecar files in the required
    folders (and subfolders if required), reads the metadata and create
    or modify the sidecar files in XMP format at the same level than the
    original image file.

    To have more control, you must call individually each method. A
    typical use case is to read the metadata by calling the `parse`
    method then the `build_xmp` method.

    Reference
    ---------
    """
    def __init__(self):
        result = True

    def process(self) -> bool:
        """
        Run the nkscexport application.

        Returns:
            `True` if the execution went well. In case of failure, an
                error is written on console.
        """
        notify_start("process")
        result = True
        return result

    def build_xmp(self) -> bool:
        """
        Run the nkscexport application.

        Returns:
            `True` if the execution went well. In case of failure, an
                error is written on console.
        """
        notify_start("build_xmp")
        result = True
        return result

    def parse(self) -> bool:
        """
        Run the nkscexport application.

        Returns:
            `True` if the execution went well. In case of failure, an
                error is written on console.
        """
        notify_start("parse")
        result = True
        return result


def notify_start(verb: str):
    """
    Notify the user of the task starting.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        verb : The action verb of the task
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
    #nkcs = NkscExport()
    print("Starting {} v{} on {:%c}".format(__project__, __release__,
                                            datetime.datetime.now()))
    for filename in args.filename:
        path = pathlib.Path(filename).resolve()
        file = path.open()
        nkcs = nikon.NikonSideCar(file)
        nkcs.parse()
        file.close()
        #print (nkcs)
    print("{} v{} completed on {:%c}".format(__project__, __release__,
                                             datetime.datetime.now()))

    if not result:
        sys.exit(1)

if __name__ == "__main__":
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")
    main()
