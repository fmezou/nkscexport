"""Handle Nikon sidecar files (read only)

The `sidecar.nikon` module implements handlers for the Nikon sidecar
file. The article named :ref:`background_papers/inside_nksc:Inside Nikon
Sidecar file` details the data structure and tags used by Nikon.

Each set of XMP properties (``sdc``, ``ast``, ``nine``) have its own
handlers to process that set. The :class:`NikonSideCar` is the main class
managing a Nikon sidecar file.

Using ``nikon``
---------------

For this short tutorial, we have a sidecar file named 'full_XMP.IPTC.NEF.nksc'.
We create an instance of :class:`NikonSideCar`).

>>> from darkbridge.sidecar.nikon import NikonSideCar
>>> from pathlib import Path
>>> path = Path('images_samples/NKSC_PARAM/full_XMP.IPTC.NEF.nksc')
>>> nksc = NikonSideCar(path)

We can parse the Nikon sidecar file to extract metadata.

>>> nksc.parse()

We can simply access th some key properties via methods as
:meth:`NikonSideCar.get_rating` or :meth:`NikonSideCar.is_geotagged`. See
:class:`NikonSideCar` for an exhaustive list of methods.

>>> nksc.get_rating()
5
>>> nksc.get_label()
'Rose'
>>> nksc.is_geotagged()
True

We can list all the metadata parsed from the sidecar files. The following
output has been truncated to fit in the page.

>>> for k, v in nksc.metadata.items():
...     print(f" * {k}: {v}")
 * appname: NX Studio
 * appversion: 1.10 W
 * xmp:Rating: 5
 * xmp:Label: Rose
 * dc:title: [Description] Titre
 * dc:subject: ['Mot-clé #1', 'Mot-clé #2', 'Mot-clé #3']
 ...
 * Iptc4xmpExt:Event: ['[Description] Evénement']

We can list all the image adjustement stored in the sidecar file. The
following output has been truncated to fit in the page.

>>> for k, v in nksc.processing.items():
...     print(f" * {k}: Active={v.active}")
...     for n, p in v.params.items():
...         print(f"     * {n}: {p} ")
 * nikon::ColorShift: Active=False
     * colorCorrection: 0
 * nikon::PictureControl: Active=True
     * Export: b'NCP\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00$0100STANDARD...'
     * SelectedPictureControl: 0
     * AutoContrast: 255
     * AutoSaturation: 255
     * SelectedPictureControlVersion2: 0
     * SavedPicConProcess: 1
     * PictureControl: 0
     ...

We can show the geolocation stored in the side file. The :attr:`geolocation`
attribute is a :class:`NikonGPSProperties`. As this class have a
`object.__repr__` method, only the GPS coordinates are printed. All GPS
properties are in :attr:`NikonGPSProperties.props`. See
:class:`NikonGPSProperties` for a more detailled view of geolocation
properties.

>>> nksc.geolocation
lat: 48.13672 (N) long: 1.64114 (W)
>>> nksc.geolocation.props['GPSLatitude']
48.13672002447976

Reference
---------

Exception
^^^^^^^^^

.. autoexception:: NikonError
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

Sidecar object
^^^^^^^^^^^^^^

.. autoclass:: NikonSideCar
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

Properties objects
^^^^^^^^^^^^^^^^^^
.. autoclass:: NikonSDCProperties
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikonAsteroidProperties
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikonNineProperties
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikonGPSProperties
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikonXMPProperty
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

.. autoclass:: NikonXMPDescriptions
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:

Constants
^^^^^^^^^

.. autodata:: NIKON_SUPPORTED_FORMAT

.. autodata:: NIKON_NKSC_SUBFOLDER

.. autodata:: NIKON_NKSC_EXT

.. autodata:: NIKON_LABEL_MAP

"""
import base64
import logging
import datetime as dt
from pathlib import Path
from xml.etree import ElementTree

from darkbridge.library.ieee754 import IEEE754
from darkbridge.library.namespace import NameSpace
from darkbridge.sidecar.nik_adjustment import create_nine_edits


__all__ = [
    "NikonError",
    "NikonSideCar",
    "NikonSDCProperties",
    "NikonAsteroidProperties",
    "NikonNineProperties",
    "NikonGPSProperties",
    "NikonXMPProperty",
    "NikonXMPDescriptions",
    "NIKON_SUPPORTED_FORMAT",
    "NIKON_NKSC_SUBFOLDER",
    "NIKON_NKSC_EXT",
    "NIKON_LABEL_MAP"
]


#: Mapping between Nikon Label and XMP label expressed as a text. This
#: table is based on default value and do not consider any customization.
#: See Nikon, `[Labels] <https://nikonimglib.com/nxstdo/onlinehelp/en/
#: labels_76.html>`_, Options > [Labels]
NIKON_LABEL_MAP = {
    "1":"Red",
    "2":"Orange",
    "3":"Yellow",
    "4":"Green",
    "5":"Cyan",
    "6":"Blue",
    "7":"Purple",
    "8":"Magenta",
    "9":"Pink",
    "0":"(Aucune)",
}

#: File extensions of supported image files.
NIKON_SUPPORTED_FORMAT = [
    ".nef", ".nrw",
    ".jpg", ".jpeg",
    ".tif", ".tiff",
    ".hif",
    ".nefx",
    ".mpo"
]

#: Subfolder storing the Nikon sidecar files.
NIKON_NKSC_SUBFOLDER = "NKSC_PARAM"

#: File extension of Nikon sidecar files.
NIKON_NKSC_EXT = ".nksc"

#: XML Namespaces used in sidecar file and ``XMLPackets`` property.
_NS = NameSpace(
        {
            # Namespaces used in XMP description block in sidecar files
            "x": "adobe:ns:meta/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "sdc": "http://ns.nikon.com/sdc/1.0/",
            "ast": "http://ns.nikon.com/asteroid/1.0/",
            "astype": "http://ns.nikon.com/asteroid/Types/1.0/",
            "nine": "http://ns.nikon.com/nine/1.0/",

            # Namespaces used in XML Packet (XMP Metadata description block)
            "dc": "http://purl.org/dc/elements/1.1/",
            "photoshop": "http://ns.adobe.com/photoshop/1.0/",
            "Iptc4xmpCore": "http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/",
            "xmpRights": "http://ns.adobe.com/xap/1.0/rights/",
            "xmp": "http://ns.adobe.com/xap/1.0/",
            "MicrosoftPhoto": "http://ns.microsoft.com/photo/1.0/",
            "Iptc4xmpExt": "http://iptc.org/std/Iptc4xmpExt/2008-02-29/"
        }
    )


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class NikonError(Exception):
    """Base class for sidecar parser exceptions.

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


class NikonGPSProperties:
    """Nikon GPS properties container.

    This class parse a sidecar file and extract ``ast`` tags (namespace
    'http://ns.nikon.com/asteroid/1.0/') related to GPS Information.
    The properties read are copied into the attribute :attr:`props`
    which can contain the following entries:

    * ``GPSVersionID``: The version of GPS information.
    * ``GPSLatitudeRef``: Whether the latitude is north (``N``) or south
      (``S``).
    * ``GPSLatitude``: The latitude, expressed in decimal degrees.
    * ``GPSLongitudeRef``: Whether the longitude is east (``E``) or west
      (``W``).
    * ``GPSLongitude``: The longitude, expressed in decimal degrees.
    * ``GPSAltitudeRef``: The altitude used as the reference altitude in
      meters.
    * ``GPSAltitude``: The altitude based on the reference in
      ``GPSAltitudeRef`` in meters.
    * ``GPSDateTimeStamp``: The date and time, in UTC (Coordinated
      Universal Time).
    * ``GPSStatus``: The status of the GPS receiver when the image is
      recorded.

      * ``A`` measurement is in progress
      * ``V`` measurement interrupted

    * ``GPSProcessingMethod``: The name of the method used for location
      finding (``GPS``, ``CELLID``, ``MANUAL``).
    * ``GPSMapDatum``: The geodetic survey data used by the GPS receiver.
      ``WGS-84`` is used in most cases.
    * ``GPSSpeedRef``: The unit used to express the ``GPSSpeed`` property.

      * ``K`` kilometers per hour
      * ``M`` miles per hour
      * ``N`` knots

    * ``GPSSpeed``: The speed of GPS receiver movement.
    * ``GPSImgDirectionRef``: The reference for giving the direction of
      the image when it is captured.

      * ``T`` true direction
      * ``M`` magnetic direction

    * ``GPSImgDirection``: The direction of the image when it was captured.
      The range of values is from 0.00 to 359.99.

    Note:
        Others GPS properties are ignored.

    This class can be used in a formatted string and returns the latitude
    and longitude.

    The article named :ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file` details the data structure and tags used by Nikon. In
    a nutshell, Nikon seems to have using DICOM specification (see
    :ref:`background_papers/inside_geoloc:GPSAttributes`).

    Raises:
        ValueError: argument has the right type but an
            inappropriate value.

    Attributes:
        props: Dictionary of properties of the GPS location.
    """
    props: dict
    def __init__(self):
        # Table of doers method for processing properties
        self._doers = {
            "ast:GPSVersionID": self._set_version,
            "ast:GPSLatitudeRef": self._set_latitude_ref,
            "ast:GPSLatitude": self._set_latitude,
            "ast:GPSLongitudeRef": self._set_longitude_ref,
            "ast:GPSLongitude": self._set_longitude,
            "ast:GPSAltitudeRef": self._set_altitude_ref,
            "ast:GPSAltitude": self._set_altitude,
            "ast:GPSTimeStamp": self._set_timestamp,
            "ast:GPSDateStamp": self._set_datestamp,
            "ast:GPSStatus": self._set_status,
            "ast:GPSMapDatum": self._set_map_datum,
            "ast:GPSProcessingMethod": self._set_processing,
            "ast:GPSSpeedRef": self._set_speed_ref,
            "ast:GPSSpeed": self._set_speed,
            "ast:GPSImgDirectionRef": self._set_img_direction_ref,
            "ast:GPSImgDirection": self._set_img_direction,
            "ast:GPSDestBearingRef": self._ignore_bearing,
            "ast:GPSDestBearing": self._ignore_bearing,
        }
        self.props = {}

    def get_xmp_props(self):
        """Returns the supported properties

        This method provides the list of the supported XMP properties to
        populate the attribute classes.

        Returns:
            list: List of the supported properties. The property names
            are those of the XMP properties expressed in a short form
            (i.e. ``prefix:tag``).
        """
        return self._doers.keys()

    def set_attr(self, xmp_property: NikonXMPProperty):
        """Set the GPS attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
       """
        if xmp_property.name in self._doers:
            self._doers[xmp_property.name](xmp_property)
        else:
            _logger.warning(
                f"GPS property '{xmp_property.name}' is not known"
                f" - {xmp_property.value=} ignored")

    def _set_version(self, xmp_property: NikonXMPProperty):
        """Set the version of GPS information.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        # The version of GPS information as a binary string.
        self.props["GPSVersionID"] \
            = int.from_bytes(xmp_property.value, "little")

    def _set_latitude_ref(self, xmp_property: NikonXMPProperty):
        """Set the latitude reference: north or south.

        Whether the latitude is north (``0``) or south (``1``). *This
        attribute do not match with the DICOM specifications* [digps]_.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        match xmp_property.value:
            case 0:
                self.props["GPSLatitudeRef"] = "N"

            case 1:
                self.props["GPSLatitudeRef"] = "S"

            case _:
                raise ValueError(
                    f"Unsupported latitude reference "
                    f"({xmp_property.value})")

    def _set_latitude(self, xmp_property: NikonXMPProperty):
        """Set the latitude.

        The latitude expressed in degrees-minutes-seconds
        as a set of three floating number.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        self.props["GPSLatitude"] = self._from_dms(xmp_property.value)

    def _set_longitude_ref(self, xmp_property: NikonXMPProperty):
        """Set the longitude reference: east or west.

        Whether the longitude is east (``2``) or west # (``3``). *This
        attribute do not match with the DICOM specifications* [digps]_.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        match xmp_property.value:
            case 2:
                self.props["GPSLongitudeRef"] = "E"

            case 3:
                self.props["GPSLongitudeRef"] = "W"

            case _:
                raise ValueError(
                    f"Unsupported longitude reference "
                    f"({xmp_property.value})")

    def _set_longitude(self, xmp_property: NikonXMPProperty):
        """Set the longitude.

        The longitude expressed in degrees-minutes-seconds as a set of
        three floating number.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        self.props["GPSLongitude"] = self._from_dms(xmp_property.value)

    def _set_altitude_ref(self, xmp_property: NikonXMPProperty):
        """Set the altitude reference.

        Reference altitude in meters as a binary string.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["GPSAltitudeRef"] = int.from_bytes(xmp_property.value,
                                                      'little')

    def _set_altitude(self, xmp_property: NikonXMPProperty):
        """Set the altitude.

        The altitude based on the reference in ``GPSAltitudeRef``, in
        meters.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["GPSAltitude"] = xmp_property.value

    def _set_timestamp(self, xmp_property: NikonXMPProperty):
        """Set the time stamp.

        The time in UTC (Coordinated Universal Time) expressed in
        hours-minutes-seconds as a set of three floating number.
        *This attribute do not match with the DICOM specifications* [digps]_.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        time = None
        # Each part is expressed as a float, but it must be an integer
        for t in xmp_property.value:
            if not t.is_integer():
                raise ValueError(
                    f"Timestamp part is not a integer ({t})")

        match len(xmp_property.value):
            case 1:
                time = dt.time(hour=int(xmp_property.value[0]),
                               tzinfo=dt.timezone.utc)

            case 2:
                time = dt.time(hour=int(xmp_property.value[0]),
                               minute=int(xmp_property.value[1]),
                               tzinfo=dt.timezone.utc)

            case 3:
                time = dt.time(hour=int(xmp_property.value[0]),
                               minute=int(xmp_property.value[1]),
                               second=int(xmp_property.value[2]),
                               tzinfo=dt.timezone.utc)

            case _:
                raise ValueError(
                    f"Timestamp having more than 3 number"
                    f" ({len(xmp_property.value)})")

        # Combine timestamps (date and time)
        if "GPSDateTimeStamp" in self.props:
            self.props["GPSDateTimeStamp"] \
                = dt.datetime.combine(self.timestamp, time)
        else:
            self.props["GPSDateTimeStamp"] = time

    def _set_datestamp(self, xmp_property: NikonXMPProperty):
        """Set the datetime stamp.

        The date as a string in the format: YYYY:MM:DD. *This attribute
        do not match with the DICOM specifications* [digps]_.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        date = dt.date.strptime(xmp_property.value, "%Y:%m:%d")
        if "GPSDateTimeStamp" in self.props:
            self.props["GPSDateTimeStamp"] \
                = dt.datetime.combine(date, self.props["GPSDateTimeStamp"])
        else:
            self.props["GPSDateTimeStamp"] = date

    def _set_status(self, xmp_property: NikonXMPProperty):
        """Set the status of the GPS receiver when the image is recorded.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        match xmp_property.value:
            case "A" | "V":
                self.props["GPSStatus"] = xmp_property.value

            case _:
                raise ValueError(
                    f"Unsupported longitude reference "
                    f"({xmp_property.value})")

    def _set_map_datum(self, xmp_property: NikonXMPProperty):
        """Set The geodetic survey data used by the GPS receiver.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["GPSMapDatum"] = xmp_property.value

    def _set_processing(self, xmp_property: NikonXMPProperty):
        """Set the name of the method used for location finding.

        The name of the method used for location finding as a set of two
        fixed strings ended by NULL characters.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        type = str(xmp_property.value[0:7].strip(b"\x00"), encoding='ascii')
        if type != "ASCII":
            raise ValueError(f"Processing method encoding is unknown ({type})")
        else:
            self.props["GPSProcessingMethod"] \
                = str(xmp_property.value[8:].strip(b"\x00"), encoding='ascii')

    def _set_speed_ref(self, xmp_property: NikonXMPProperty):
        """Set The unit used to express the ``GPSSpeed``.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        match xmp_property.value:
            case "K" | "M" | "N":
                self.props["GPSSpeedRef"] = xmp_property.value

            case _:
                raise ValueError(f"Unsupported speed reference "
                                 f"({xmp_property.value})")

    def _set_speed(self, xmp_property: NikonXMPProperty):
        """Set the speed of GPS receiver movement.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["GPSSpeed"] = xmp_property.value

    def _set_img_direction_ref(self, xmp_property: NikonXMPProperty):
        """Set the reference for giving the direction of the image.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        match xmp_property.value:
            case "T" | "M":
                self.props["GPSImgDirectionRef"] = xmp_property.value

            case _:
                raise ValueError(
                    f"Unsupported image direction reference "
                    f"({xmp_property.value})")

    def _set_img_direction(self, xmp_property: NikonXMPProperty):
        """Set the direction of the image.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["GPSImgDirection"] = xmp_property.value

    def _ignore_bearing(self, xmp_property: NikonXMPProperty):
        """Do nothing.

        Bearing GPS properties are is ignored as it contains the same
        information as Image Direction.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        _logger.info(
            f"GPS property '{xmp_property.name}' "
            f"({xmp_property.value=}) is ignored as it contains"
            f" the same information as Image Direction. ")

    def _from_dms(self, dms: list[float]):
        """Get coordinate in decimal degrees.

        The method convert a coordinate expressed in degrees-minutes-seconds
        in decimal degrees. This method can accept one to three float.

        Args:
            dms: coordinate expressed in degrees-minutes-seconds as a
                set of one to three `float`.

        Returns:
            float: coordinate in decimal degrees .
        """
        div = 1
        dd = 0.0

        if len(dms) > 3:
            raise ValueError(
                f"Coordinate having more than 3 number ({len(dms)})")
        else:
            for c in dms:
                if c is not None:
                    dd = dd + c / div
                    div = div * 60
        return dd

    def is_completed(self) -> bool:
        """Indicates a minimum of properties is present.

        The choice is a latitude and a longitude. The other properties
        as GPS references or altitude are optional.

        Returns:
             `True` if at least latitude and longitude is present.
        """
        return ("GPSLongitude" in self.props
                and "GPSLatitude" in self.props)

    def __repr__(self) -> str:
        """Return a printable string representation.

        The representation is the latitude and the longitude coordinate
        as two number expressed in decimal degree (5 precision digits)
        and the reference as suffix.

        Example:
            lat: ll.lllll (r), long: lll.lllll (r)
        """
        s = ""
        if "GPSLatitude" in self.props and "GPSLongitude" in self.props:
            s = (f"lat: {self.props["GPSLatitude"]:.5f} "
                 f"({self.props["GPSLatitudeRef"]}) "
                 f"long: {self.props["GPSLongitude"]:.5f} "
                 f"({self.props["GPSLongitudeRef"]})")
        return s


class NikonXMPProperty:
    """Nikon XMP property.

    This class parses an XML element as a ``XMP`` property and decode
    the resource. The resource may be a simple text , a structured
    data identified with the ``rdf:parseType`` attribute, or an array
    (see section 7.3 to 7.9 [adxmp1]_)

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Args:
        element: Element containing the property.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.

    Attributes:
        name: Name of the property.
        value: Value of the property, the type of the attribute depends on the
            resource type (binary, double,...).
    """
    name: str
    value: None | str | list[float|None] | int | bytes

    def __init__(self, element: ElementTree.Element):
        self.value = None

        self.name = _NS.shorten_name(element.tag)
        type_name = _NS.expand_name("rdf:parseType")
        if type_name in element.attrib:
            # Structure valued XMP property
            res_value = ""
            res_type = ""
            match element.attrib[type_name]:
                case "Resource":
                    for item in element:
                        item_name = _NS.shorten_name(item.tag)
                        match item_name: #
                            case "rdf:value":
                                res_value = item.text
                            case "astype:Type":
                                res_type = item.text
                            case _:
                                res_type = "dict"
                case _:
                    raise NikonError(f"Unknown parseType for property "
                                     f"({element.attrib[type_name]})")

            match res_type:
                case "Binary": # Binary buffer
                    self._set_binary(res_value)

                case "Long": # Integer
                    self._set_long(res_value)

                case "Double": # One or more float number
                    self._set_double(res_value)

                case "Ascii": # ASCII string
                    self._set_ascii(res_value)

                case "GPSProcessingMethod": # GPSProcessingMethod
                    self._set_gps_processing_method(res_value)

                case "dict": # Unqualified structure value
                    self._set_dict(element)

                case _:
                    raise NikonError(f"Unknown type for property ({res_type})")

        else:
            match len(element):
                case 0:
                    self._set_simple(element) # Simple valued XMP property

                case 1:
                    name = _NS.shorten_name(element[0].tag)
                    match name:
                        case "rdf:Bag": # element for an unordered (resp ordered array).
                            self._set_array(element[0])

                        case "rdf:Seq": # element for an ordered array.
                            self._set_array(element[0])

                        case "rdf:Alt": # element for an alternative array.
                            self._set_array(element[0])

                case _:
                    raise NikonError(
                        f"Unexpected number of elements for an array: "
                        f"actual '{len(element)}', expected 1")


    def _set_array(self, element: ElementTree.Element):
        """Set an array.

        The XMP specifications defines three type of array (section
        6.3.4 [adxmp1]_). This method store the array item in a `list`.

        Args:
            element: Element containing the property.
        """
        self.value = []
        for li in element:
            name = _NS.shorten_name(li.tag)
            if name == "rdf:li":
                self.value.append(li.text)
            else:
                raise NikonError(
                    f"Unexpected tag name for array content: "
                    f"actual '{name}', expected 'rdf:li'")

        _logger.debug(f"XMP property (array):"
                      f" {self.name}={self.value}")

    def _set_simple(self, element: ElementTree.Element):
        """Set a simple value.

        Args:
            element: Element containing the property.
        """
        self.value = element.text
        _logger.debug(f"XMP property (XML text):"
                      f" {self.name}={self.value}")

    def _set_binary(self, value:str):
        """Set a binary resource.

        Args:
            value: Value of the resource expressed as binary
                string encoded in base64 .
        """
        self.value = base64.b64decode(value)
        _logger.debug(f"XMP property (Binary):"
                      f" {self.name}={self.value}")

    def _set_long(self, value:str):
        """Set an integer resource.

        Args:
            value: Value of resource expressed as binary
                string encoded in base64 .
        """
        buffer = base64.b64decode(value)
        self.value = int.from_bytes(buffer, byteorder='little')
        _logger.debug(f"XMP property (Long):"
                      f" {self.name}={self.value}")

    def _set_double(self, value:str):
        """Set float number resource.

        The value may define one or more float number (IEEE754 Double
        precision 64-bits). All numbers are simply concatenated with no
        separators.

        Args:
            value: Value of resource expressed as binary
                string encoded in base64 .
        """
        buffer = base64.b64decode(value)
        vm = len(buffer) // 8
        if vm == 1:
            self.value = IEEE754(buffer).value
            _logger.debug(f"XMP property (Double):"
                          f" {self.name}={self.value}")
        else:
            self.value = []
            for i in range(len(buffer) // 8):
                self.value.append(
                    IEEE754(buffer[i * 8: (i + 1) * 8]).value)
            _logger.debug(f"XMP property (n*Double):"
                          f" {self.name}={self.value}")

    def _set_ascii(self, value: str):
        """Set ACSII string resource.

        Args:
            value: Value of resource expressed as binary
                string encoded in base64 .
        """
        self.value = value
        _logger.debug(f"XMP property (Ascii):"
                      f" {self.name}={self.value}")

    def _set_gps_processing_method(self, value: str):
        """Set GPSProcessingMethod resource (proprietary format...).

        Args:
            value: Value of integer resource expressed as binary
                string encoded in base64 .
        """
        self.value = base64.b64decode(value)
        _logger.debug(f"XMP property (GPSProcessingMethod):"
                      f" {self.name}={self.value}")

    def _set_dict(self, element: ElementTree.Element):
        """Set structure valued resource.

        Args:
            element: Element containing the property.
        """
        self.value = dict()
        for k in element:
            name = _NS.shorten_name(k.tag)
            self.value[name] = k.text
        _logger.debug(f"XMP property (Structure value):"
                      f" {self.name}={self.value}")


class NikonXMPDescriptions:
    """Manage the :term:`XMP Packet` header description

    This class parses an :term:`XMP Packet` and checks its structure. In case of
    error and NikonError exception is raised. :attr:`descriptions`
    attribute contains the list of description block. For the observed
    use case, there is only description block per sidecar file.

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Args:
        element: XML element containing the XMP Packet with its wrapper(
            ``xpacket``) as an XML processing instruction.

    Attributes:
        xmptk: Name of the xmp toolkit used to build the sidecar files.
        descriptions: List of ElementTree.Element containing XMP
            description block identified by the ``rdf:Description``
            element.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
    """
    _element: ElementTree.Element
    xmptk: str | None
    descriptions: list[ElementTree.Element] | None
    def __init__(self, element: ElementTree.Element):
        self._element = element
        self.descriptions = None
        self.xmptk = None

        self._check_xmp_packet()
        self._set_xmp_descriptions()

    def _check_xmp_packet(self):
        """Check the XMP metadata marker
        
        This method checks the :term:`XMP Packet` identified by a ``rdf:RDF``
        element (section 7.4 [adxmp1]_). The method set the
        :attr:`_element` attribute to ``rdf:RDF`` element in the XML tree.
        An ``x:xmpmeta`` element may be placed around the ``rdf:RDF``
        element (aka :term:`XMP Packet` - see section 7.3.3 [adxmp1]_)
        with name of the toolkit (``x:xmptk``) as attribute. This value
        is saved in :attr:`xmptk`.

        Raises:
            NikonError: Generic error, the :attr:`NikonError.message` details
                the error.
        """

        element = self._element
        # An XMP processor should tolerate an ``x:xmpmeta`` element in any
        # input and look within it for the ``rdf:RDF`` element.
        tag = _NS.shorten_name(element.tag)
        if tag == "x:xmpmeta":
            name = _NS.expand_name("x:xmptk")
            if name in element.attrib:
                self.xmptk = element.attrib[name]
                _logger.info(f"XMP Toolkit: {self.xmptk}")

            name = _NS.expand_name("rdf:RDF")
            elements = element.findall(name)
            if len(elements) != 1:
                raise NikonError(
                    f"Unexpected number of XMP packet: "
                    f"actual '{len(elements)}', expected 1")
        else:
            name = _NS.expand_name("rdf:RDF")
            elements = element.findall(name)
            if len(elements) != 1:
                raise NikonError(
                    f"More than XMP Packet: actual '{len(elements)}', "
                    f"expected 1")

        self._element = elements[0]

    def _set_xmp_descriptions(self):
        """Set the XMP descriptions attributes

        This method checks the XMP description identified by a
        ``rdf:Description`` element (section 7.4 [adxmp1]_). The method
        set the :attr:`descriptions` attribute.

        Raises:
            NikonError: Generic error, the :attr:`NikonError.message` details
                the error.
        """
        element = self._element
        self.descriptions = []
        for descr in element:
            tag = _NS.shorten_name(descr.tag)
            if tag != "rdf:Description":
                raise NikonError(f"Not a XMP description: actual '{tag}', "
                                 f"expected 'rdf:Description'")
            else:
                self.descriptions.append(descr)

        match len(self.descriptions):
            case 0:
                _logger.warning(f"No description element (rdf:Description)")

            case 1:
                pass

            case _:
                _logger.warning(f"More than one description element: "
                                f"actual {len(self.descriptions)},expected: 1."
                                f"Only the first one will be considered")


class NikonSDCProperties:
    """Nikon SDC properties container.

    This class parse a sidecar file and extract ``sdc`` tags (namespace
    'http://ns.nikon.com/sdc/1.0/'). The properties read are copied into
    the attribute :attr:`props` which can contain the following entries:

    * ``appname``: Name of the application that created the sidecar
      file.
    * ``appversion``: Version identifier of the application that
      created the sidecar file.

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Attributes:
        about: Identifier of properties set. The identifier have to be
            ``nikon sidecar/1.0``.
        version: Version identifier of the sidecar format.
        props: Dictionary of properties of the SDC set.
    """
    _ID = "nikon sidecar/1.0"
    about: str | None
    version: str | None
    props: dict
    def __init__(self):
        # Table of doers method for processing properties
        self._doers = {
            "sdc:about": self._check_about,
            "sdc:version": self._check_version,
            "sdc:appversion": self._set_appversion,
            "sdc:appname": self._set_appname,
        }
        self.about = None
        self.version= None
        self.props = {}

    def get_xmp_props(self):
        """Returns the supported properties

        This method provides the list of the supported XMP properties to
        populate the attribute classes.

        Returns:
            list: List of the supported properties. The property names
            are those of the XMP properties expressed in a short form
            (i.e. ``prefix:tag``).
        """
        return self._doers.keys()

    def set_attr(self, xmp_property: NikonXMPProperty):
        """Set the SDC attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if xmp_property.name in self._doers:
            _logger.debug(f"SDC property {xmp_property.name}"
                          f"={xmp_property.value}")
            self._doers[xmp_property.name](xmp_property)
        else:
            _logger.warning(f"SDC property '{xmp_property.name}' is not known"
                            f" - ignored")

    def _check_about(self, xmp_property: NikonXMPProperty):
        """Check the identifier of properties set.

        The identifier have to be ``nikon sidecar/1.0``.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.about = xmp_property.value
        if self.about != self._ID:
            raise ValueError(f"SDC Unsupported identifier, actual: "
                             f"{xmp_property.value}, expected: {self._ID}")

    def _check_version(self, xmp_property: NikonXMPProperty):
        """Check the version identifier  of properties set.

        The method simply read the version identifier as this attributes
        is not used.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.version = xmp_property.value

    def _set_appname(self, xmp_property: NikonXMPProperty):
        """Set the name of the application that created the sidecar file.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["appname"] = xmp_property.value

    def _set_appversion(self, xmp_property: NikonXMPProperty):
        """Set the version of the application that created the sidecar file.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["appversion"] = xmp_property.value


class NikonAsteroidProperties:
    """Nikon Asteroid (AST) properties container.

    This class parse a sidecar file and extract ``ast`` tags (namespace
    'http://ns.nikon.com/asteroid/1.0/'). The properties read are copied
    into the attribute :attr:`props` which can contain the following
    entries:

    * ``XMLPackets``: Image's metadata expressed as an :term:`XMP Packet`.
    * ``GPS``: Object containing the GPS properties
    * ``IPTC``: Image's metadata using :term:`IPTC Information Interchange
      Model`.

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Raises:
        ValueError: Inappropriate value, the :attr:`ValueError.message`
            details the error.

    Attributes:
        about: Identifier of the sidecar file format. The identifier
            have to be ``core-asteroid-tags``.
        version: version identifier of the sidecar format (currently
            ``11.0.0.3000``)
        props: Dictionary of properties of the AST set.
    """
    _ID = "core-asteroid-tags"
    #: Mapping IPTC properties to XMP properties, `IPTC Specification
    #: <https://www.iptc.org/std/photometadata/specification
    #: /IPTC-PhotoMetadata-2025.1.html#specification-table-template>`_
    #: defines the mapping.
    _IPTC_XMP = {
        "2:05": "dc:title",
        "2:25": "dc:subject",
        "2:40": "photoshop:Instructions",
        "2:55": "photoshop:DateCreated",
        "2:80": "dc:creator",
        "2:85": "photoshop:AuthorsPosition",
        "2:90": "photoshop:City",
        "2:95": "photoshop:State",
        "2:101": "photoshop:Country",
        "2:103": "photoshop:TransmissionReference",
        "2:105": "photoshop:Headline",
        "2:110": "photoshop:Credit",
        "2:115": "photoshop:Source",
        "2:116": "dc:rights",
        "2:120": "dc:description",
        "2:122": "photoshop:CaptionWriter",
    }
    #: See `Mapping Category Codes to Subject NewsCodes
    #: <https://www.iptc.org/std/photometadata/specification
    #: /IPTC-PhotoMetadata-2025.1.html#guideline-for-mapping-category-
    #: codes-to-subject-newscodes>`_
    _SUBJECTS = {
        "ACE": "1000000",
        "CLJ": "2000000",
        "DIS": "3000000",
        "FIN": "4000000",
        "EDU": "5000000",
        "EVN": "6000000",
        "HTH": "7000000",
        "HUM": "8000000",
        "LAB": "9000000",
        "LIF": "10000000",
        "POL": "11000000",
        "REL": "12000000",
        "SCI": "13000000",
        "SOI": "14000000",
        "SPO": "15000000"
    }
    #: Supported XMP metadata expressed as XMP properties. This list is
    #: subset of the XMP specification [ref] as observed from use cases
    _XMP_META = {
        "dc:title",
        "dc:subject",
        "dc:creator",
        "dc:rights",
        "dc:description",
        "photoshop:Category",
        "photoshop:SupplementalCategories",
        "photoshop:Instructions",
        "photoshop:DateCreated",
        "photoshop:AuthorsPosition",
        "photoshop:City",
        "photoshop:State",
        "photoshop:Country",
        "photoshop:TransmissionReference",
        "photoshop:Headline",
        "photoshop:Credit",
        "photoshop:Source",
        "photoshop:CaptionWriter",
        "photoshop:Urgency",
        "Iptc4xmpCore:CreatorContactInfo",
        "Iptc4xmpCore:CountryCode",
        "Iptc4xmpCore:IntellectualGenre",
        "Iptc4xmpCore:Location",
        "Iptc4xmpCore:SubjectCode",
        "Iptc4xmpCore:Scene",
        "xmpRights:UsageTerms",
        "xmp:Label",
        "xmp:Rating",
        "MicrosoftPhoto:Rating",
        "Iptc4xmpExt:Event"
    }

    about: str | None
    version: str | None
    props: dict
    def __init__(self):
        # Table of doers method for processing properties
        self._doers = {
            "ast:about": self._check_about,
            "ast:version": self._check_version,
            "ast:XMLPackets": self._set_xmlpacket,
            "ast:IPTC": self._set_iptc,
            "ast:GPSVersionID": self._set_gps,
            "ast:GPSLatitudeRef": self._set_gps,
            "ast:GPSLatitude": self._set_gps,
            "ast:GPSLongitudeRef": self._set_gps,
            "ast:GPSLongitude": self._set_gps,
            "ast:GPSAltitudeRef": self._set_gps,
            "ast:GPSAltitude": self._set_gps,
            "ast:GPSTimeStamp": self._set_gps,
            "ast:GPSDateStamp": self._set_gps,
            "ast:GPSStatus": self._set_gps,
            "ast:GPSMapDatum": self._set_gps,
            "ast:GPSProcessingMethod": self._set_gps,
            "ast:GPSSpeedRef": self._set_gps,
            "ast:GPSSpeed": self._set_gps,
            "ast:GPSImgDirectionRef": self._set_gps,
            "ast:GPSImgDirection": self._set_gps,
            "ast:GPSDestBearingRef": self._set_gps,
            "ast:GPSDestBearing": self._set_gps,
        }
        self.about = None
        self.version= None
        self.props = {}

    def get_xmp_props(self):
        """Returns the supported properties

        This method provides the list of the supported XMP properties to
        populate the attribute classes.

        Returns:
            list: List of the supported properties. The property names
            are those of the XMP properties expressed in a short form
            (i.e. ``prefix:tag``).
        """
        return self._doers.keys()

    def set_attr(self, xmp_property: NikonXMPProperty):
        """Set the AST attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if xmp_property.name in self._doers:
            _logger.debug(f"AST property {xmp_property.name}"
                          f"={xmp_property.value}")
            self._doers[xmp_property.name](xmp_property)
        else:
            _logger.warning(f"AST property '{xmp_property.name}' is not known"
                            f" - ignored")

    def _check_about(self, xmp_property: NikonXMPProperty):
        """Check the identifier of properties set.

        The identifier have to be ``core-asteroid-tags``.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.about = xmp_property.value
        if self.about != self._ID:
            raise ValueError(f"AST Unsupported identifier, actual: "
                             f"{xmp_property.value}, expected: {self._ID}")

    def _check_version(self, xmp_property: NikonXMPProperty):
        """Check the version identifier  of properties set.

        The method simply read the version identifier as this attributes
        is not used.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.version = xmp_property.value

    def _set_xmlpacket(self, xmp_property: NikonXMPProperty):
        """Set the metadata of the image.

        The image data are serialized in an embedded XML/XMP, so we
        walk in the RDF tree.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        element = ElementTree.fromstring(xmp_property.value)
        metadata = {}

        xmp_descr = NikonXMPDescriptions(element)
        if len(xmp_descr.descriptions) != 0:
            for prop in xmp_descr.descriptions[0]:
                xmp_property = NikonXMPProperty(prop)
                if xmp_property.name in self._XMP_META:
                    metadata[xmp_property.name] = xmp_property.value
                else:
                    _logger.warning(f"Metadata property '{xmp_property.name}' is not known"
                                    f" - ignored")

        self.props["XMLPackets"] = metadata


    def _set_iptc(self, xmp_property: NikonXMPProperty):
        """Set the IPTC data expressed as an XMP binary property.

        This method use the XMP name for the IPTC properties and
        not the IPTC name. It allows to have a unique naming referential

        Datasets 2:15 “Category” and 2:20 “Supplemental Category” are
        deprecated, but both are still present in NX studio. These two
        fields were replaced in IIM version 4 by the Dataset 2:12 “Subject
        Reference” which must be populated by values from the Subject
        NewsCodes controlled (see `Guideline for mapping Category Codes
        to Subject NewsCodes <https://www.iptc.org/std/photometadata
        /specification/IPTC-PhotoMetadata-2025.1.html#guideline-for
        -mapping-category-codes-to-subject-newscodes>`_

        Args:
            xmp_property: Nikon XMP property containing IPTC data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        iptc = {}
        buffer = xmp_property.value
        subject_code = [None]
        keywords = []

        while len(buffer) != 0:
            t, r, d = buffer[0], buffer[1], buffer[2]
            l = int.from_bytes(buffer[3:5])
            iim_id = f"{r:}:{d:02}"
            value = str(buffer[5:5 + l], encoding="ansi")
            if iim_id in self._IPTC_XMP:
                match iim_id:
                    case "2:25": # Keywords may be present one or more time.
                        keywords.append(value)
                    case _:
                        iptc[self._IPTC_XMP[iim_id]] = value
            else:
                match iim_id:
                    case "2:15": # Category deprecated (see note above)
                        if value in self._SUBJECTS:
                            subject_code[0] = "IPTC"
                            subject_code.append(f"{self._SUBJECTS[value]}")
                        else:
                            _logger.warning(
                                f"IPTC Unknown Category ({value} )- "
                                f"ignored as this field is deprecated")

                    case "2:20": # Supplemental Category (see note above)
                        subject_code.append(f"{value}")

                    case _:
                        raise ValueError(
                            f"IPTC Unsupported IIMid ({iim_id})")
            buffer = buffer[5 + l:]

        # Adding keywords
        if len(keywords) != 0:
            iptc[self._IPTC_XMP["2:25"]] = keywords

        # Mapping Category Codes to Subject NewsCodes
        # Subject Reference => Iptc4xmpCore:SubjectCode
        if subject_code[0] is not None:
            iptc["Iptc4xmpCore:SubjectCode"] = ":".join(subject_code)

        self.props["IPTC"] = iptc

    def _set_gps(self, xmp_property: NikonXMPProperty):
        """Set the GPS data expressed as an XMP property.

        This method is called for each GPS attribute, so the GPS container
        is created during the first call and updated on following calls.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        if "GPS" not in self.props:
            self.props["GPS"] = NikonGPSProperties()
        self.props["GPS"].set_attr(xmp_property)

class NikonNineProperties:
    """Nikon NINE properties container.

    This class parse a sidecar file and extract ``nine`` tags (namespace
    'http://ns.nikon.com/nine/1.0/').The properties read are copied
    into the attribute :attr:`props` which can contain the following
    entries:

    * ``NineEdits``: dictionary of image's adjustments.
    * ``Label``:  the image label
    * ``Rating``: the image rating

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Note:
        In the observed use cases, ``Label`` and ``Rating`` properties are
            always set to 0 (probably deprecated, but there is no public
            information).

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.

    Attributes:
        about: identifier of the sidecar file format. The identifier
            have to be ``nine-tags``.
        version: version identifier of the sidecar format (currently
            ``2.0.0``)
        props: Dictionary of properties of the NINE set.
    """
    _ID = "nine-tags"
    about: str | None
    version: str | None
    props: dict
    def __init__(self):
        # Table of doers method for processing properties
        self._doers = {
            "nine:about": self._check_about,
            "nine:version": self._check_version,
            "nine:NineEdits": self._set_nine_edits,
            "nine:Label": self._set_label,
            "nine:Rating": self._set_rating,
            "nine:Trim": self._ignore,
        }
        self.about = None
        self.version= None
        self.props = {}

    def get_xmp_props(self):
        """Returns the supported properties

        This method provides the list of the supported XMP properties to
        populate the attribute classes.

        Returns:
            list: List of the supported properties. The property names
            are those of the XMP properties expressed in a short form
            (i.e. ``prefix:tag``).
        """
        return self._doers.keys()

    def set_attr(self, xmp_property: NikonXMPProperty):
        """Set the Nine attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if xmp_property.name in self._doers:
            _logger.debug(f"NINE property {xmp_property.name}"
                          f"={xmp_property.value}")
            self._doers[xmp_property.name](xmp_property)
        else:
            _logger.warning(f"NINE property '{xmp_property.name}' is not known"
                            f" - ignored")

    def _check_about(self, xmp_property: NikonXMPProperty):
        """Check the identifier of properties set.

        The identifier have to be ``nikon sidecar/1.0``.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.about = xmp_property.value
        if self.about != self._ID:
            raise ValueError(f"NINE Unsupported identifier, actual: "
                             f"{xmp_property.value}, expected: {self._ID}")

    def _check_version(self, xmp_property: NikonXMPProperty):
        """Check the version identifier  of properties set.

        The method simply read the version identifier as this attributes
        is not used.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.version = xmp_property.value

    def _set_nine_edits(self, xmp_property: NikonXMPProperty):
        """Set the NineEdits (aka adjustments) attribute.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            NikAdjustmentError: Generic error, the :attr:`NikAdjustmentError.message`
                details the error.
        """
        tree = ElementTree.fromstring(xmp_property.value)
        self.props["NineEdits"] = create_nine_edits(tree)

    def _set_label(self, xmp_property: NikonXMPProperty):
        """Set the label of the image.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["Label"] = xmp_property.value

    def _set_rating(self, xmp_property: NikonXMPProperty):
        """Set the rating of the image.

        The image data are serialized in an embedded XML/XMP, so we
        walk in the RDF tree.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props["Rating"] = xmp_property.value

    def _ignore(self, xmp_property: NikonXMPProperty):
        """Do nothing.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        _logger.debug(
            f"NINE property '{xmp_property.name}' "
            f"({xmp_property.value}) is ignored ")


class NikonSideCar:
    """Nikon Side car file.

    This class parses a sidecar file to extract the metadata of the
    image on the one hand, and the image processing stack on the other.
    The NKSC files are in XML/XMP, so we walk in the RDF tree.

    The article named ":ref:`background_papers/inside_nksc:Inside Nikon
    Sidecar file`" details the data structure and tags used by Nikon.

    Args:
        path: filesystem path of the Nikon Sidecar files containing the
            :term:`XMP Packet` element.

    Attributes:
        metadata: unified dictionary of image metadata coming from the
            Asteroid (ast) set.
        geolocation: object contains the geolocation of the image.
        processing: dictonary of image ajustements. The key ``active``
            indicate if the processing will be applied on the
            image when opening in NX Studio. The key ``params`` contains
            processing's parameters as a dictionnary.
    """
    metadata: dict | None
    processing: dict | None
    geolocation: NikonGPSProperties | None
    def __init__(self, path: Path):
        self._doers = {}
        self._path = path
        self._element = None
        self._sdc = None
        self._ast = None
        self._nine = None
        self.metadata = {}
        self.processing = {}
        self.geolocation = None

        # Build the doers list based on elementary containers
        c = NikonSDCProperties()
        for k in c.get_xmp_props():
            self._doers[k] = self._set_sdc_attr

        c = NikonAsteroidProperties()
        for k in c.get_xmp_props():
            self._doers[k] = self._set_ast_attr
        c = NikonGPSProperties()
        for k in c.get_xmp_props():
            self._doers[k] = self._set_ast_attr

        c = NikonNineProperties()
        for k in c.get_xmp_props():
            self._doers[k] = self._set_nine_attr

        # Parses the sidecar file into an element tree for further analysis
        file = path.open()
        self._element = ElementTree.parse(file).getroot()
        file.close()


    def parse(self):
        """Parse the :term:`XMP Packet`.

        Raises:
            NikonError: Generic error, the :attr:`NikonError.message` details
                the error.
        """
        xmp_descr = NikonXMPDescriptions(self._element)
        if len(xmp_descr.descriptions) != 0:
            for prop in xmp_descr.descriptions[0]:
                xmp_property = NikonXMPProperty(prop)
                if xmp_property.name in self._doers:
                    self._doers[xmp_property.name](xmp_property)
                else:
                    _logger.warning(f"Property '{xmp_property.name}' is "
                                    f"not known - ignored")

        # Populate the public attribute with metadata and image adjustements
        self._merge_metadata()
        self._set_processing()
        self._set_geoloc()

        # Logging the read attributes
        if _logger.getEffectiveLevel() <= logging.INFO:
            if len(self.metadata) != 0:
                for k, v in self.metadata.items():
                    _logger.info(f"Metadata property {k}={v}")
            else:
                _logger.info(f"No metadata in the image")

            if self.geolocation is not None:
                _logger.info(f"Geolocation property: {self.geolocation}")
                for k, v in self.geolocation.props.items():
                    _logger.info(f"Full geolocation property {k}={v}")
            else:
                _logger.info(f"No geolocation data in the image")

            if len(self.processing) != 0:
                for k, v in self.processing.items():
                    _logger.info(f"Processing property {k}={v}")
            else:
                _logger.info(f"No processing in the image")

    def _set_sdc_attr(self, xmp_property: NikonXMPProperty):
        """Set the SDC attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self._sdc is None:
            self._sdc = NikonSDCProperties()
        self._sdc.set_attr(xmp_property)

    def _set_ast_attr(self, xmp_property: NikonXMPProperty):
        """Set the AST attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self._ast is None:
            self._ast = NikonAsteroidProperties()
        self._ast.set_attr(xmp_property)

    def _set_nine_attr(self, xmp_property: NikonXMPProperty):
        """Set the NINE attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self._nine is None:
            self._nine = NikonNineProperties()
        self._nine.set_attr(xmp_property)

    def _merge_metadata(self):
        """Merge the metadata sets.

        Image metadata comes from the IPTC set (``ast:IPTC`` element) and
        the XMP set (``ast:XMLPackets``). This method merge the two sets
        and store the metadata in :attr:`metadata`. The priority is the
        following order : IPTC, XMP.

        The image label and rating may be defined in the ``nine`` set
        and in the XMP set (``ast:XMLPackets``). In the observed use
        cases, these properties in the ``nine`` set are always set to 0
        (probably deprecated, but there is no public information). So
        the priority is the following order : XMP, Nine.
        """
        # Add application identifiers, to avoid collision
        self.metadata["appname"] = self._sdc.props["appname"]
        self.metadata["appversion"] = self._sdc.props["appversion"]

        # Default value for 'xmp:Rating' and  'xmp:Label'
        self.metadata["xmp:Rating"] = self._nine.props["Rating"]
        self.metadata["xmp:Label"] = NIKON_LABEL_MAP[self._nine.props["Label"]]

        # Copy the XMP set and overwrite with IPTC set.
        if self._ast is not None:
            if "XMLPackets" in self._ast.props:
                for k, v in self._ast.props["XMLPackets"].items():
                    if k in self.metadata:
                        _logger.info(f"Overwrite metadata {k}:"
                                     f" {self.metadata[k]} -> {v}")
                    self.metadata[k] = v
            if "IPTC" in self._ast.props:
                for k, v in self._ast.props["IPTC"].items():
                    if k in self.metadata:
                        _logger.info(f"Overwrite metadata {k}:"
                                     f" {self.metadata[k]} -> {v}")
                    self.metadata[k] = v

    def _set_processing(self):
        """Set the image adjustments.

        This method simply copy image adjustments in :attr:`processing`.
        """
        if self._nine is not None and "NineEdits" in self._nine.props:
            for k, v in self._nine.props["NineEdits"].items():
                self.processing[k] = v

    def _set_geoloc(self):
        """Set the geolocation of the image.

        This method simply copy GPS data in :attr:`geolocation`.
        """
        if self._ast is not None:
            if "GPS" in self._ast.props:
                self.geolocation = self._ast.props["GPS"]

    def get_rating(self) -> int:
        """Return the image rating.

        detail the param
        """
        if "xmp:Rating" in self.metadata:
            return int(self.metadata["xmp:Rating"])
        else:
            return 0

    def get_label(self) -> int:
        """Return the image label.

        detail the param
        """
        if "xmp:Label" in self.metadata:
            return self.metadata["xmp:Label"]
        else:
            return 0

    def is_protected(self) -> bool:
        """Return `True` if the image is protected.

        detail the param
        """
        return False

    def is_geotagged(self) -> bool:
        """Return `True` if the image have geolocation data.

        detail the param
        """
        is_geotagged = False
        if self.geolocation is not None:
            is_geotagged = self.geolocation.is_completed()
        return is_geotagged

    def is_tagged(self) -> bool:
        """Return `True` if the image have keywords.

        detail the param
        """
        return "dc:subject" in self.metadata

    def is_adjusted(self) -> bool:
        """Return `True` if the image have image adjustment.

        The method indicates if at least one image adjustment (filter) is
        active.

        Todo:
            Reduire le spectre des filtres (lié aux traitement d'image)
        """
        is_adjusted = False
        for k, v in self.processing.items():
            if v.active:
                is_adjusted = True
                break
        return is_adjusted

    def is_cropped(self) -> bool:
        """Return `True` if the image is cropped.

        detail the param
        """
        return False

    def is_perpective_adj(self) -> bool:
        """Return `True` if the image have perspective adjusted.

        detail the param
        """
        return False

    def is_bw(self) -> bool:
        """Return `True` if the image is monochrome (black and white).

        detail the param
        """
        return False

    def is_exposure_comp(self) -> bool:
        """Return `True` if the image have its exposure adjusted.

        detail the param
        """
        return False

    def is_denoised(self) -> bool:
        """Return `True` if the image have noise reduction.

        detail the param
        """
        return False

