"""Darkbridge core module

The :mod:`darkbridge.core` module schedules operations to convert the
sidecar files. Main tasks are filtering/checking the supported image
files, parsing the Nikon sidecar files, transforming the metadata and
writing the result in a XMP sidecar file compliant with Darktable.
Furthermore, this module displays the sidecar content in a 'human-readable'
way, and allows to search a metadata or image adjustment by name in a
file tree structure.

This module is built around two set of features: the first one is the core
scheduler (:class:`DarkBridge`) to process the sidecar file, the second one
is the display manager (:class:`DefaultDisplay`).

Using ``core``
--------------

For this short tutorial, we have a photo in NEF format named 'full_XMP.IPTC.NEF'
in the folder named 'images_samples' and is associated sidecar file
('images_samples/NKSC_PARAM/full_XMP.IPTC.NEF.nksc'). We create an instance of
:class:`DarkBridge`) with a level of verbosity set to 2 to have field names
and contents.

>>> from darkbridge.core import DarkBridge
>>> bridge = DarkBridge(2, ["images_samples\\full_XMP.IPTC.NEF"], False, None)

We can list the metadata and image adjustement with :meth:`DarkBridge.list`.
The following output has been truncated to fit in the page.

>>> bridge.list()
List metadata from '['images_samples\\full_XMP.IPTC.NEF']'...
[1/1] Image full_XMP.IPTC.NEF
    Metadata
      * appname: NX Studio
      * appversion: 1.10 W
      * xmp:Rating: 5
      * xmp:Label: Rose
      * dc:title: [Description] Titre
      * dc:subject: ['Mot-clé #1', 'Mot-clé #2', 'Mot-clé #3']
      ...
      * Iptc4xmpExt:Event: ['[Description] Evénement']
    Adjustment
      * nikon::PictureControl
          * Export: b'NCP\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00$0100STANDARD...'
          * SelectedPictureControl: 0
          * AutoContrast: 255
          * AutoSaturation: 255
          * SelectedPictureControlVersion2: 0
          * SavedPicConProcess: 1
          * PictureControl: 0
      ...
List metadata from '['images_samples\\full_XMP.IPTC.NEF']' completed...

We can search if a metadata has been entered with :meth:`DarkBridge.search_meta`
(``dc:subject`` here, that contains the keyword).

>>> bridge.search_meta("dc:subject")
Search 'dc:subject' in metadata from '['images_samples\\full_XMP.IPTC.NEF']'...
[1/1] Image full_XMP.IPTC.NEF
    Matching
      * dc:subject: ['Mot-clé #1', 'Mot-clé #2', 'Mot-clé #3']
Found 1 images - Number of files: 1

We can search if an image adjustement is active with :meth:`DarkBridge.search_processing`
(``PictureControl`` here).

>>> bridge.search_processing("PictureControl")
Search 'PictureControl' in metadata from '['images_samples\\full_XMP.IPTC...
[1/1] Image full_XMP.IPTC.NEF
    Matching
      * nikon::PictureControl
          * Export: b'NCP\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00$0100STANDARD...'
          * SelectedPictureControl: 0
          * AutoContrast: 255
          * AutoSaturation: 255
          * SelectedPictureControlVersion2: 0
          * SavedPicConProcess: 1
          * PictureControl: 0
Found 1 images - Number of files: 1

The output in the examples above are the default one made by the
:class:`DefaultDisplay`. You can create a new class derived from the
:class:`BaseDisplay` or :class:`DefaultDisplay` to customize the output
(adding some colors, see :class:`darkbridge.main_cli.CLIDisplay` for
an example).

About verbosity level...
------------------------

The verbosity level impacts the leval of detail of each output. Verbosity
is a positive integer number between 0 and 3. Any values greater than 3
(or 2 for search) is considered the maximum level (i.e. 3 for list,
2 for search).

* :meth:`DarkBridge.list` -- list metadata and image adjustement

.. table:: verbosity level for list output

    +-------+-----------------------------------------------------------+
    | Level | output content (based on :class:DefaultDisplay`) [#co]_   |
    +=======+===========================================================+
    | 0     | write image name and a set of indicators.                 |
    |       | Example:                                                  |
    +-------+-----------------------------------------------------------+
    | 1     | write relevant metadata (i.e. non-empty) and active image |
    |       | adjustments.                                              |
    +-------+-----------------------------------------------------------+
    | 2     | write metadata's content and image adjustment parameters  |
    +-------+-----------------------------------------------------------+
    | 3     | write all metadata and image's adjustment whatever its    |
    |       | status.                                                   |
    +-------+-----------------------------------------------------------+

* :meth:`DarkBridge.convert` -- list convert Nikon sidecar files

.. table:: verbosity level for convert output

    +-------+-----------------------------------------------------------+
    | Level | output content (based on :class:DefaultDisplay`) [#co]_   |
    +=======+===========================================================+
    | 0     | write image name processed.                               |
    |       | Example:                                                  |
    +-------+-----------------------------------------------------------+
    | 1     | write image name, metadata and active image adjustement   |
    |       | processed.                                                |
    +-------+-----------------------------------------------------------+
    | 2     | write image name, metadata content and active image       |
    |       | adjustement's parameters processed.                       |
    +-------+-----------------------------------------------------------+
    | 3     | write image name, metadata and image's adjustment         |
    |       | parameters processed whatever its status                  |
    +-------+-----------------------------------------------------------+


* :meth:`DarkBridge.search_meta`, :meth:`DarkBridge.search_processing`
  -- search a metadata or an image adjustement

.. table:: verbosity level for search output

    +-------+-----------------------------------------------------------+
    | Level | output content (based on :class:DefaultDisplay`) [#co]_   |
    +=======+===========================================================+
    | 0     | write the number of image files matching search criterias |
    |       | Example:                                                  |
    +-------+-----------------------------------------------------------+
    | 1     | write image name, metadata and/or active image            |
    |       | adjustments matching search criterias.                    |
    +-------+-----------------------------------------------------------+
    | 2     | write image name, metadata's content and image adjustment |
    |       | parameters  matching search criterias.                    |
    +-------+-----------------------------------------------------------+
    | 3     | ignored                                                   |
    +-------+-----------------------------------------------------------+

Notes:
    .. [#co] The ``display`` parameter of the :class:`DarkBridge` allow to
        customize output (see :class:`BaseDisplay` and :class:`DefaultDisplay`
        for more details.


Reference
---------

Display objects
^^^^^^^^^^^^^^^

.. autoclass:: BaseDisplay
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: DefaultDisplay
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

Scheduler object
^^^^^^^^^^^^^^^^

.. autoclass:: DarkBridge
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:
"""
import logging
import sys
from pathlib import Path

from darkbridge.sidecar.nikon import *
from darkbridge.sidecar.nik_adjustment import NikBaseAdjustment


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


class BaseDisplay:
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
    """
    def __init__(self):
        pass

    def start_convert(self, filenames: list[str], recursive: bool,
                      dry_run: bool, force: bool, verbosity: int, total: int):
        """Display the conversion launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            dry_run: `True` runs in preview mode (see :meth:`DarkBridge.convert`)
            force: `True` overwrites existing sidecar files (see
                :meth:`DarkBridge.convert`).
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_convert(self, index: int, path: Path, nksc: NikonSideCar):
        """Display a sidecar content after conversion.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_convert(self, index: int):
        """Display the conversion completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
        """
        raise NotImplementedError

    def start_list(self, filenames: list[str], recursive: bool,
                   verbosity:int, total:int):
        """Display the listing launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

    def show_meta(self, index: int, path: Path, nksc: NikonSideCar):
        """Display sidecar contents.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_list(self, index: int):
        """Display the listing completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
        """
        raise NotImplementedError

    def start_search(self, filenames: list[str], recursive: bool,
                     pattern: str, verbosity:int, total: int):
        """Display the searching launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            pattern: Substring to find in metadata field names.
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def complete_search(self, index: int, matching: int):
        """Display the searching completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
            matching: Number of image's files where metadata or processing
                name match the pattern
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
    """
    _total: int
    def __init__(self):
        super().__init__()

        # Store paramaters as attributes
        self._filenames = None
        self._recursive = False
        self._dry_run = False
        self._force = False
        self._pattern = ""
        self._verbosity = 0
        self._total = 0
        self._path = None
        self._nksc = None

    def start_convert(self, filenames: list[str], recursive: bool,
                      dry_run: bool, force: bool, verbosity: int, total: int):
        """Display the conversion launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            dry_run: `True` runs in preview mode (see :meth:`DarkBridge.convert`)
            force: `True` overwrites existing sidecar files (see
                :meth:`DarkBridge.convert`).
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        self._filenames = filenames
        self._recursive = recursive
        self._total = total
        self._dry_run = dry_run
        self._force = force
        self._verbosity = verbosity
        modes = ["(mode:"]
        if self._recursive:
            modes.append("_recursive")
        if force:
            modes.append("forced")
        if dry_run:
            modes.append("_dry_run")
        if len(modes) > 1:
            modes.append(")")
            mode = " ".join(modes)
        else:
            mode = ""
        print(f"Convert sidecar files from '{self._filenames}' {mode}"
              f" - Number of files: {total}")
        _logger.debug(f"Convert sidecar files from '{self._filenames=}'"
                      f" {mode} - Number of files: {total}")

    def show_convert(self, index: int, path: Path, nksc: NikonSideCar):
        """Display a sidecar content after conversion.

        Args:
            index: Index of the current image files. The index cannot be
                greater than ``_total`` parameter.
            path: Path of the current image file.
            nksc: Object containing the metadata and processing data of
                the current image.
        """
        raise NotImplementedError

    def complete_convert(self, index: int):
        """Display the conversion completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
        """
        print(f"Convert sidecar files from '{self._filenames}' completed"
              f" - Number of files processed: {index}")
        _logger.debug(f"Convert sidecar files from '{self._filenames=}' completed"
                      f" - Number of files processed: {index}")

    def start_list(self, filenames: list[str], recursive: bool,
                   verbosity:int, total:int):
        """Display the listing launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        self._filenames = filenames
        self._recursive = recursive
        self._total = total
        self._verbosity = verbosity

        modes = ["(mode:"]
        if self._recursive:
            modes.append("recursive")
        modes.append(f"verbosity: {verbosity})")
        mode = " ".join(modes)

        print(f"List metadata from '{self._filenames}' {mode}"
              f" - Number of files: {total}")
        _logger.info(f"List metadata from '{self._filenames=}' {mode}"
                      f" - Number of files: {total}")

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
            case 0:
                self._show_meta_v0(index, path, nksc)

            case 1:
                self._show_meta_v1(index, path, nksc)

            case 2:
                self._show_meta_v2(index, path, nksc)

            case _:
                self._show_meta_v3(index, path, nksc)

    def complete_list(self, index: int):
        """Display the listing completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
        """
        print(f"List metadata from '{self._filenames}' completed"
              f" - Number of files processed: {index}")
        _logger.info(f"List metadata from '{self._filenames=}' completed"
                      f" - Number of files processed: {index}")

    def start_search(self, filenames: list[str], recursive: bool,
                     pattern: str, verbosity:int, total: int):
        """Display the searching launching.

        Args:
            filenames: List of images _filenames (see :class:`DarkBridge`)
            recursive: `True` make a _recursive search (see :class:`DarkBridge`)
            pattern: Substring to find in metadata field names.
            verbosity: level of verbosity for the command output. The
                level should be 0 to 3 (see
                :ref:`dev_guide/darkbridge/core:about verbosity level...`
                for more details)
            total: Number of image files in the processing pipe.
        """
        self._filenames = filenames
        self._recursive = recursive
        self._pattern = pattern
        self._verbosity = verbosity
        self._total = total

        modes = ["(mode:"]
        if self._recursive:
            modes.append("recursive")
        modes.append(f"verbosity: {verbosity})")
        mode = " ".join(modes)

        print(f"Search '{pattern}' in metadata from '{self._filenames}' {mode}"
              f" - Number of files: {total}")
        _logger.info(
            f"Search '{pattern}' in metadata from '{self._filenames}' {mode}"
            f" - Number of files: {total}")

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

    def complete_search(self, index: int, matching: int):
        """Display the searching completion.

        Args:
            index: Index of the last image files. The index cannot be
                greater than ``_total`` parameter.
            matching: Number of image's files where metadata or processing name
                match the pattern
        """
        print(f"Found {matching} images - Number of files: {index}")
        _logger.info(f"Found {matching} images - Number of files: {index}")

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

        print(f"[{index}/{self._total}] Image {path.name:30}: "
              f"{"".join(msgs)}")

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
        print(f"[{index}/{self._total}] Image {path.name:30}")
        if nksc.metadata is not None:
            msgs.append(f"    Metadata")
            for k, v in nksc.metadata.items():
                if len(v) != 0:
                    msgs.append(f"      * {k}")
        else:
            msgs.append("    No Metadata present")

        if nksc.processing is not None:
            msgs.append(f"    Adjustment")
            for k, v in nksc.processing.items():
                    if v.active:
                        msgs.append(f"      * {k} ")

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
        print(f"[{index}/{self._total}] Image {path.name:30}")
        if nksc.metadata is not None:
            msgs.append(f"    Metadata")
            for k, v in nksc.metadata.items():
                if len(v) != 0:
                    msgs.append(f"      * {k}: {v}")
        else:
            msgs.append("    No Metadata present")

        if nksc.processing is not None:
            msgs.append(f"    Adjustment")
            for k, v in nksc.processing.items():
                if v.active:
                    msgs.append(f"      * {k} ")
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
        print(f"[{index}/{self._total}] Image {path.name:30}")
        if nksc.metadata is not None:
            msgs.append(f"    Metadata")
            for k, v in nksc.metadata.items():
                msgs.append(f"      * {k}: {v}")
        else:
            msgs.append("    No Metadata present")

        if nksc.processing is not None:
            msgs.append(f"    Adjustment")
            for k, v in nksc.processing.items():
                if v.active:
                    msgs.append(f"      * [X] {k} ")
                else:
                    msgs.append(f"      * [ ] {k} ")
                for n, p in v.params.items():
                    msgs.append(f"          * {n}: {p} ")

        print("\n".join(msgs))

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
        print(f"[{index}/{self._total}] Image {path.name:30}")
        msgs.append(f"    Matching")
        for k, v in findings.items():
            msgs.append(f"      * {k}")

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
        print(f"[{index}/{self._total}] Image {path.name:30}")
        msgs.append(f"    Matching")
        for k, v in findings.items():
            if isinstance(v, NikBaseAdjustment):
                msgs.append(f"      * {k}")
                for n, p in v.params.items():
                    msgs.append(f"          * {n}: {p} ")
            else:
                msgs.append(f"      * {k}: {v}")

        print("\n".join(msgs))


class DarkBridge:
    """Convert sidecar files from Nikon NX Studio (._nksc) in sidecar files
    compliant with Darktable.

    Args:
        verbosity: level of verbosity for the command output. The
            level should be 0 to 3 (see
            :ref:`dev_guide/darkbridge/core:about verbosity level...`
            for more details).
        pathname: List of pathname of images files list based on patterns
            as defined by :meth:`Path.glob` function (see
            `pathlib-pattern-language` for more details)
        recursive: `True` make a _recursive search of images files in
            subfolders.
    """
    _verbosity: int
    _pathname: list[str]
    _recursive: bool
    _display: BaseDisplay
    # list of path pair to process:  first item is the path of the image file,
    # second item is the path of the Nikon sidecar file.
    _paths: list[list[Path]]
    # current NKSC file
    _nksc: None | NikonSideCar
    def __init__(self, verbosity: int, pathname: list[str], recursive: bool,
                 display: BaseDisplay | None = None):
        self._verbosity = verbosity
        self._pathname = pathname
        self._recursive = recursive
        self._paths = []
        self._nksc = None
        self._display = DefaultDisplay()
        if display is not None:
            self._display = display

    def _append_path(self, path: Path) -> None | list[Path]:
        """Add the path in the list of files to process.

        Only supported images files with a sidecar file are considered.

        Args:
            path: filesystem path of the image file to add.
        """
        # check the suffix (maybe lower case or upper case)
        if path.is_file():
            if path.suffix.lower() in NIKON_SUPPORTED_FORMAT:
                # build the sidecar name
                name = path.name + NIKON_NKSC_EXT
                nksc_path = (path.parent / NIKON_NKSC_SUBFOLDER / name)
                if nksc_path.exists():
                    self._paths.append([path, nksc_path])
                else:
                    _logger.info(
                        f"Sidecar image file '{nksc_path.name}' not exist. "
                        f"Image file '{path.name}' ignored")
            else:
                self._display.ignore(path)
                _logger.warning(
                    f"Image file not supported. "
                    f"Image file '{path.name}' ignored")
        else:
            _logger.info(
                f"Not a file. '{path.name}' ignored")

    def _build_filelist(self) -> int:
        """ Build the images files list based on patterns as defined in
        `glob.glob` function.

        The method returns a list of unique image files. If the selection
        pattern covers the same directory, the files are included only
        once.

        Returns:
            Number of filesystem path of image files to process
        """
        fq_pathname = []
        self._paths = []
        for pathname in self._pathname:
            p = Path(pathname)
            if self._recursive:
                paths = p.parent.rglob(p.name)
            else:
                paths = p.parent.glob(p.name)
            for path in paths:
                img_path = path.resolve()
                if img_path.as_uri() in fq_pathname:
                    _logger.info(f"Image file already processed: "
                                 f"'{img_path.name}' ignored")
                else:
                    self._append_path(img_path)
                    fq_pathname.append(img_path.as_uri())
        return len(self._paths)

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

    def list(self) -> bool:
        """Entry point to launch metadata listing.

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and list metadata for each file.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        numfiles = self._build_filelist()
        index = 0
        self._display.start_list(self._pathname, self._recursive, self._verbosity, numfiles)
        for path in self._paths:
            index += 1
            _logger.info(f"[{index}/{numfiles}] Parsing of '{path[1].name}'...")
            self._nksc = NikonSideCar(path[1])
            if self._nksc is not None:
                self._nksc.parse()
                self._display.show_meta(index, path[0], self._nksc)
        self._display.complete_list(index)
        return True

    def search_meta(self, pattern: str) -> bool:
        """Entry point to search a pattern in metadata

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and indicate if the pattern is found in metada.

        Args:
            pattern: Substring to find in metadata field names.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        numfiles = self._build_filelist()
        index = 0
        matching = 0
        self._display.start_search(self._pathname, self._recursive, pattern,
                                   self._verbosity, numfiles)
        for path in self._paths:
            index += 1
            found = False
            _logger.info(f"[{index}/{numfiles}] Parsing of '{path[1].name}'...")
            self._nksc = NikonSideCar(path[1])
            if self._nksc is not None:
                self._nksc.parse()
                findings = {}
                for k, v in self._nksc.metadata.items():
                    if pattern in k and len(v) != 0:
                        found = True
                        findings[k] = v
                        _logger.info(f"Metadata '{k}' match with '{pattern}'")
                if found:
                    self._display.show_findings(index, path[0], self._nksc, findings)
                    matching += 1
        self._display.complete_search(index, matching)
        return True

    def search_processing(self, pattern: str) -> bool:
        """Entry point to search a pattern in processing

        This method searches sidecar files in the required folders (and
        subfolders if :attr:`_recursive` is ``True``), reads the
        metadata and indicate if the pattern is found in active
        processing.

        Args:
            pattern: Substring to find in processing names.

        Returns:
            `True` if the execution went well. In case of failure, an
            error is written on console.
        """
        numfiles = self._build_filelist()
        index = 0
        matching = 0
        self._display.start_search(self._pathname, self._recursive, pattern,
                                   self._verbosity, numfiles)
        for path in self._paths:
            index += 1
            found = False
            _logger.info(f"[{index}/{numfiles}] Parsing of '{path[1].name}'...")
            self._nksc = NikonSideCar(path[1])
            if self._nksc is not None:
                self._nksc.parse()
                findings = {}
                for k, v in self._nksc.processing.items():
                    if pattern in k and v.active:
                        found = True
                        findings[k] = v
                        _logger.info(f"Processing '{k}' match with '{pattern}'")
                if found:
                    self._display.show_findings(index, path[0], self._nksc, findings)
                    matching += 1
        self._display.complete_search(index, matching)
        return True
