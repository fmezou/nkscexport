"""Darkbridge core module

The :mod:`darkbridge.core` module schedules operations to convert the
sidecar files. Main task are filtering/checking the supported image
files, parsing the Nikon sidecar files, transforming the metadata and
wrinting the result in a XMP sidecar file compliant with Darktable.

The exported classes, exceptions and functions (and any other objects)
are as follows:

``core`` exceptions
-------------------

Todo:
    Review the list after completing

``core``  classes
-----------------
.. hlist::
    :columns: 2

    * :class:`DarkBridge`- Convert sidecar files

``core`` constants
------------------

Todo:
    Review the list after completing

Using ``core``
--------------

Todo:
    Describe how using the module

``core`` reference manual
-------------------------
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
    absract class, a concrete class should be defined by overriding the
    following methods:

    * :meth:`show_start` -- Display starting information
    * :meth:`show_complete` -- Display ending information
    * :meth:`show_list` -- Display sidecar contents during a list
      operation
    * :meth:`show_convert` -- Display sidecar contents during a convert
      operation

    Args:
        filenames: List of images filenames (see :class:`DarkBridge`)
        recursive: `True` make a recursive search (see :class:`DarkBridge`)
        dry_run: `True` runs in preview mode (see :meth:`DarkBridge.convert`)
        force: `True` overwrites existing sidecar files (see
            :meth:`DarkBridge.convert`).
        detailed: `True` includes active image's adjustments (see
            :meth:`DarkBridge.list`).
        all: `True` includes all image's adjustments (see
            :meth:`DarkBridge.list`).

    Attributes:
        verb: see ``verb`` parameter.
        filenames: see ``filenames`` parameter.
        recursive: see ``recursive`` parameter.
        dry_run: see ``dry_run`` parameter.
        force: see ``force`` parameter.
        detailed: see ``detailed`` parameter.
        all: see ``all`` parameter.

    Raise:
        ValueError: Inappropriate value, the :attr:`ValueError.message`
            details the error.

    ``Display`` Reference
    ---------------------
    """
    #: Supported verbs defining the ongoing operation
    VERBS = ["list", "convert"]
    verb: str
    filenames: list[str]
    recursive: bool
    dry_run: bool
    force: bool
    detailed: bool
    all: bool
    def __init__(self, filenames: list[str], recursive: bool,
                 dry_run: bool, force: bool,
                 all: bool, detailed: bool):
        # Store paramaters as public attributes to simplify the code reading
        self.filenames = filenames
        self.recursive = recursive
        self.dry_run = dry_run
        self.force = force
        self.detailed = detailed
        self.all = all

    def show_start(self, verb: str, total: int):
        """Display starting information at the operation launching.

        Args:
            verb: Name of the launched operation. The possible values
               defined in `Display.VERBS`: ``list`` for listing the
               metadata, ``convert`` for converting to Darktable sidecar
               files. Any other value should raise a ValueError
               exception.
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_complete(self, index: int):
        """Display ending information at the operation completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than :arg:`total`.
        """
        raise NotImplementedError

    def show(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents during an operation.

        Args:
            index: Index of the current image files. The index cannot be
                greater than :arg:`total`.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
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
                              f" {mode} - Number of files: {total}")

            case _:
                raise ValueError(f"Unsupported verb, actual: "
                                 f"{self.verb}, expected: {self.VERBS}")

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
            print(f"[{index}/{self.total}] Image {path.name:30}")
            print(f"{self._get_metadata(self.all)}")
        else:
            print(f"[{index}/{self.total}] Image {path.name:30}: "
                  + f"{self._get_summary()}")

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
            msgs.append(f" [{'*' * rate:5}]")

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
            msgs.append(f"    Metadata")
            for k, v in self.nksc.metadata.items():
                msgs.append(f"      * {k}: {v}")
        else:
            msgs.append("    No Metadata present")

        if self.nksc.processing is not None:
            msgs.append(f"    Adjustment")
            for k, v in self.nksc.processing.items():
                if all:
                    if v.active:
                        msgs.append(f"      * [X] {k} ")
                    else:
                        msgs.append(f"      * [ ] {k} ")
                else:
                    if v.active:
                        msgs.append(f"      * {k}")

        return "\n".join(msgs)


class DarkBridge(object):
    """Convert sidecar files from Nikon NX Studio (.nksc) in sidecar files
    compliant with Darktable.

    Args:
        pathname: List of pathname of images files list based on patterns
            as defined by `glob.glob` function.
        recursive: `True` make a recursive search of images files in
            subfolders.
        dry_run: `True` runs in preview mode without any sidecar
            writing.
        force: `True` overwrites existing sidecar files without
            prompting for confirmation.
        detailed: `True` includes active image's adjustments specified in
            sidecar files. `False` displays a summary of metadata. In this
            case, the ``all`` parameter is ignored.
        all: `True` includes all image's adjustments, `False` enumerates only
            active image's adjustments.


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
                 dry_run: bool, force: bool,
                 all: bool, detailed: bool,
                 display: BaseDisplay | None = None):
        self._pathname = pathname
        self._recursive = recursive
        self._paths = []
        self._nksc = None
        self._display = DefaultDisplay(pathname, recursive, dry_run,
                                       force, all, detailed)
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

    def convert(self) -> bool:
        """Entry point to launch conversions to Darktable sidecar files

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and create or modify the sidecar files in XMP format at
        the same level as the original image file.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        raise NotImplementedError

    def list(self) -> bool:
        """Entry point to launch metadata listing.

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and list metadata for each files.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        self._build_filelist()
        numfiles = len(self._paths)
        index = 0
        self._display.show_start('list', numfiles)
        for path in self._paths:
            index += 1
            _logger.info(f"[{index}/{numfiles}] Parsing of '{path[1].name}'...")

            file = path[1].open()
            tree = ElementTree.parse(file)
            self._nksc = NikonSideCar(tree.getroot())
            if self._nksc is not None:
                self._nksc.parse()
                self._display.show(index, path[0], self._nksc)
            file.close()
        self._display.show_complete(index)
        return True

