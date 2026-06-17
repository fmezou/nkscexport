"""Handle Nikon sidecar files (read only)

The `sidecar.nikon` module implements handlers for the Nikon sidecar
file. The article named ":ref:`Inside Nikon Sidecar file`" details the
data structure and tags used by Nikon.

The exported classes, exceptions and functions (and any other objects)
are as follows:

``nikon`` exceptions
--------------------
.. hlist::
    :columns: 2

    * :exc:`NikonError` - Base class for sidecar parser exceptions
    * :exc:`NikonTagValueError` - Raised when a resource is erroneous
      (unknown tag)
    * :exc:`NikonMissingTagError` - Raised when an expected tag is missing
    * :exc:`NikonResourceError` - Raised when a tag value is not expected
    * :exc:`NikonResourceTypeError` - Raised when a resource is erroneous
      (unknown type)

``nikon``  classes
------------------
.. hlist::
    :columns: 2

    * :class:`NikonBaseProperties`- Base class for Nikon Properties class
    * :class:`NikonXMPProperty` - Nikon XMP property
    * :class:`NikonXMPMeta`- Nikon XMP Meta container
    * :class:`NikonRDF`- Nikon RDF container
    * :class:`NikonRDFDescription`- Nikon RDF Description container.
      (NOT USEFUL)
    * :class:`NikonSDCProperties`- Nikon SDC properties container
    * :class:`NikonAsteroidProperties`- Nikon Asteroid properties container
    * :class:`NikonNineProperties`- Nikon Nine properties container
    * :class:`NikonSideCar`- Nikon sidecar file.

``nikon`` constants
-------------------
.. todo:: review the list after the completion of implement

.. hlist::
    :columns: 2

    * :const:`NIKON_RATING_MAP` - Correspondence note Nikon → note XMP
    * :const:`NIKON_LABEL_MAP` - Correspondence note Nikon → note XMP"
    * :const:`NIKON_SUPPORTED_FORMAT` - file extension of the supported
      image file
    * :const:`NIKON_NKSC_SUBFOLDER`- subfolder storing the Nikon sidecar
      file
    * :const:`NIKON_NKSC_EXT`- file extension of Nikon sidecar files

Using ``nikon``
---------------
.. todo:: describe how using the module

``nikon`` reference manual
--------------------------
"""
import base64
import logging
import datetime as dt
from xml.etree import ElementTree

from library.ieee754 import IEEE754
from library.namespace import NameSpace
from sidecar.nik_adjustment import NineEdits


__all__ = [
    "NikonError",
    "NikonMissingTagError",
    "NikonTagValueError",
    "NikonResourceError",
    "NikonResourceTypeError",
    "NikonGPSProperties",
    "NikonXMPProperty",
    "NikonXMPDescriptions",
    "NikonSDCProperties",
    "NikonAsteroidProperties",
    "NikonNineProperties",
    "NikonSideCar",
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

#: file extensions of supported image files
NIKON_SUPPORTED_FORMAT = [
    ".nef", ".nrw",
    ".jpg", ".jpeg",
    ".tif", ".tiff",
    ".hif",
    ".nefx",
    ".mpo"
]

#: Subfolder storing the Nikon sidecar files
NIKON_NKSC_SUBFOLDER = "NKSC_PARAM"

#: file extension of Nikon sidecar files
NIKON_NKSC_EXT = ".nksc"

#: XML Namespaces used in sidecar file
_NS = NameSpace({
    "x": "adobe:ns:meta/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "sdc": "http://ns.nikon.com/sdc/1.0/",
    "ast": "http://ns.nikon.com/asteroid/1.0/",
    "astype": "http://ns.nikon.com/asteroid/Types/1.0/",
    "nine": "http://ns.nikon.com/nine/1.0/"})

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


class NikonMissingTagError(NikonError):
    """Raised when an expected tag is missing.

    Args:
        name: Name of the missing tag.

    Attributes:
        name: Name of the missing tag.
    """
    name: str | None

    def __init__(self, name: str | None):
        self.name = name
        NikonError.__init__(self, f"Expected tag '{name}' is missing.")


class NikonTagValueError(NikonError):
    """Raised when a tag value is not expected.

    Args:
        name: Name of the tag.
        value: Value of the erroneous tag.

    Attributes:
        name: Name of the tag.
        value: Value of the erroneous tag.
    """
    name: str | None
    value: str | None

    def __init__(self, name: str, value: str | None):
        self.name = name
        self.value = value
        NikonError.__init__(self, f"Unexpected value '{value}' for the "
                                 f"tag '{name}'.")


class NikonResourceError(NikonError):
    """Raised when a resource is erroneous (unknown tag).

    Args:
        prop_name : Name of the property.
        tag_name: Name of the erroneous tag.

    Attributes:
        prop_name : Name of the property
        tag_name: Name of the erroneous tag.
    """
    prop_name: str | None
    tag_name: str | None

    def __init__(self, prop_name: str | None, tag_name: str | None):
        self.prop_name = prop_name
        self.tag_name = tag_name
        msg = f"Unknown tag '{tag_name}' used for the resource value of "\
              "{prop_name} property"
        NikonError.__init__(self, msg)


class NikonResourceTypeError(NikonError):
    """Raised when a resource is erroneous (unknown type).

    Args:
        prop_name : Name of the property.
        type_name: Name of the erroneous type.

    Attributes:
        prop_name : Name of the property.
        type_name: Name of the erroneous type.
    """
    prop_name: str | None
    type_name: str | None

    def __init__(self, prop_name: str | None, type_name: str | None):
        self.prop_name = prop_name
        self.type_name = type_name
        msg = f"Unknown type '{type_name}' used for the resource value of {prop_name} property"
        NikonError.__init__(self, msg)


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

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon. In a nutshell, Nikon seems to have
    using DICOM specification (see :ref:`InsideNKCS.GPSAttrTable`).

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

        Example::

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
    the resource. The resource may be a simple text or a structured
    data identified with the ``rdf:parseType`` attribute.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: Element containing the property.

    Raises:
        NikonResourceError: A resource is erroneous (unknown tag).
        NikonResourceTypeError: A resource is erroneous (unknown type)

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
            # Get the value encoded in ascii and the type
            match element.attrib[type_name]:
                case "Resource":
                    for item in element:
                        item_name = _NS.shorten_name(item.tag)
                        match item_name:
                            case "rdf:value":
                                res_value = item.text
                            case "astype:Type":
                                res_type = item.text
                            case _:
                                raise NikonResourceError(self.name, item_name)
                case _:
                    raise NikonResourceError(self.name, element.attrib[type_name])

            match res_type:
                # Binary buffer
                case "Binary":
                    self.value = base64.b64decode(res_value)
                    _logger.debug(f"XMP property (Binary):"
                                  f" {self.name}={self.value}")

            # Integer
                case "Long":
                    buffer = base64.b64decode(res_value)
                    self.value = int.from_bytes(buffer, byteorder='little')
                    _logger.debug(f"XMP property (Long):"
                                  f" {self.name}={self.value}")

                # One or more float number (IEEE754 Double precision 64-bits)
                case "Double":
                    buffer = base64.b64decode(res_value)
                    vm = len(buffer) // 8
                    if vm == 1:
                        self.value = IEEE754(buffer).value
                        _logger.debug(f"XMP property (Double):"
                                      f" {self.name}={self.value}")
                    else:
                        self.value = []
                        for i in range(len(buffer) // 8):
                            self.value.append(
                                IEEE754(buffer[i*8 : (i+1)*8]).value)
                        _logger.debug(f"XMP property (n*Double):"
                                      f" {self.name}={self.value}")

                # ASCII string
                case "Ascii":
                    self.value = res_value
                    _logger.debug(f"XMP property (Ascii):"
                                  f" {self.name}={self.value}")

                # GPSProcessingMethod : proprietary format...
                case "GPSProcessingMethod":
                    self.value = base64.b64decode(res_value)
                    _logger.debug(f"XMP property (GPSProcessingMethod):"
                                  f" {self.name}={self.value}")

                case _:
                    raise NikonResourceTypeError(self.name, res_type)

        else:
            # Simple valued XMP property
            self.value = element.text
            _logger.debug(f"XMP property (XML text):"
                          f" {self.name}={self.value}")


class NikonXMPDescriptions:
    """Manage the XMP Packet header description

    This class parses an XMP Packet and checks its structure. In case of
    error and NikonError exception is raised. :attr:`descriptions`
    attribute contains the list of description block. For the observed
    use case, there is only description block per sidecar file.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

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
        
        This method checks the XMP packet identified by a ``rdf:RDF``
        element (section 7.4 [adxmp1]_). The method set the
        :attr:`_element` attribute to ``rdf:RDF`` element in the XML tree.
        An ``x:xmpmeta`` element may be placed around the ``rdf:RDF``
        element (aka XMP packet). (section 7.3.3 [adxmp1]_) with name of
        the toolkit (``x:xmptk``) as attribute. This value is saved in
        :attr:`xmptk`.

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
                _logger.debug(f"XMP Toolkit: {self.xmptk}")

            name = _NS.expand_name("rdf:RDF")
            elements = element.findall(name)
            if len(elements) != 1:
                raise NikonError(
                    f"More than XMP Packet: actual '{len(elements)}', "
                    f"expected 1")
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

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

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
            self._doers[xmp_property.name](xmp_property)
            _logger.debug(f"SDC property {xmp_property.name}"
                          f"={xmp_property.value}")
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
        self.props['appname'] = xmp_property.value

    def _set_appversion(self, xmp_property: NikonXMPProperty):
        """Set the version of the application that created the sidecar file.

        Args:
            xmp_property: Nikon XMP property containing data.
        """
        self.props['appversion'] = xmp_property.value


class NikonAsteroidProperties:
    """Nikon Asteroid properties container.

    This class parse a sidecar file and extract ``ast`` tags (namespace
    'http://ns.nikon.com/asteroid/1.0/'). The properties read are copied
    into the attribute :attr:`props` which can contain the following
    entries:

    * ``XMLPackets``: `<https://www.exiftool.org/TagNames/XMP.html>`_
    * ``GPS``: Object containing the GPS properties
    * ``IPTC``: `<https://www.exiftool.org/TagNames/IPTC.html>`_

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:Description`` tag.

    Raises:
        ValueError: Inappropriate value, the :attr:`ValueError.message`
            details the error.

    Attributes:
        about: Identifier of the sidecar file format. The identifier
            have to be ``core-asteroid-tags``.
        version: version identifier of the sidecar format (currently
            ``11.0.0.3000``)
        props: Dictionary of properties of the SDC set.
    """
    _ID = "core-asteroid-tags"
    #: Mapping IPTC properties to XMP properties, `IPTC Specification
    #: <https://www.iptc.org/std/photometadata/specification
    #: /IPTC-PhotoMetadata-2025.1.html#specification-table-template>`_
    #: defines the mapping.
    _XMP = {
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
    _SUBJECT = {
        'ACE': '1000000',
        'CLJ': '2000000',
        'DIS': '3000000',
        'FIN': '4000000',
        'EDU': '5000000',
        'EVN': '6000000',
        'HTH': '7000000',
        'HUM': '8000000',
        'LAB': '9000000',
        'LIF': '10000000',
        'POL': '11000000',
        'REL': '12000000',
        'SCI': '13000000',
        'SOI': '14000000',
        'SPO': '15000000',
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
            self._doers[xmp_property.name](xmp_property)
            _logger.debug(f"AST property {xmp_property.name}"
                          f"={xmp_property.value}")
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
        self.props["XMLPackets"] = xmp_property.value

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
            if iim_id in self._XMP:
                match iim_id:
                    case "2:25": # May be present one or more time.
                        keywords.append(value)
                    case _:
                        iptc[self._XMP[iim_id]] = value
            else:
                match iim_id:
                    case "2:15":
                        if value in self._SUBJECT:
                            subject_code[0] = "IPTC"
                            subject_code.append(f"{self._SUBJECT[value]}")
                        else:
                            _logger.warning(
                                f"IPTC Unknown Category ({value} )- "
                                f"ignored as this field is deprecated")

                    case "2:20":
                        subject_code.append(f"{value}")

                    case _:
                        raise ValueError(
                            f"IPTC Unsupported IIMid ({iim_id})")
            buffer = buffer[5 + l:]

        # Adding keywords
        if len(keywords) != 0:
            iptc[self._XMP["2:25"]] = keywords

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
    """Nikon Nine properties container.

    This class parse a sidecar file and extract ``nine`` tags (namespace
    'http://ns.nikon.com/nine/1.0/').The properties read are copied
    into the attribute :attr:`props` which can contain the following
    entries:

    * ``NineEdits``: `<https://www.exiftool.org/TagNames/Nikon.html#NineEdits>`_
    * ``Label``:  todo
    * ``Rating``: todo

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:Description`` tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: identifier of the sidecar file format. The identifier
            have to be ``nine-tags``.
        version: version identifier of the sidecar format (currently
            ``2.0.0``)
        props: Dictionary of properties of the SDC set.
    """
    _ID = "nine-tags"
    about: str | None
    version: str | None
    trim: str | None
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
        self.trim = None
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
            self._doers[xmp_property.name](xmp_property)
            _logger.debug(f"NINE property {xmp_property.name}"
                          f"={xmp_property.value}")
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
            NikAdjustmentError: Generic error, the :attr:`NikFilterError.message`
                details the error.
        """
        tree = ElementTree.fromstring(xmp_property.value)
        self.props["NineEdits"] = NineEdits(tree).adjustments

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


class NikonSideCar(object):
    """Nikon Side car file.

    This class parses a sidecar file to extract the metadata of the
    image on the one hand, and the image processing stack on the other.
    The NKSC files are in XML/XMP, so we walk in the RDF tree.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    This class parse a sidecar file and extract ``xmpmeta`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the XMP Packet element.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `parse`                              ..
        ===================================  ===================================

    **Using NikonSideCar...**
    """
    sdc: NikonSDCProperties | None
    ast: NikonAsteroidProperties | None
    nine: NikonNineProperties | None
    def __init__(self, element: ElementTree.Element):
        self._doers = {}
        self._metadata = {}
        self._processing = {}
        self._data = None
        self._element = element
        self.sdc = None
        self.ast = None
        self.nine = None

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


    def parse(self):
        """
        Parse the :term:`XMP` tree and populate metadata and filters dictionaries

        Raises:
            NikonMissingTagError: A tag value is not expected.
            NikonTagValueError: An expected tag is missing.

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error log is written on the standard error (``stderr``).
        """
        xmp_descr = NikonXMPDescriptions(self._element)
        if len(xmp_descr.descriptions) != 0:
            for prop in xmp_descr.descriptions[0]:
                xmp_property = NikonXMPProperty(prop)
                if xmp_property.name in self._doers:
                    self._doers[xmp_property.name](xmp_property)
                else:
                    _logger.warning(f"SDC property '{xmp_property.name}' is not known"
                                    f" - ignored")

        # Logging the read attributes
        if _logger.getEffectiveLevel() <= logging.INFO:
            if self.sdc is not None:
                for k, v in self.sdc.props.items():
                    _logger.info(f"SDC property {k}={v}")
            else:
                _logger.info(f"No SDC property")

            if self.ast is not None:
                for k, v in self.ast.props.items():
                    _logger.info(f"AST property {k}={v}")
                if "GPS" in self.ast.props:
                    for k, v in self.ast.props["GPS"].props.items():
                        _logger.info(f"AST GPS property {k}={v}")
                if "IPTC" in self.ast.props:
                    for k, v in self.ast.props["IPTC"].items():
                        _logger.info(f"AST IPTC property {k}={v}")
            else:
                _logger.info(f"No AST property")

            if self.nine is not None:
                for k, v in self.nine.props.items():
                    _logger.info(f"NINE property {k}={v}")
            else:
                _logger.info(f"No NINE property")

    def _set_sdc_attr(self, xmp_property: NikonXMPProperty):
        """Set the SDC attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self.sdc is None:
            self.sdc = NikonSDCProperties()
        self.sdc.set_attr(xmp_property)

    def _set_ast_attr(self, xmp_property: NikonXMPProperty):
        """Set the AST attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self.ast is None:
            self.ast = NikonAsteroidProperties()
        self.ast.set_attr(xmp_property)

    def _set_nine_attr(self, xmp_property: NikonXMPProperty):
        """Set the NINE attribute expressed as an XMP property.

        Args:
            xmp_property: Nikon XMP property containing data.

        Raises:
            ValueError: Inappropriate value, the :attr:`ValueError.message`
                details the error.
        """
        if self.nine is None:
            self.nine = NikonNineProperties()
        self.nine.set_attr(xmp_property)

    def get_rating(self) -> int:
        """Return the image rating.

        detail the param
        """
        return 0

    def get_label(self) -> int:
        """Return the image label.

        detail the param
        """
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
        if self.ast is not None and "GPS" in self.ast.props:
            is_geotagged = self.ast.props["GPS"].is_completed()
        return is_geotagged

    def is_tagged(self) -> bool:
        """Return `True` if the image have keywords.

        detail the param
        """
        return False

    def is_filtered(self) -> bool:
        """Return `True` if the image have image adjustment.

        The method indicates if at least one image adjustment (filter) is
        active.
        """
        return False

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

