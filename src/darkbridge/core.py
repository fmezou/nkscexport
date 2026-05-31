"""Convert Nikon sidecar files

The :mod:`core` module schedules operations to convert the sidecar files.
Main task are filtering/checking the supported image files, parsing the
Nikon sidecar files, transforming the metadata and wrinting the result
in a XMP sidecar file compliant with Darktable.

The exported classes, exceptions and functions (and any other objects)
are as follows:

darkbridge.core exceptions
--------------------------
.. todo:: review the list after completing

darkbridge.core classes
-----------------------
.. hlist::
    :columns: 2

    * :class:`DarkBridge`- Convert sidecar files

darkbridge.core constants
-------------------------
.. todo:: review the list after completing

Using darkbridge.core
---------------------
.. todo:: describe how using the module

darkbridge.core reference manual
--------------------------------
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

from darkbridge.sidecar import nikon


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

