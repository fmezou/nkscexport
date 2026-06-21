"""Darkbridge core module

The :mod:`darkbridge.core` module schedules operations to convert the
sidecar files. Main task are filtering/checking the supported image
files, parsing the Nikon sidecar files, transforming the metadata and
wrinting the result in a XMP sidecar file compliant with Darktable.

The exported classes, exceptions and functions (and any other objects)
are as follows:

Exceptions
----------

Todo:
    Review the list after completing

Classes
-------
.. hlist::
    :columns: 2

    * :class:`DarkBridge`- Convert sidecar files

Constants
---------

Todo:
    Review the list after completing

Using ``core``
--------------

Todo:
    Describe how using the module

Reference manual
----------------
"""
import glob
import logging
import pathlib
import sys
from pathlib import Path
from xml.etree import ElementTree

from sidecar.nikon import *

__all__ = [
    "BaseDisplay",
    "DefaultDisplay",
    "DarkBridge"
]

# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BaseDisplay(object):
    """Base class for managing display of image's metadata.

    This class is an abstract class used by :class:`DarkBridge` to display
    metadata, processing module, progress status during an operation
    (:meth:`DarkBridge.convert`, :meth:`DarkBridge.list`). As it is an
    absract class, a concrete class should be defined by overriding one
    or more following methods:

    * :meth:`start_convert` -- Display the conversion launching.
    * :meth:`show_convert` -- Display the result of a search (unitary)
    * :meth:`complete_convert` -- Display the conversion completion
    * :meth:`start_list` -- Display starting information
    * :meth:`show_meta` -- Display sidecar contents
    * :meth:`show_meta_overview` -- Display an overview of sidecar contents
    * :meth:`complete_list` -- Display the listing completion
    * :meth:`start_search` -- Display the searching launching
    * :meth:`show_meta_findings` -- Display the result of a search (unitary)
    * :meth:`complete_search` -- Display the searching completion.

    Args:
        filenames: List of images filenames (see :class:`DarkBridge`)
        recursive: `True` make a recursive search (see :class:`DarkBridge`)

    Attributes:
        filenames: see ``filenames`` parameter.
        recursive: see ``recursive`` parameter.
        dry_run: see ``dry_run`` parameter.
        force: see ``force`` parameter.
        detailed: see ``detailed`` parameter.
        all: see ``all`` parameter.
        pattern: see ``pattern`` parameter.
        count: see ``count`` parameter.

    Raise:
        ValueError: Inappropriate value, the :attr:`ValueError.message`
            details the error.

    ``Display`` Reference
    ---------------------
    """
    #: Supported verbs defining the ongoing operation.
    verb: str
    filenames: list[str]
    recursive: bool
    dry_run: bool
    force: bool
    detailed: bool
    all: bool
    pattern: str
    count: bool
    def __init__(self, filenames: list[str], recursive: bool):
        # Store paramaters as public attributes to simplify the code reading
        self.filenames = filenames
        self.recursive = recursive
        self.dry_run = False
        self.force = False
        self.detailed = False
        self.all = False
        self.pattern = ""
        self.count = False

    def start_convert(self, dry_run: bool, force: bool, total: int):
        """Display the conversion launching.

        Args:
            dry_run: `True` runs in preview mode (see :meth:`DarkBridge.convert`)
            force: `True` overwrites existing sidecar files (see
                :meth:`DarkBridge.convert`).
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_convert(self, index: int, path: Path, nksc: NikonSideCar):
        """Display a sidecar content after conversion.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_convert(self, index: int):
        """Display the conversion completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
        """
        raise NotImplementedError

    def start_list(self, detailed: bool, all: bool, total: int):
        """Display the listing launching.

        Args:
            detailed: `True` includes active image's adjustments specified
                in sidecar files. `False` displays a summary of metadata.
            all: `True` includes all image's adjustments, `False`
                enumerates only active image's adjustments.
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_meta(self, index: int, path: Path, nksc: NikonSideCar, all: bool):
        """Display sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
            all: `True` includes all image's adjustments (see
                :meth:`DarkBridge.list`).
        """
        raise NotImplementedError

    def show_meta_overview(self, index: int, path: Path, nksc: NikonSideCar):
        """Display an overview of sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_list(self, index: int):
        """Display the listing completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
        """
        raise NotImplementedError

    def start_search(self, pattern: str, count: bool, total: int):
        """Display the searching launching.

        Args:
            pattern: Substring to find in metadata field names.
            count: `True` displays only a count of selected images.
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_findings(self, index: int, path: Path, nksc: NikonSideCar):
        """Display the result of a search (unitary)

        This method is called when the finding should be displayed (`count`
        parameters to `False`).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_search(self, index: int, found: int):
        """Display the searching completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
            found: Number of image's files where metadata or processing name
                match the pattern
        """
        raise NotImplementedError

    def ignore(self, path: Path):
        """Indicate that an image's file is ignored.

        An image's files is ignored when it is not a supported image file
        or no sidecar file exists.

        Args:
            path: Path of the current image file.
        """
        raise NotImplementedError


class DefaultDisplay(BaseDisplay):
    """Concrete class for managing display of image's metadata.

    This concrete class implements the default behavior for displaying
    image's metadata. The display is simply based on standard output.

    Attributes:
        total: Number of image files in the processing pipe.
        path: Path of the current image file.
        nksc: Object containing the metadata and processing data of
            the current image.

    Note:
        The attributes below are specific to this concrete class. For
        the attributes of the base class, see :class:`BaseDisplay`
    """
    total: int
    def __init__(self, filenames: list[str], recursive: bool):
        super().__init__(filenames, recursive)
        self.total = 0
        self.path = None
        self.nksc = None

    def start_convert(self, dry_run: bool, force: bool, total: int):
        """Display the conversion launching.

        Args:
            dry_run: `True` runs in preview mode (see :meth:`DarkBridge.convert`)
            force: `True` overwrites existing sidecar files (see
                :meth:`DarkBridge.convert`).
            total: Number of image files in the processing pipe.
        """
        self.total = total
        self.dry_run = dry_run
        self.force = force
        modes = ["(mode:"]
        if self.recursive:
            modes.append("recursive")
        if force:
            modes.append("forced")
        if dry_run:
            modes.append("dry_run")
        if len(modes) > 1:
            modes.append(")")
            mode = " ".join(modes)
        else:
            mode = ""
        print(f"Convert sidecar files from '{self.filenames}' {mode}"
              f" - Number of files: {total}")
        _logger.debug(f"Convert sidecar files from '{self.filenames=}'"
                      f" {mode} - Number of files: {total}")

    def show_convert(self, index: int, path: Path, nksc: NikonSideCar):
        """Display a sidecar content after conversion.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_convert(self, index: int):
        """Display the conversion completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
        """
        print(f"Convert sidecar files from '{self.filenames}' completed"
              f" - Number of files processed: {index}")
        _logger.debug(f"Convert sidecar files from '{self.filenames=}' completed"
                      f" - Number of files processed: {index}")

    def start_list(self, detailed: bool, all: bool, total: int):
        """Display the listing launching.

        Args:
            detailed: `True` includes active image's adjustments specified
                in sidecar files. `False` displays a summary of metadata.
            all: `True` includes all image's adjustments, `False`
                enumerates only active image's adjustments.
            total: Number of image files in the processing pipe.
        """
        self.total = total
        self.detailed = detailed
        self.all = all

        modes = ["(mode:"]
        if self.recursive:
            modes.append("recursive")
        if all:
            modes.append("all")
        if detailed:
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

    def show_meta(self, index: int, path: Path, nksc: NikonSideCar, all: bool):
        """Display sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
            all: `True` includes all image's adjustments (see
                :meth:`DarkBridge.list`).
        """
        msgs = []
        print(f"[{index}/{self.total}] Image {path.name:30}")
        if nksc.metadata is not None:
            msgs.append(f"    Metadata")
            for k, v in nksc.metadata.items():
                msgs.append(f"      * {k}: {v}")
        else:
            msgs.append("    No Metadata present")

        if nksc.processing is not None:
            msgs.append(f"    Adjustment")
            for k, v in nksc.processing.items():
                if all:
                    if v.active:
                        msgs.append(f"      * [X] {k} ")
                    else:
                        msgs.append(f"      * [ ] {k} ")
                else:
                    if v.active:
                        msgs.append(f"      * {k}")

        print("\n".join(msgs))

    def show_meta_overview(self, index: int, path: Path, nksc: NikonSideCar):
        """Display an overview of sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        msgs = []
        rate = nksc.get_rating()
        if rate == -1:
            msgs.append(" [XXXXX]")
        else:
            msgs.append(f" [{'*' * rate:5}]")

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

        print(f"[{index}/{self.total}] Image {path.name:30}: "
              f"{"".join(msgs)}")

    def complete_list(self, index: int):
        """Display the listing completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
        """
        print(f"List metadata from '{self.filenames}' completed"
              f" - Number of files processed: {index}")
        _logger.debug(f"List metadata from '{self.filenames=}' completed"
                      f" - Number of files processed: {index}")

    def start_search(self, pattern: str, count: bool, total: int):
        """Display the searching launching.

        Args:
            pattern: Substring to find in metadata field names.
            count: `True` displays only a count of selected images.
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_findings(self, index: int, path: Path, nksc: NikonSideCar):
        """Display the result of a search (unitary)

        This method is called when the finding should be displayed (`count`
        parameters to `False`).

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_search(self, index: int, found: int):
        """Display the searching completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``total`` parameter.
            found: Number of image's files where metadata or processing name
                match the pattern
        """
        raise NotImplementedError


    def ignore(self, path: Path):
        """Indicate that an image's file is ignored.

        An image's files is ignored when it is not a supported image file
        or no sidecar file exists.

        Args:
            path: Path of the current image file.
        """
        print(f"File '{path.name}' ignored as it is not a supported "
              f"image file or no sidecar file exists",
              file=sys.stderr)


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
    _display: BaseDisplay
    def __init__(self, pathname: list[str], recursive: bool,
                 display: BaseDisplay | None = None):
        self._pathname = pathname
        self._recursive = recursive
        self._paths = []
        self._nksc = None
        self._display = DefaultDisplay(pathname, recursive)
        if display is not None:
            self._display = display

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
        `glob.glob` function.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self._paths = []
        for pathname in self._pathname:
            names = glob.glob(pathname, recursive=self._recursive)
            for name in names:
                img_path = pathlib.Path(name).resolve()
                paths = self._filter_filelist(img_path)
                if paths is not None:
                    self._paths.append(paths)
                else:
                    self._display.ignore(img_path)
        return True

    def convert(self,dry_run: bool, force: bool) -> bool:
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
        metadata and list metadata for each file.

        Args:
            detailed: `True` includes active image's adjustments specified
                in sidecar files. `False` displays a summary of metadata.
                In this case, the ``all`` parameter is ignored.
            all: `True` includes all image's adjustments, `False`
                enumerates only active image's adjustments.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self._build_filelist()
        numfiles = len(self._paths)
        index = 0
        self._display.start_list(detailed, all, numfiles)
        for path in self._paths:
            index += 1
            _logger.info(f"[{index}/{numfiles}] Parsing of '{path[1].name}'...")

            file = path[1].open()
            tree = ElementTree.parse(file)
            self._nksc = NikonSideCar(tree.getroot())
            if self._nksc is not None:
                self._nksc.parse()
                if detailed:
                    self._display.show_meta(index, path[0], self._nksc, all)
                else:
                    self._display.show_meta_overview(index, path[0], self._nksc)
            file.close()
        self._display.complete_list(index)
        return True

    def search_meta(self, pattern: str, count: bool) -> bool:
        """Entry point to search a pattern in metadata

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and indicate if the pattern is found in metada.

        Args:
            pattern: Substring to find in metadata field names.
            count: `True` displays only a count of selected images.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def search_processing(self, pattern: str, count: bool) -> bool:
        """Entry point to search a pattern in processing

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and indicate if the pattern is found in active
        processing.

        Args:
            pattern: Substring to find in processing names.
            count: `True` displays only a count of selected images.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError
