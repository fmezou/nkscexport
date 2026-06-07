"""Darkbridge core module

The :mod:`darkbridge.core` module schedules operations to convert the
sidecar files. Main task are filtering/checking the supported image
files, parsing the Nikon sidecar files, transforming the metadata and
wrinting the result in a XMP sidecar file compliant with Darktable.

The exported classes, exceptions and functions (and any other objects)
are as follows:

``core`` exceptions
-------------------
.. todo:: Review the list after completing

``core``  classes
-----------------
.. hlist::
    :columns: 2

    * :class:`DarkBridge`- Convert sidecar files

``core`` constants
------------------
.. todo:: Review the list after completing

Using ``core``
--------------
.. todo:: Describe how using the module

``core`` reference manual
-------------------------
"""
import argparse
import datetime
import glob
import locale
import logging
import pathlib
import sys
from pathlib import Path
from xml.etree import ElementTree

from colorama import Fore, Back, Style

from sidecar.nikon import *


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class DarkBridge(object):
    """Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files
    compliant with Darktable.

    Args:
        pathname: List of pathname of images files list based on patterns
            as defined by `glob.glob` function.
        recursive: `True` make a recursive search of images files in
            subfolders.


    Using darkbridge
    ----------------

    This class is the scheduler and handles elementary operations to
    complete the expected task.

    The easiest way of using this class is to call the `convert` or
    `list` methods. The first searches sidecar files in the required
    folders (and subfolders if required), reads the metadata and create
    or modify the sidecar files in XMP format at the same level as the
    original image file. The second do the same, but only displays
    metadata stored in Nikon sidecar files.

    Reference
    ---------
    """
    _pathname: list[str]
    _recursive: bool
    _paths: list[list[Path]]
    _nksc: None | NikonSideCar # current NKSC file

    def __init__(self, pathname: list[str], recursive: bool):
        self._pathname = pathname
        self._recursive = recursive
        self._paths = []
        self._nksc = None

    def _filter_filelist(self, path: Path) -> None | list[Path]:
        """ Filter the file list by removing no supported images files or
        images files without sidecar files.

        Args:
            path: Path of the image file.

        Returns:
            A list of two paths: the path of the image file and the path
            of the Nikon sidecar file. `None` if the image file is not
            supported or without sidecar file.
        """
        paths_set = None
        # check the suffix (maybe lower case or upper case)
        if path.is_file():
            if path.suffix.lower() in NIKON_SUPPORTED_FORMAT:
                # build the sidecar name
                name = path.name + NIKON_NKSC_EXT
                nksc_path = (path.parent / NIKON_NKSC_SUBFOLDER / name)
                if nksc_path.exists():
                    paths_set = [path, nksc_path]
                else:
                    _logger.info(
                        f"Sidecar image file '{nksc_path.name}' not exist. "
                        f"Image file '{path.name}' ignored")
            else:
                _logger.warning(
                    f"Image file not supported. "
                    f"Image file '{path.name}' ignored")
        else:
            _logger.info(
                f"Not a file. '{path.name}' ignored")

        return paths_set

    def _build_filelist(self) -> bool:
        """ Build the images files list based on patterns as defined in
        `glob.glob` functions.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self._paths = []
        for pathname in self._pathname:
            names = glob.glob(pathname, recursive=self._recursive)
            for name in names:
                paths = self._filter_filelist(pathlib.Path(name).resolve())
                if paths is not None:
                    self._paths.append(paths)
                else:
                    print(f"File '{name}' ignored as it is not a supported "
                          f"image file or no sidecar file exists",
                          file=sys.stderr)
        return True

    def convert(self, dry_run: bool, force: bool) -> bool:
        """Entry point to launch conversions to Darktable sidecar files

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and create or modify the sidecar files in XMP format at
        the same level as the original image file.

        Args:
            dry_run: `True` runs in preview mode without any sidecar
                writing.
            force: `True` overwrites existing sidecar files without
                prompting for confirmation.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def list(self, all: bool, detailed: bool) -> bool:
        """Entry point to launch metadata listing.

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and list metadata for each files.

        Args:
            detailed: `True` includes active filters specified in
                sidecar files. `False` displays '[F]' in metadata to
                indicate that at least a filter is active. In this case,
                the ``all`` parameter is ignored.
            all: `True` includes all filters, `False` enumerates only
                active filters.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self._build_filelist()
        for path in self._paths:
            _logger.debug(f"Parsing of '{path[1].name}'...")
            file = path[1].open()
            tree = ElementTree.parse(file)
            self._nksc = NikonSideCar(tree.getroot())
            self._nksc.parse()
            if detailed:
                print(Fore.GREEN
                      +Style.BRIGHT
                      +f"Image {path[0].name:30}"
                      +Style.RESET_ALL)
                print(f"{self._get_metadata(all)}")
            else:
                print(Fore.GREEN
                      +Style.BRIGHT
                      +f"Image {path[0].name:30}"
                      +Style.RESET_ALL
                      +": "
                      +Fore.MAGENTA
                      +Style.BRIGHT
                      +f"{self._get_summary()}"
                      +Style.RESET_ALL)
            file.close()
        return True

    def _get_summary(self) -> str:
        """Return a summary of image metadata

        Returns:
            A string with the metadata summary.
        """
        # nom du fichier image (uniquement)
        # classement
        # etiquette
        # protégé ou pas
        # post traitement ou pas
        # darktable : presence de tag ou pas
        # geolocalisé ou pas
        if self._nksc.ast.gps.longitude is None:
            msg = ""
        else:
            msg = " [G] "

        return msg

    def _get_metadata(self, all: bool) -> str:
        """Return a summary of image metadata

        Args:
            all: `True` includes all filters, `False` enumerates only
                active filters.

        Returns:
             A string with the metadata.
        """
        lines = []
        msg = ""
        if self._nksc.nine.nine_edits is not None:
            lines.append(Style.DIM+f"    nine edit: {str(self._nksc.nine.nine_edits[:20])}"+Style.RESET_ALL)
        if self._nksc.ast.xml_packets is not None:
            lines.append(Style.DIM+f"    xml packet: {str(self._nksc.ast.xml_packets[:20])}"+Style.RESET_ALL)
        if self._nksc.ast.iptc is not None:
            lines.append(Style.DIM+f"    iptc: {str(self._nksc.ast.iptc[:20])}"+Style.RESET_ALL)
        if self._nksc.ast.gps.longitude is not None:
            lines.append(Style.BRIGHT+f"    location: {self._nksc.ast.gps}"+Style.RESET_ALL)
        msg = "\n".join(lines)
        return msg

