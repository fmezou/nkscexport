"""Handle Nikon adjustments

The :mod:`sidecar.nik_adjustment` module implements handlers for the Nikon
image adjustments stored in Nikon sidecar files.file. The article named
":ref:`background_papers/inside_adjustment:Inside Nikon image adjustments`"
details the data structure and tags used by Nikon.

Each image adjustments, as declared in the observed sidecar file have
its own class to later implement the convert Nikon parameters to
Darktable module parameters if it is possible. Nevertheless, all these
classes are derived from the base class :class:`NikBaseAdjustment`. This
base class offers the interface contract and a set of common methods for
decoding parameters expressed as XMP properties.

Using ``nk_adjustment``
-----------------------

For this short tutorial, we have a dummy content of nine:NineEdits XMP
property used as sample.

.. code-block:: XML
   :caption: dummy nine:NineEdits XMP property

    <userData>
        <filter id="nikon::NoiseReduction">
            <active>true</active>
            <parameters>
                <integer name="NoiseReduction.version">13</integer>
                <integer name="NoiseReduction.endableMore">0</integer>
            </parameters>
        </filter>
        <filter id="nikon::transform">
            <active>true</active>
            <parameters>
                <integer name="Rotation">0</integer>
                <integer name="PreRotation">0</integer>
                <bool name="Flip">false</bool>
            </parameters>
        </filter>
        <filter id="nikon::DLightingHQ">
            <active>false</active>
            <parameters>
                <shadowAdjustment>50</shadowAdjustment>
                <highlightAdjustment>1</highlightAdjustment>
                <colorBoost>60</colorBoost>
            </parameters>
        </filter>
    </userData>

We use a linearized form of the XMP property expressed as a string.

>>> prop = ('<userData><filter id="nikon::NoiseReduction"><active>true</active>'
...         '<parameters><integer name="NoiseReduction.version">13</integer>'
...         '<integer name="NoiseReduction.endableMore">0</integer></parameters>'
...         '</filter><filter id="nikon::transform"><active>true</active>'
...         '<parameters><integer name="Rotation">0</integer>'
...         '<integer name="PreRotation">0</integer><bool name="Flip">false</bool>'
...         '</parameters></filter><filter id="nikon::DLightingHQ"><active>false'
...         '</active><parameters><shadowAdjustment>50</shadowAdjustment>'
...         '<highlightAdjustment>1</highlightAdjustment><colorBoost>60'
...         '</colorBoost></parameters></filter></userData>')

We create images adjustements objects based the above string with the factory
function :func:`create_nine_edits`.

>>> from darkbridge.sidecar.nik_adjustment import create_nine_edits
>>> from xml.etree import ElementTree
>>> tree = ElementTree.fromstring(prop)
>>> procs = create_nine_edits(tree)

We can list the image ajustements declarated in the XMP property,
:func:`create_nine_edits` returning a dictionary of image adjustments objects
with the image adjustment name as key.

>>> procs
{'nikon::NoiseReduction': NikNoiseReduction object: active=True, 'nikon::transform': Niktransform object: active=True, 'nikon::DLightingHQ': NikDLightingHQ object: active=False}

We can access to the status (active or not) and its parameters for each image
ajustement by using its shortname as key.

>>> procs['nikon::NoiseReduction']
NikNoiseReduction object: active=True
>>> procs['nikon::NoiseReduction'].active
True
>>> procs['nikon::NoiseReduction'].params
{'NoiseReduction.version': 13.0, 'NoiseReduction.endableMore': 0.0}

Reference
---------

Exception
^^^^^^^^^

.. autoexception:: NikAdjustmentError
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

Image adjustement functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: create_nine_edits

Image adjustment objects
^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: NikBaseAdjustment
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikColorShift
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDLightingHS
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikWhiteBalance
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikStraighten
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikPictureControl
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikQuickFixToneCurve
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikGaussianBlur
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikLEGeneral
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikFishEye
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDehaze
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikColorBalance
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikFlare
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikSkinTone
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikVignette
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikPerspective
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikChrAb
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikUnsharpMask
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikColorBooster
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikNXHistory
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikSkinSoftening
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikLevelsCurves
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikRedEye
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDiffraction
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDistortion
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikApplicationData
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikLongChrAb
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikExposureSettings
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikLCH
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikQuickFixContrast
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikGrainNoise
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDustOff
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: Niktransform
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikSizeRes
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikPhotoEffects
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikBrightness
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikActiveDLighting
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikNoiseReduction
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikPixelShiftNoiseReduction
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikDLightingHQ
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikAdaptivePaste
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikNewton
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikRotate
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikCrop
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

"""
import base64
import datetime
import logging
from xml.etree import ElementTree


__all__ = [
    "NikAdjustmentError",
    "NikBaseAdjustment",
    "NikColorShift",
    "NikDLightingHS",
    "NikWhiteBalance",
    "NikStraighten",
    "NikPictureControl",
    "NikQuickFixToneCurve",
    "NikGaussianBlur",
    "NikLEGeneral",
    "NikFishEye",
    "NikDehaze",
    "NikColorBalance",
    "NikFlare",
    "NikSkinTone",
    "NikVignette",
    "NikPerspective",
    "NikChrAb",
    "NikUnsharpMask",
    "NikColorBooster",
    "NikNXHistory",
    "NikSkinSoftening",
    "NikLevelsCurves",
    "NikRedEye",
    "NikDiffraction",
    "NikDistortion",
    "NikApplicationData",
    "NikLongChrAb",
    "NikExposureSettings",
    "NikLCH",
    "NikQuickFixContrast",
    "NikGrainNoise",
    "NikDustOff",
    "Niktransform",
    "NikSizeRes",
    "NikPhotoEffects",
    "NikBrightness",
    "NikActiveDLighting",
    "NikNoiseReduction",
    "NikPixelShiftNoiseReduction",
    "NikDLightingHQ",
    "NikAdaptivePaste",
    "NikNewton",
    "NikRotate",
    "NikCrop",
    "create_nine_edits"
]


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class NikAdjustmentError(Exception):
    """Base class for image's adjustment parser exceptions.

    Args:
        message: (optional) Human readable string describing the
            exception.

    Attributes:
        message: Human readable string describing the exception.
    """
    message: str | None
    def __init__(self, message: str | None = ""):
        self.message = message

    def __str__(self) -> str | None:
        return self.message


class NikBaseAdjustment:
    """Base class for Nikon image's adjustment class
    
    Args:
        element: XML element containing the metadata.

    Raises:
        NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
            details the error.

    Attributes:
        active : `True` indicate that the image's adjustments will be
            applied on the image associated to the sidecar files when
            opening in NX Studio.
        params: image's adjustment parameters as a dictionnary.
    """
    active: bool
    params: dict
    def __init__(self, element: ElementTree.Element):
        # Table of doers method for processing parameters
        self._doers = {
            "integer": self._set_param_integer,
            "double": self._set_param_double,
            "bool":self._set_param_bool,
            "Export": self._set_param_export,
            "Custom": self._set_param_custom,
            "points": self._set_param_points,
            "point": self._set_param_point,
            "data": self._set_param_data,
            "binary": self._set_param_binary,
            "map": self._set_param_map,
            "dateAndTime": self._set_param_dtstamp,
            "_default": self._set_default
        }
        self._element = element
        self.active = False
        self.params = {}

    def parse(self):
        """Parse the image adjustment XML element.

        This method parses an XML element as an image's adjustment
        block and populate attributes (:attr:`active` and :attr:`params`).

        The article named ":ref:`background_papers/inside_nksc:Inside
        Nikon Sidecar file`" details the data structure and tags used by
        Nikon.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        for child in self._element:
            match child.tag:
                case "active":
                    name, val = child.tag, child.text
                    if val is not None:
                        match val.lower():
                            case "false" | "true":
                                self.active = (val.lower() == "true")

                            case _:
                                raise NikAdjustmentError(
                                    f"Unsupported active value ({val})")
                    else:
                        raise NikAdjustmentError(
                            f"Unsupported active value ({val})")

                case "parameters":
                    self._set_params(child)

                case _:
                    raise NikAdjustmentError(
                        f"Unsupported tag value ({child.text})")

    def _set_params(self, element: ElementTree.Element):
        """Set image's adjustment parameters.

        This method parses an XML element as a image's adjustment
        parameters block and store it in the parameters' dictionary
        :attr:`params` according to its explicit or implicit type. As
        image's adjustment parameters are not documented (Nikon
        proprietary format), the method is permissive and not checks the
        data set.

        The article named ":ref:`background_papers/inside_nksc:Inside
        Nikon Sidecar file`" details the data structure and tags used by
        Nikon.

        Particular use cases


        Args:
            element: Element containing the parameter block.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        for child in element:
            if child.tag in self._doers:
                self._doers[child.tag](child)
            else:
                self._doers["_default"](child)

        _logger.debug(f"{self.__class__.__name__} adjustments parameters: "
                      f"{len(self.params)}")
        for k, v in self.params.items():
            _logger.debug(f"{self.__class__.__name__} adjustments parameters {k}={v}")

    def _set_param_integer(self, element: ElementTree.Element):
        """Set integer parameter.

        An ``integer`` may a decimal number or a boolean if its
        value is ``true`` or ``false``.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "name" in element.attrib:
            k, v = element.attrib["name"], element.text
            if v is not None:
                match v:
                    case "false" | "true":
                        self.params[k] = (v.lower() == "true")
                    case _:
                        self.params[k] = float(v)
            else:
                self.params[k] = None
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

    def _set_param_bool(self, element: ElementTree.Element):
        """Set boolean parameter.

        As the NineEdits XML format is not documented, some type may be
        overloaded (boolean and integer for exemple).

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "name" in element.attrib:
            k, v = element.attrib["name"], element.text
            if v is not None:
                match v:
                    case "false" | "true":
                        self.params[k] = (v.lower() == "true")
                    case _:
                        raise NikAdjustmentError(f"Parameters {k} is not "
                                                 f"a boolean ({v})")
            else:
                self.params[k] = None
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

    def _set_param_double(self, element: ElementTree.Element):
        """Set double parameter.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "name" in element.attrib:
            k, v = element.attrib["name"], element.text
            if v is not None:
                self.params[k] = float(v)
            else:
                self.params[k] = None
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

    def _set_param_data(self, element: ElementTree.Element):
        """Set data parameter.

        Data is an unspecified text string

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "id" in element.attrib:
            k, v = element.attrib["id"], element.text
            if v is not None:
                self.params[k] = v
            else:
                self.params[k] = None
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

    def _set_param_binary(self, element: ElementTree.Element):
        """Set binary parameter.

        Binary string encoded in base64 (seems similar to Export type
        parameters)

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "name" in element.attrib:
            k, v = element.attrib["name"], element.text
            if v is not None:
                self.params[k] = base64.b64decode(v)
            else:
                self.params[k] = None
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

    def _set_default(self, element: ElementTree.Element):
        """Default setter for parameter.

        Simple parameter is a simple tag, its type is guessed from its
        value. As the method is the default setter, it checks that the
        parameter is a simple one. If not a warning is logged.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        k, v = element.tag, element.text
        if "name" in element.attrib:
            name = element.attrib["name"]
            _logger.warning(f"{self.__class__.__name__}: {name} ({k}) "
                            f"parameter is not known - ignored")
        else:
            if v is not None:
                if v.isdecimal():
                    self.params[k] = int(v)
                else:
                    self.params[k] = v
            else:
                _logger.warning(f"{self.__class__.__name__}: Empty or null "
                                f"parameter ({k})")
                self.params[k] = None

    def _set_param_dtstamp(self, element: ElementTree.Element):
        """Set datetime stamp parameter.

        ``dateAndTime`` parameter is a date and a time expressed in a
        block with ``year``, ``month``, ``day``, ``hour``, ``minute``
        and ``second`` xml tag. The date 1900-1-1 00:00:00 seems to be
        default value.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        year = 1900
        month = 1
        day = 1
        hour = 0
        minute = 0
        second = 0
        for child in element:
            k, v = child.tag, child.text
            match k:
                case "year":
                    if v is not None:
                        year = int(v)

                case "month":
                    if v is not None:
                        month = int(v)

                case "day":
                    if v is not None:
                        day = int(v)

                case "hour":
                    if v is not None:
                        hour = int(v)

                case "minute":
                    if v is not None:
                        minute = int(v)

                case "second":
                    if v is not None:
                        second = int(v)

                case _:
                    raise NikAdjustmentError(
                        f"Unexpected tag for dateAndTime parameter: {k}")

            self.params["dateAndTime"] \
                = datetime.datetime(year, month, day, hour, minute, second)

    def _set_param_export(self, element: ElementTree.Element):
        """Set export parameter.

        Export parameter is a binary string expressed as a set of two elements:
        ``ExportData`` and ``ExportDataSize``. ``ExportData`` is a binary
        string encoded in Base64. ``ExportDataSize`` is the length of the
        **encoded** string.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        data = None
        data_size = 0
        rawdata_size = 0
        for child in element:
            k, v = child.tag, child.text
            match k:
                case "ExportData":
                    if v is not None:
                        data = base64.b64decode(v)
                        rawdata_size = len(v)

                case "ExportDataSize":
                    if v is not None:
                        data_size = int(v)

                case _:
                    raise NikAdjustmentError(
                        f"Unexpected tag for Export parameter: {k}")

        if data is not None:
            if rawdata_size != data_size:
                raise NikAdjustmentError(
                    f"Export Data have a wrong size: actual {len(data)}, "
                    f"expected {data_size}")
            self.params["Export"] = data

    def _set_param_custom(self, element: ElementTree.Element):
        """Set custom parameter.

        Custom parameter is a binary string expressed as a set of two elements:
        ``CustomData`` and ``CustomDataSize``. ``CustomData`` is a binary
        string encoded in Base64. ``CustomDataSize`` is the length of the
        **encoded** string.

        This parameter is similar to Export parameter.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        data = None
        data_size = 0
        rawdata_size = 0
        for child in element:
            k, v = child.tag, child.text
            match k:
                case "CustomData":
                    if v is not None:
                        data = base64.b64decode(v)
                        rawdata_size = len(v)

                case "CustomDataSize":
                    if v is not None:
                        data_size = int(v)

                case _:
                    raise NikAdjustmentError(
                        f"Unexpected tag for Custom parameter: {k}")

        if data is not None:
            if rawdata_size != data_size:
                raise NikAdjustmentError(
                    f"Custom Data have a wrong size: actual {len(data)}, "
                    f"expected {data_size}")
            self.params["Custom"] = data

    def _set_param_map(self, element: ElementTree.Element):
        """Set map parameter.

        Map parameter is a binary string expressed as a set of two elements:
        ``mapdata`` and ``mapsize``. ``mapdata`` is a binary
        string encoded in Base64. ``mapsize`` is the length of the
        **encoded** string. This parameter contains data used by the dust
        off adjustment.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        map = None
        map_size = 0
        rawdata_size = 0
        for child in element:
            k, v = child.tag, child.text
            match k:
                case "mapData":
                    if v is not None:
                        map = base64.b64decode(v)
                        rawdata_size = len(v)

                case "mapSize":
                    if v is not None:
                        map_size = int(v)

                case _:
                    raise NikAdjustmentError(
                        f"Unexpected tag for map parameter: {k}")

        if map is not None:
            if rawdata_size != map_size:
                raise NikAdjustmentError(
                    f"map have a wrong size: actual {rawdata_size}, "
                    f"expected {map_size}")
            self.params["map"] = map

    def _set_param_points(self, element: ElementTree.Element):
        """Set points parameter.

        Points parameter is a set of 2D coordinates (``x`` and ``y``).

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        points = None
        if "name" in element.attrib:
            name = element.attrib["name"]
            for child in element:
                k, v = child.tag, child.attrib
                match k:
                    case "pointOfPoints":
                        if points is None:
                            points = []
                        point = {"x": int(v["x"]), "y": int(v["y"])}
                        points.append(point)

                    case _:
                        raise NikAdjustmentError(
                            f"Unexpected tag for points parameter: {k}")
        else:
            raise NikAdjustmentError(f"Unnamed parameters")

        self.params[name] = points

    def _set_param_point(self, element: ElementTree.Element):
        """Set point parameter.

        Point parameter is a 2D coordinates (``x`` and ``y``). Please note
        that data structure is not the same than points.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        point = None
        if "name" in element.attrib:
            name = element.attrib["name"]
            point = {
                "x": int(element.attrib["x"]),
                "y": int(element.attrib["y"])
            }

        else:
            raise NikAdjustmentError(f"Unnamed parameters")

        self.params[name] = point

    def __repr__(self):
        """Return a printable string representation.

        The representation is the name of the image's adjustment (class
        name) and if the adjustment is active or not.
        """
        return f"{self.__class__.__name__} object: active={self.active}"

    def is_dt_ready(self):
        """Return if this image's adjustment may be used in Darktable.

        The ....

        Returns:
            `True` if this image's adjustment may be used in Darktable.
        """
        raise NotImplementedError

    def get_dt_module(self):
        """Return the image's adjustment parameters for Darktable.

        The ....

        Returns:
            /todo something .
        """
        raise NotImplementedError


class NikColorShift(NikBaseAdjustment):
    pass
    

class NikDLightingHS(NikBaseAdjustment):
    pass


class NikWhiteBalance(NikBaseAdjustment):
    pass
    

class NikStraighten(NikBaseAdjustment):
    pass
    

class NikPictureControl(NikBaseAdjustment):
    """Picture control image's adjustment class

    Picture control (nikon::PictureControl) adjusts the SDR tone range
    of RAW pictures.

    The article named
    ":ref:`background_papers/nikon_picturecontrol:Inside nikon::PictureControl`"
    details parameters and especially ``Export`` parameter expressed as
    an obscure data. To avoid parameters overwritten, the setting names are
    prefixed with "PC." in the dictionary :attr:`params` (example: setting
    named "Sharpening" have "PC.Sharpening" as key.

    This class override the :meth:`NikBaseAdjustment._set_param_export`
    method to parse the 'Export' parameter.

    Args:
        element: XML element containing the metadata.

    Raises:
        NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
            details the error.
    """
    #: Filter effect mapping. Names are used instead of value to have a
    #: human-readable structure, and these are the ones used by Nikon
    #: Studio.
    FILTER_EFFECT = ["none", "yellow", "orange", "red", "green"]
    #: Toning mapping. Names are used instead of value to have a
    #: human-readable structure, and these are the ones used by Nikon
    #: Studio.
    TONING = ["B&W", "sepia", "cyanotype", "red", "yellow", "green",
              "blue-green", "blue", "purple-blue", "reddish-purple"]
    #: Customization mapping. Names are used instead of value to have a
    #: human-readable structure, and these are the ones used by Nikon
    #: Studio.
    CUSTOMIZATION = {
        0x00: "Built-in",
        0x01: "Quick Adjust",
        0x02: "Advanced settings",
        0x0100: "Advanced settings",
        0x0200: "Sharpening settings"
    }
    #: Customization mapping. Names are used instead of value to have a
    #: human-readable structure, and these are the ones used by Nikon
    #: Studio.
    PCID = {
        0x0001: "SD", # STANDARD
        0x03C2: "NL", # NEUTRAL
        0x00C3: "VI", # VIVID
        0x064D: "MC", # MONOCHROME
        0x0486: "PT", # PORTRAIT
        0x04C7: "LS", # LANDSCAPE
        0x02CF: "A",  # AUTO
        0x0654: "FM", # FLAT MONOCHROME
        0x6655: "DM", # DEEPTONE MONOCHROME
        0x0493: "RP", # RICH TONE PORTAIT
        0x028E: "FL", # FLAT
        0x0020: "FC", # FLEXIBLE COLOR
        0x0801: "01", # [01] DREAM
        0x0802: "02", # [02] MORNING
        0x0803: "03", # [03] POP
        0x0804: "04", # [04] SUNDAY
        0x0805: "05", # [05]SOMBER
        0x0806: "06", # [06] DRAMATIC
        0x0807: "07", # [07] SILENCE
        0x0808: "08", # [08] BLEACHED
        0x0809: "09", # [09] MELANCHOLIC
        0x080A: "10", # [10] PURE
        0x080B: "11", # [11] DENIM
        0x080C: "12", # [12] TOY
        0x080D: "13", # [13] SEPIA
        0x080E: "14", # [14] BLUE
        0x080F: "15", # [15] RED
        0x0810: "16", # [16] PINK
        0x0811: "17", # [17] CHARCOAL
        0x0812: "18", # [18] GRAPHITE
        0x0813: "19", # [19] BINARY
        0x0814: "20", # [20] CARBON
    }
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        # override the specific handler
        doers = {
            "Export": self._set_param_export
        }
        self._doers.update(doers)

        # Table of doers methods for processing picture control dataset
        self._pc_doers = {
            0x00000001: ("PC.CC", self._parse_camera_compatible),
            0x00000002: ("PC.CustomToneCurve", self._set_opaque),
            0x00000100: ("PC.Version", self._set_version),
            0x00000200: ("PC.Name", self._set_string),
            0x00000300: ("PC.Id", self._set_id),
            0x00000400: ("PC.CustomizationLevel", self._set_customization),
            0x00000500: ("PC.Undefined#0500", self._set_value),
            0x00000600: ("PC.Sharpening", self._set_value),
            0x00000700: ("PC.Clarity", self._set_value),
            0x00000800: ("PC.Contrast", self._set_value),
            0x00000900: ("PC.Brightness", self._set_value),
            0x00000A00: ("PC.Saturation", self._set_value),
            0x00000B00: ("PC.Hue", self._set_value),
            0x00000C00: ("PC.FilterEffect", self._set_filter_effect),
            0x00000D00: ("PC.Toning", self._set_toning),
            0x00000E00: ("PC.AdjustSaturation", self._set_value),
            0x00000F00: ("PC.AutoSharpening", self._set_value),
            0x00001000: ("PC.AutoClarity", self._set_value),
            0x00001100: ("PC.AutoContrast", self._set_value),
            0x00001200: ("PC.AutoSaturation", self._set_value),
            0x00001300: ("PC.AutoMidRangeSharpening", self._set_value),
            0x00001400: ("PC.QuickSharp", self._set_value),
            0x00001500: ("PC.EffectLevel",  self._set_value),
            0x00001600: ("PC.MidRangeSharpening",  self._set_value),
            0x00001700: ("PC.Undefined#1700", self._set_value),
            0x00001800: ("PC.Undefined#1800", self._set_value),
            0x00001900: ("PC.FC.Contrast", self._set_value),
            0x00001A00: ("PC.FC.Highlights",  self._set_value),
            0x00001B00: ("PC.FC.Shadows ", self._set_value),
            0x00001C00: ("PC.FC.WhiteLevel ",self._set_value),
            0x00001D00: ("PC.FC.BlackLevel", self._set_value),
            0x00001E00: ("PC.FC.Saturation", self._set_value),
            0x00001F00: ("PC.FC.ColorBlender", self._set_opaque),
            0x00002000: ("PC.FC.ColorGrading ", self._set_opaque),
            0x00010100: ("PC.Comment",  self._set_string)
        }
        # Layout of the camera compatible dataset (id: 0x00000001). The
        # layout is a tuple: offset, length, handler.
        self._pccc_layout = [
            ( 0,  4, ("PC.Version", self._set_version)),
            ( 4, 20, ("PC.Name", self._set_string)),
            (24,  2, ("PC.Id", self._set_id)),
            (26,  1, ("PC.CustomizationLevel", self._set_customization)),
            (27,  1, ("PC.QuickAdjust", self._set_value)),
            (28,  1, ("PC.Sharpening", self._set_value)),
            (29,  1, ("PC.Contrast", self._set_value)),
            (30,  1, ("PC.Brightness", self._set_value)),
            (31,  1, ("PC.Saturation", self._set_value)),
            (32,  1, ("PC.Hue", self._set_value)),
            (33,  1, ("PC.FilterEffect", self._set_filter_effect)),
            (34,  1, ("PC.Toning", self._set_toning)),
            (35,  1, ("PC.AdjustSaturation", self._set_value))
        ]
        self._pc_params = {}
        self._undefined  = 0

    def _set_param_export(self, element: ElementTree.Element):
        """Set export parameter.

        Parses the 'Export' parameter and store the processed settings in
        the dictionary :attr:`params`. The original 'Export' entry is
        removed from dictionary :attr:`NikBaseAdjustment.params`.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        super()._set_param_export(element)
        data = self.params["Export"]

        # Check the record identifier
        record = str(data[0:4], encoding='ASCII').rstrip("\x00")
        data = data[4:] # Remove processed field
        if record != 'NCP':
            raise NikAdjustmentError(f"Unsupported Picture control ({record})")

        # Process datasets
        dset = int.from_bytes(data[0:4])
        while dset != 0x00000000:
            dlen = int.from_bytes(data[4:8])
            dval = data[8: 8+dlen]
            if dset not in self._pc_doers:
                _logger.warning(f"{self.__class__.__name__}: DataSet is not "
                                f"known ({dset:08x}) - ignored")
            else:
                key, handler = self._pc_doers[dset]
                _logger.debug(f"{self.__class__.__name__}: Processing "
                              f"DataSet {dset:08x} ({key}): {dval}")
                handler(key, dval)
            # Remove processed dataset and retrieve the next one
            data = data[8+dlen:]
            dset = int.from_bytes(data[0:4])

        self.params.update(self._pc_params)
        # Clean-up
        self._pc_params = None
        # todo: Remove 'Export' entry after debug
        # del self.params["Export"]

    def _parse_camera_compatible(self, key: str, data: bytes):
        """Process 'camera compatible' dataset.

        This method parses the 'Camera compatible' dataset (id: 0x00000001).
        This dataset is a binary structure and parsing uses the layout
        expressed in instance attribute '_pccc_layout'. See article named
        ":ref:`background_papers/nikon_picturecontrol:Camera compatible`"
        for more details.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the dataset expressed as a binary string.
        """
        for offset, length, doer in self._pccc_layout:
            dval = data[offset: offset + length]
            key, handler = doer
            _logger.debug(f"{self.__class__.__name__}: Processing "
                          f"Field offset {offset:02d} ({key}): {dval}")
            handler(key, dval)

    def _set_version(self, key: str, data: bytes):
        """Process version setting.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._pc_params[key] = str(data, encoding="ASCII")

    def _set_value(self, key: str, data: bytes) -> None :
        """Process setting expressed as a value.

        Parameters values are encoded on one or two bytes and may be
        expressed as an integer or a decimal number. See article named
        ":ref:`background_papers/nikon_picturecontrol:Parameters encoding`"
        for more details.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._pc_params[key] = None
        bv = 0xff
        match len(data):
            case 1:
                bv = data[0]
                div = 0

            case 2:
                bv = data[0]
                div = data[1]

            case _:
                raise NikAdjustmentError(
                    f"Unsupported length value: actual '{len(data)}', "
                    f"expected <2")

        match bv:
            case 0xff:
                self._pc_params[key] = None

            case 0x00:
                self._pc_params[key] = "Auto"

            case _:
                self._pc_params[key] = (bv - 0x80)
                if div != 0: # Apply subdivision
                    self._pc_params[key] = self._pc_params[key] / div

    def _set_string(self, key: str, data: bytes) -> None :
        """Process setting expressed as a string.

        String are null terminated ASCII string.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._pc_params[key] = str(data, encoding="ASCII").rstrip("\x00")

    def _set_opaque(self, key: str, data: bytes):
        """Process setting expressed as an opaque data.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._pc_params[key] = data

    def _set_id(self, key: str, data: bytes) -> None :
        """Process id setting.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        v = int.from_bytes(data)
        self._pc_params[key] = int.from_bytes(data)
        if v in self.PCID:
            self._pc_params[key] = self.PCID[v]
        else:
            raise NikAdjustmentError(f"Unsupported picture control Id: "
                                     f"actual ({v})")

    def _set_customization(self, key: str, data: bytes):
        """Process customization level setting.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        v = int.from_bytes(data)
        if v in self.CUSTOMIZATION:
            self._pc_params[key] = self.CUSTOMIZATION[v]
        else:
            raise NikAdjustmentError(f"Unsupported customization: actual ({v})")

    def _set_filter_effect(self, key: str, data: bytes):
        """Process filter effect setting.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._set_value(key, data)
        v = self._pc_params[key]
        # Substitute the numeric value by a human-readable string
        if v is not None:
            if v in range(len(self.FILTER_EFFECT)):
                self._pc_params[key] = self.FILTER_EFFECT[v]
            else:
                raise NikAdjustmentError(
                    f"Unsupported filter effect: actual ({v}), "
                    f"expected <{len(self.FILTER_EFFECT)}")

    def _set_toning(self, key: str, data: bytes):
        """Process toning setting.

        Args:
            key: Name of the parameter in :attr:`NikBaseAdjustment.params`
                dictionary.
            data: Value of the parameter expressed as a binary string.
        """
        self._set_value(key, data)
        v = self._pc_params[key]
        # Substitute the numeric value by a human-readable string
        if v is not None:
            if v in range(len(self.TONING)):
                self._pc_params[key] = self.TONING[v]
            else:
                raise NikAdjustmentError(
                    f"Unsupported toning: actual ({v}), "
                    f"expected <{len(self.TONING)}")


class NikQuickFixToneCurve(NikBaseAdjustment):
    pass
    

class NikGaussianBlur(NikBaseAdjustment):
    pass
    

class NikLEGeneral(NikBaseAdjustment):
    pass
    

class NikFishEye(NikBaseAdjustment):
    pass
    

class NikDehaze(NikBaseAdjustment):
    pass
    

class NikColorBalance(NikBaseAdjustment):
    pass
    

class NikFlare(NikBaseAdjustment):
    pass
        

class NikSkinTone(NikBaseAdjustment):
    pass


class NikVignette(NikBaseAdjustment):
    pass
    

class NikPerspective(NikBaseAdjustment):
    pass
    

class NikChrAb(NikBaseAdjustment):
    pass
    

class NikUnsharpMask(NikBaseAdjustment):
    pass
    

class NikColorBooster(NikBaseAdjustment):
    pass
    

class NikNXHistory(NikBaseAdjustment):
    """NXHistory image's adjustment class

     NXHistory (Nikon::NXHistory) is not strictly an image adjustment, it
     is an ordered list whose entries are tagged with ``historystep``.
     Each entry (aka. step) is an unitary image adjustment to apply to
     the image. For example, cropping an image should be done after image
     processing modifying the image size as lens correction or perspective
     controls). The list is stored in a dictionary with name
     ``historystep:XXX`` as key where XXX is the step index (from 1 to 999).

     The step parameters are in a dictionary with parameter name as key.
     The value type is set according to its explicit or implicit type.

     Args:
         element: XML element containing the metadata.

     Raises:
         NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
             details the error.
     """
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        # Add the specific handler
        doers = {
            "historystep": self._set_param_history_step
        }
        self._doers.update(doers)

        # Table of doers method for processing historystep subparameters
        self._hs_doers = {
            "filter": self._set_hs_filter,
            "adjustmentData": self._set_hs_adjustment_data,
            "_default": self._set_hs_default
        }
        self._index = 1
        self._hs_params = {}

    def _set_param_history_step(self, element: ElementTree.Element):
            """Set history step parameter.

            Args:
                element: Element containing the parameter.

            Raises:
                NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                    details the error.
            """
            self._hs_params = {}
            for child in element:
                if child.tag in self._hs_doers:
                    self._hs_doers[child.tag](child)
                else:
                    self._hs_doers["_default"](child)

            self.params[f"{element.tag}:{self._index:03d}"] = self._hs_params

            _logger.debug(f"{self.__class__.__name__} history step "
                          f"#{self._index} parameters: {len(self._hs_params)}")
            for k, v in self._hs_params.items():
                _logger.debug(f"{self.__class__.__name__} history step "
                              f"parameters {k}={v}")
            self._index += 1

    def _set_hs_filter(self, element: ElementTree.Element):
        """Set history step filter parameter.

        This parameter is the image adjustment to apply.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        if "id" in element.attrib:
            k = element.attrib["id"]
            if k in _MAP_ADJUSTMENT_ID:
                self._hs_params[k] = _MAP_ADJUSTMENT_ID[k](element)
                self._hs_params[k].parse()
            else:
                _logger.warning(f"{self.__class__.__name__}: "
                                f"Unknown adjustment: {k}")
        else:
             raise NikAdjustmentError(f"Unnamed filter")

    def _set_hs_adjustment_data(self, element: ElementTree.Element):
        """Set history step adjustmentData parameter.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        for child in element:
            if child.tag == "data":
                if "id" in child.attrib:
                    k, v = child.attrib["id"], child.text
                    if v is not None:
                        match v.lower():
                            case "false" | "true":
                                self._hs_params[k] = (v.lower() == "true")

                            case _:
                                self._hs_params[k] = v
                    else:
                        self._hs_params[k] = None
                else:
                    raise NikAdjustmentError(f"Unnamed parameters")
            else:
                raise NikAdjustmentError(
                    f"Unexpected tag for adjustmentData parameter: {child.tag}")

    def _set_hs_default(self, element: ElementTree.Element):
        """Default setter for history step parameter.

        Simple parameter is a simple tag, its type is guessed from its
        value.

        Args:
            element: Element containing the parameter.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        k, v = element.tag, element.text
        if v is not None:
            match v.lower():
                case "false" | "true":
                    self._hs_params[k] = (v.lower() == "true")

                case _:
                    if v.isdecimal():
                        self._hs_params[k] = int(v)
                    else:
                        self._hs_params[k] = v
        else:
            _logger.warning(f"{self.__class__.__name__}: Empty or null "
                            f"parameter ({k})")
            self._hs_params[k] = None

class NikSkinSoftening(NikBaseAdjustment):
    pass
    

class NikLevelsCurves(NikBaseAdjustment):
    pass
    

class NikRedEye(NikBaseAdjustment):
    pass
    

class NikDiffraction(NikBaseAdjustment):
    pass


class NikDistortion(NikBaseAdjustment):
    pass
    

class NikApplicationData(NikBaseAdjustment):
    pass
    

class NikLongChrAb(NikBaseAdjustment):
    pass
    

class NikExposureSettings(NikBaseAdjustment):
    pass
    

class NikLCH(NikBaseAdjustment):
    pass
    

class NikQuickFixContrast(NikBaseAdjustment):
    pass
    

class NikGrainNoise(NikBaseAdjustment):
    pass
    

class NikDustOff(NikBaseAdjustment):
    pass


class Niktransform(NikBaseAdjustment):
    pass
    

class NikSizeRes(NikBaseAdjustment):
    pass
    

class NikPhotoEffects(NikBaseAdjustment):
    pass
    

class NikBrightness(NikBaseAdjustment):
    pass


class NikActiveDLighting(NikBaseAdjustment):
    pass


class NikNoiseReduction(NikBaseAdjustment):
    pass


class NikPixelShiftNoiseReduction(NikBaseAdjustment):
    pass


class NikDLightingHQ(NikBaseAdjustment):
    pass

class NikAdaptivePaste(NikBaseAdjustment):
    pass

class NikNewton(NikBaseAdjustment):
    pass

class NikRotate(NikBaseAdjustment):
    pass

class NikCrop(NikBaseAdjustment):
    pass

def create_nine_edits(element: ElementTree.Element) -> dict:
    """Return the list of image adjustments

        Args:
            element: XML element containing the ``NineEdits`` property.

        Return:
            Dictionary of image adjustments with the image adjustment name
            as key. The value is an instance of the image adjustment
            class (:class:`NikWhiteBalance`, :class:`NikPictureControl`
            or :class:`NikBaseAdjustment` for example). See class
            documentation to have more details.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
    """
    adjustments = {}
    if element.tag == "userData":
        for child in element:
            match child.tag:
                case "filter":
                    if "id" in child.attrib:
                        k = child.attrib["id"]
                        if k in _MAP_ADJUSTMENT_ID:
                            adjustments[k] = _MAP_ADJUSTMENT_ID[k](child)
                            adjustments[k].parse()
                        else:
                            _logger.warning(f"Unknown adjustment: {k}")
                    else:
                        raise NikAdjustmentError(f"Unnamed filter")

                case _:
                    raise NikAdjustmentError(
                        f"Unsupported tag value ({child.text})")
    else:
        raise NikAdjustmentError(
            f"NineEdit Wrong header block: actual {element.tag}, "
            f"expected userData")

    for k, v in adjustments.items():
        _logger.debug(f"NineEdits adjustments parameters {k}={v}")

    return adjustments


#: Mapping Nikon adjustment name (``filter id``) with the adjustment class
_MAP_ADJUSTMENT_ID = {
    "nikon::ColorShift": NikColorShift,
    "nikon::DLightingHS": NikDLightingHS,
    "nikon::WhiteBalance": NikWhiteBalance,
    "nik::Straighten": NikStraighten,
    "nikon::PictureControl": NikPictureControl,
    "nikon::QuickFixToneCurve": NikQuickFixToneCurve,
    "nik::GaussianBlur": NikGaussianBlur,
    "nikon::LEGeneral": NikLEGeneral,
    "Nikon::FishEye": NikFishEye,
    "nikon::Dehaze": NikDehaze,
    "nikon::ColorBalance": NikColorBalance,
    "nikon::Flare": NikFlare,
    "nikon::SkinTone": NikSkinTone,
    "nikon::Vignette": NikVignette,
    "nikon::Perspective": NikPerspective,
    "nikon::ChrAb": NikChrAb,
    "nikon::UnsharpMask": NikUnsharpMask,
    "nikon::ColorBooster": NikColorBooster,
    "nikon::NXHistory": NikNXHistory,
    "nikon::SkinSoftening": NikSkinSoftening,
    "nik::LevelsCurves": NikLevelsCurves,
    "nikon::RedEye": NikRedEye,
    "nikon::Diffraction": NikDiffraction,
    "nikon::Distortion": NikDistortion,
    "nikon::ApplicationData": NikApplicationData,
    "nikon::LongChrAb": NikLongChrAb,
    "nikon::ExposureSettings": NikExposureSettings,
    "nik::LCH": NikLCH,
    "nikon::QuickFixContrast": NikQuickFixContrast,
    "nik::GrainNoise": NikGrainNoise,
    "nikon::DustOff": NikDustOff,
    "nikon::transform": Niktransform,
    "nikon::SizeRes": NikSizeRes,
    "nikon::PhotoEffects": NikPhotoEffects,
    "nikon::Brightness": NikBrightness,
    "nikon::ActiveDLighting": NikActiveDLighting,
    "nikon::NoiseReduction": NikNoiseReduction,
    "nikon::PixelShiftNoiseReduction": NikPixelShiftNoiseReduction,
    "nikon::DLightingHQ": NikDLightingHQ,
    "nik::AdaptivePaste": NikAdaptivePaste,
    "nik::Newton": NikNewton,
    "nik::Rotate": NikRotate,
    "nik::Crop": NikCrop,
}
