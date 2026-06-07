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

__all__ = [
    "NikonError",
    "NikonMissingTagError",
    "NikonTagValueError",
    "NikonResourceError",
    "NikonResourceTypeError",
    "NikonBaseProperties",
    "NikonGPSProperty",
    "NikonXMPProperty",
    "NikonXMPMeta",
    "NikonRDF",
    "NikonRDFDescription",
    "NikonSDCProperties",
    "NikonAsteroidProperties",
    "NikonNineProperties",
    "NikonSideCar",
    "NIKON_RATING_MAP",
    "NIKON_LABEL_MAP",
    "NIKON_SUPPORTED_FORMAT",
    "NIKON_NKSC_SUBFOLDER",
    "NIKON_NKSC_EXT"
]


NIKON_RATING_MAP = {
    "-1":"-1",# rejeté → -1 en XMP
    "0":"0", # Aucun
    "1":"1", # *
    "2":"2", # **
    "3":"3", # ***
    "4":"4", # ****
    "5":"5", # *****
}
"""Correspondence note Nikon → note XMP (0-5)
Nikon stocke la note sous forme entière 0–5 directement compatible XMP"""


NIKON_LABEL_MAP = {
    "1":"Rouge",
    "2":"Orange",
    "3":"Jaune",
    "4":"Vert",
    "5":"Cyan",
    "6":"Bleu",
    "7":"Violet",
    "8":"Magenta",
    "9":"Rose",
    "0":"(Aucune)",
}
"""Correspondence label couleur Nikon → label XMP (texte)
Nikon encode les labels par numéro dans nksc"""


NIKON_SUPPORTED_FORMAT = [
    ".nef", ".nrw",
    ".jpg", ".jpeg",
    ".tif", ".tiff",
    ".hif",
    ".nefx",
    ".mpo"
]
"""file extension of the supported image file"""

NIKON_NKSC_SUBFOLDER = "NKSC_PARAM"
"""subfolder storing the Nikon sidecar files"""

NIKON_NKSC_EXT = ".nksc"
"""file extension of Nikon sidecar files"""

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


class NikonGPSProperty():
    """Nikon GPS property.

    This class manage compound data representing geographic coordinates
    used by Nikon to geolocalize image. This class can be used in a
    formatted string.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon. In a nutshell, Nikon seems to have
    using DICOM specification (see :ref:`InsideNKCS.GPSAttrTable`).

    Raises:
        ValueError: argument has the right type but an
            inappropriate value.

    Attributes:
        version_id: The version of GPS information.
        latitude_ref: Whether the latitude is north (``N``) or south
            (``S``).
        latitude: The latitude, expressed in decimal degrees.
        longitude_ref: Whether the longitude is east (``E``) or west
            (``W``).
        longitude: The longitude, expressed in decimal degrees.
        altitude_ref: The altitude used as the reference altitude in
            meters.
        altitude: The altitude based on the reference in
            :attr:`altitude_ref` in meters.
        timestamp: The date and time, in UTC (Coordinated Universal Time).
        status: The status of the GPS receiver when the image is
            recorded. ``A`` measurement is in progress, ``V``
            measurement interrupted
        processing_method: The name of the method used for location
            finding (``GPS``, ``CELLID``, ``MANUAL``).
        map_datum: The geodetic survey data used by the GPS receiver.
            ``WGS-84`` is used in most cases.
    """
    version_id: int | None
    latitude_ref: str | None
    latitude: float | None
    longitude_ref: str | None
    longitude: float | None
    altitude_ref: int | None
    altitude: float | None
    timestamp: dt.datetime | dt.time | None
    status: str | None
    processing_method: str | None
    map_datum: str | None
    def __init__(self):
        self.version_id = 0
        self.latitude_ref = None
        self.latitude = None
        self.longitude_ref = None
        self.longitude = None
        self.altitude_ref = None
        self.altitude = None
        self.timestamp = None
        self.status = None
        self.processing_method = None
        self.map_datum = None

    def set_version_id(self, version_id: bytes):
        """Set the version of GPS information.

        Args:
            version_id: The version of GPS information as a binary
                string.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {version_id=}")
        self.version_id = int.from_bytes(version_id, 'little')

    def set_latitude_ref(self, latitude_ref: int):
        """Set the latitude reference.

        Args:
            latitude_ref: Whether the latitude is north (``0``) or south
                (``1``). *This attribute do not match with the
                DICOM specifications* [digps]_.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {latitude_ref=}")
        match latitude_ref:
            case 0:
                self.latitude_ref = "N"

            case 1:
                self.latitude_ref = "S"

            case _:
                raise ValueError(
                    f"Unsupported latitude reference ({latitude_ref})")

    def set_latitude(self, latitude: list[float]):
        """Set the latitude.

        Args:
            latitude: The latitude expressed in degrees-minutes-seconds
                as a set of three floating number. The method considers
                the set having a variable size (1 to 3 float).

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {latitude=}")
        self.latitude = self._from_dms(latitude)

    def set_longitude_ref(self, longitude_ref: int):
        """Set the longitude reference.

        Args:
            longitude_ref: Whether the longitude is east (``2``) or west
                (``3``). *This attribute do not match with the
                DICOM specifications* [digps]_.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {longitude_ref=}")
        match longitude_ref:
            case 2:
                self.longitude_ref = "E"

            case 3:
                self.longitude_ref = "W"

            case _:
                raise ValueError(
                    f"Unsupported longitude reference ({longitude_ref})")

    def set_longitude(self, longitude: list[float]):
        """Set the longitude.

        Args:
            longitude: The longitude expressed in degrees-minutes-seconds
                as a set of three floating number. The method considers
                the set having a variable size (1 to 3 float).

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {longitude=}")
        self.longitude = self._from_dms(longitude)

    def set_altitude_ref(self, altitude_ref: int):
        """Set the altitude reference.

        Args:
            altitude_ref: The altitude used as the reference altitude in
                meters.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {altitude_ref=}")
        self.altitude_ref = altitude_ref

    def set_altitude(self, altitude: float):
        """Set the altitude.

        Args:
            altitude: The altitude based on the reference in
                :attr:`altitude_ref` in meters.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {altitude=}")
        self.altitude = altitude

    def set_timestamp(self, timestamp: list[float]):
        """Set the datetime stamp.

        Args:
            timestamp: The time in UTC (Coordinated Universal Time)
                expressed in hours-minutes-seconds as a set of three
                floating number. *This attribute do not match with the
                DICOM specifications* [digps]_.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {timestamp=}")
        time = None
        # Each part is expressed as a float, but it must be an integer
        for t in timestamp:
            if not t.is_integer():
                raise ValueError(
                    f"Timestamp part is not a integer ({t})")

        match len(timestamp):
            case 1:
                time = dt.time(hour=int(timestamp[0]),
                               tzinfo=dt.timezone.utc)

            case 2:
                time = dt.time(hour=int(timestamp[0]),
                               minute=int(timestamp[1]),
                               tzinfo=dt.timezone.utc)

            case 3:
                time = dt.time(hour=int(timestamp[0]),
                               minute=int(timestamp[1]),
                               second=int(timestamp[2]),
                               tzinfo=dt.timezone.utc)

            case _:
                raise ValueError(
                    f"Timestamp having more than 3 number ({len(timestamp)})")

        # Combine timestamps (date and time)
        if self.timestamp is None:
            self.timestamp = time
        else:
            self.timestamp = dt.datetime.combine(self.timestamp, time)

    def set_datestamp(self, datestamp: str):
        """Set the datetime stamp.

        Args:
            timestamp: The date as a string in the format: YYYY:MM:DD.
                *This attribute do not match with the DICOM
                specifications* [digps]_.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {datestamp=}")
        date = dt.date.strptime(datestamp, "%Y:%m:%d")
        if self.timestamp is None:
            self.timestamp = date
        else:
            self.timestamp = dt.datetime.combine(date, self.timestamp)

    def set_status(self, status: str):
        """Set the status of the GPS receiver.

        Args:
            status: The status of the GPS receiver when the image is
            recorded. ``A`` measurement is in progress, ``V``
            measurement interrupted.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {status=}")
        match status:
            case "A" | "V":
                self.status = "E"

            case _:
                raise ValueError(
                    f"Unsupported longitude reference ({status})")

    def set_processing_method(self, processing_method: bytes):
        """Set ame of the method used for location finding.

        DICOM specifications [digps]_ do not clearly define the
            encoding use.

        Args:
            processing_method: The name of the method used for location
                finding as a set of two fixed strings ended by NULL
                characters.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {processing_method=}")
        type = str(processing_method[0:7].strip(b"\x00"), encoding='ascii')
        method = str(processing_method[8:].strip(b"\x00"), encoding='ascii')
        if type != "ASCII":
            raise ValueError(
                f"Processing method encoding is unknown ({type})")
        else:
            self.processing_method = method

    def set_map_datum(self, map_datum: str ):
        """Set the geodetic survey data.

        Args:
            map_datum: The geodetic survey data used by the GPS receiver.
                ``WGS-84`` is used in most cases.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        _logger.debug(f"GPS property {map_datum=}")
        self.map_datum = map_datum

    def _from_dms(self, dms: list[float]):
        """Get coordinate in decimal degrees.

        The method convert a coordinate expressed in degrees-minutes-seconds
        in decimal degrees. This method can accept one to three float.

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

    def __repr__(self) -> str:
        """Return a printable string representation.

        The method format the latitude and the longitude coordinate as two
        number expressed in decimal degree (5 precision digits) and the
        reference as suffix.

        lat: ll.lllll (r), long: lll.lllll (r)
        """
        s = ""
        if self.latitude is not None and self.longitude is not None:
            s = (f"lat: {self.latitude:.5f} ({self.latitude_ref}) "
                 f"long: {self.longitude:.5f} ({self.longitude_ref})")
        return s

class NikonBaseProperties(object):
    """Base class for Nikon Properties class.

    Args:
        element: XML element containing the metadata.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message`
            details the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    """
    def __init__(self, element: ElementTree.Element):
        self._element = element

        # Namespaces used in sidecar file
        self._namespaces = {
            "x": "adobe:ns:meta/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "sdc": "http://ns.nikon.com/sdc/1.0/",
            "ast": "http://ns.nikon.com/asteroid/1.0/",
            "astype": "http://ns.nikon.com/asteroid/Types/1.0/",
            "nine": "http://ns.nikon.com/nine/1.0/"
        }
        # build the reverse namespace table
        self._reverse_namespaces = {}
        for prefix, uri in self._namespaces.items():
            self._reverse_namespaces[uri] = prefix

    def _shorten_name(self, expanded_name: str) -> str:
        """Shorten a tag or attribute name based on the namespace table.

        Args:
            expanded_name: Name of the tag or attribute in expanded
                format (i.e. ``{uri}tag``). An empty string or without
                uri is accepted.

        Return:
            Name in a short format (i.e. ``prefix:tag``). An empty
            string or without uri in :data:`expanded_name` returns the
            unchanged value.
        """
        if "}" in expanded_name:
            uri, tag = expanded_name.split("}")
            short_name = "{}:{}".format(
                self._reverse_namespaces[uri.removeprefix("{")],
                tag)
        else:
            short_name = expanded_name

        return short_name

    def _expand_name(self, short_name: str) -> str:
        """Expand a tag or attribute name based on the namespace table.

        Args:
            short_name: Name of the tag or attribute in short format
                (i.e. ``prefix:tag``). An empty string or without
                prefix is accepted.

        Returns:
            Name in expanded format (i.e. ``{uri}tag``). An empty
            string or without prefix in :data:`short_name` return the
            unchanged value.
        """
        if ":" in short_name:
            prefix, tag = short_name.split(":")
            expanded_name = "{{{}}}{}".format(self._namespaces[prefix], tag)
        else:
            expanded_name = short_name
        return expanded_name


class NikonXMPProperty(NikonBaseProperties):
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
        super().__init__(element)
        self.value = None

        self.name = self._shorten_name(element.tag)
        type_name = self._expand_name("rdf:parseType")
        if type_name in element.attrib:
            # Structure valued XMP property
            res_value = ""
            res_type = ""
            # Get the value encoded in ascii and the type
            match element.attrib[type_name]:
                case "Resource":
                    for item in element:
                        item_name = self._shorten_name(item.tag)
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

                # Integer
                case "Long":
                    buffer = base64.b64decode(res_value)
                    self.value = int.from_bytes(buffer, byteorder='little')

                # List of float number (IEEE754 Double precision 64-bits)
                case "Double":
                    self.value = []
                    value = base64.b64decode(res_value)
                    for i in range(len(value) // 8):
                        self.value.append(IEEE754(value[i*8 : (i+1)*8]).value)

                # ASCII string
                case "Ascii":
                    self.value = res_value

                # GPSProcessingMethod : unknown format...
                # todo: explain or search
                case "GPSProcessingMethod":
                    self.value = base64.b64decode(res_value)

                case _:
                    raise NikonResourceTypeError(self.name, res_type)

        else:
            # Simple valued XMP property
            self.value = element.text


class NikonXMPMeta(NikonBaseProperties):
    """Nikon XMP Meta container.

    This class parse a sidecar file and extract ``xmpmeta`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``x:xmpmeta`` element.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    Attributes:
        xmptk: The toolkit name (``XMP Core 5.5.0`` for example).
    """
    xmptk: str | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.xmptk = None

        if self._shorten_name(self._element.tag) != "x:xmpmeta":
            raise NikonMissingTagError("x:xmpmeta")
        name = self._expand_name("x:xmptk")
        if name in self._element.attrib:
            self.xmptk = element.attrib[name]
            _logger.debug(f"{name} = {element.attrib[name]}")


class NikonRDF(NikonBaseProperties):
    """Nikon RDF container.

    This class parse a sidecar file and extract ``rdf:RDF`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:RDF`` tag.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: A expected tag is missing.
    """
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)

        if self._shorten_name(self._element.tag) != "rdf:RDF":
            raise NikonMissingTagError("rdf:RDF")


class NikonRDFDescription(NikonBaseProperties):
    """Nikon RDF Description container. (NOT USEFUL)

    This class parse a sidecar file and extract ``rdf:Description`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:Description`` tag.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.
    """
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)

        if self._shorten_name(self._element.tag) != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")


class NikonSDCProperties(NikonBaseProperties):
    """Nikon SDC properties container.

    This class parse a sidecar file and extract ``sdc`` tags (namespace
    'http://ns.nikon.com/sdc/1.0/').

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:Description`` tag.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    Attributes:
        about: Identifier of the sidecar file format. The identifier
            have to be ``nikon sidecar/1.0``.
        version: Version identifier of the sidecar format
        app_name: Name of the application that created the sidecar file.
        app_version: Version identifier of the application that created
            the sidecar file.
    """
    _ID = "nikon sidecar/1.0"
    about: str | None
    version: str | None
    app_name: str | None
    app_version: str | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.app_name = None
        self.version = None

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        for child in self._element:
            prefix = (self._shorten_name(child.tag)).split(":")[0]
            if prefix == "sdc":
                xmp_property = NikonXMPProperty(child)
                match xmp_property.name:
                    case("sdc:about"):
                        self.about = xmp_property.value
                        if self.about != self._ID:
                            raise NikonTagValueError("sdc:about", self.about)

                    case("sdc:version"):
                        self.version = xmp_property.value

                    case("sdc:appversion"):
                        self.app_version = xmp_property.value

                    case("sdc:appname"):
                        self.app_name = xmp_property.value

                    case _:
                        _logger.warning(
                            f"SDC property '{xmp_property.name}' is not known"
                            f" - ignored")

        _logger.debug(f"SDC property {self.about=}")
        _logger.debug(f"SDC property {self.version=}")
        _logger.debug(f"SDC property {self.app_version=}")
        _logger.debug(f"SDC property {self.app_name=}")


class NikonAsteroidProperties(NikonBaseProperties):
    """Nikon Asteroid properties container.

    This class parse a sidecar file and extract ``ast`` tags (namespace
    'http://ns.nikon.com/asteroid/1.0/').

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the ``rdf:Description`` tag.

    Raises:
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    Attributes:
        about: Identifier of the sidecar file format. The identifier
            have to be ``core-asteroid-tags``.
        version: version identifier of the sidecar format (currently
            ``11.0.0.3000``)
        xml_packets: `<https://www.exiftool.org/TagNames/XMP.html>`_
        gps: Object containing the GPS properties
        iptc: `<https://www.exiftool.org/TagNames/IPTC.html>`_
    """
    _ID = "core-asteroid-tags"
    about: str | None
    version: str | None
    xml_packets: bytes | None
    gps: NikonGPSProperty
    iptc: bytes | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.xml_packets = None
        self.gps = NikonGPSProperty()
        self.iptc = None

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        for child in self._element:
            prefix = (self._shorten_name(child.tag)).split(":")[0]
            if prefix == "ast":
                xmp_property = NikonXMPProperty(child)
                match xmp_property.name:
                    case "ast:about":
                        self.about = xmp_property.value
                        if self.about != self._ID:
                            raise NikonTagValueError("ast:about", self.about)

                    case "ast:version":
                        self.version = xmp_property.value

                    case "ast:XMLPackets":
                        self.xml_packets = xmp_property.value

                    case ("ast:GPSVersionID"):
                        self.gps.set_version_id(xmp_property.value)

                    case ("ast:GPSLatitudeRef"):
                        self.gps.set_latitude_ref(xmp_property.value)

                    case ("ast:GPSLatitude"):
                        self.gps.set_latitude(xmp_property.value)

                    case ("ast:GPSLongitudeRef"):
                        self.gps.set_longitude_ref(xmp_property.value)

                    case ("ast:GPSLongitude"):
                        self.gps.set_longitude(xmp_property.value)

                    case ("ast:GPSAltitudeRef"):
                        self.gps.set_altitude_ref(xmp_property.value)

                    case ("ast:GPSAltitude"):
                        self.gps.set_altitude(xmp_property.value)

                    case ("ast:GPSTimeStamp"):
                        self.gps.set_timestamp(xmp_property.value)

                    case ("ast:GPSDateStamp"):
                        self.gps.set_datestamp(xmp_property.value)

                    case ("ast:GPSStatus"):
                        self.gps.set_status(xmp_property.value)

                    case("ast:GPSMapDatum"):
                        self.gps.set_map_datum(xmp_property.value)

                    case("ast:GPSProcessingMethod"):
                        self.gps.set_processing_method(xmp_property.value)

                    case("ast:IPTC"):
                        self.iptc = xmp_property.value

                    case _:
                        _logger.warning(
                            f"AST property '{xmp_property.name}' is not known"
                            f" - {xmp_property.value=} ignored")

        _logger.debug(f"AST property {self.about=}")
        _logger.debug(f"AST property {self.version=}")
        _logger.debug(f"AST property {self.xml_packets=}")
        _logger.debug(f"AST property {self.gps=}")
        _logger.debug(f"AST property {self.gps.version_id=}")
        _logger.debug(f"AST property {self.gps.latitude_ref=}")
        _logger.debug(f"AST property {self.gps.latitude=}")
        _logger.debug(f"AST property {self.gps.longitude_ref=}")
        _logger.debug(f"AST property {self.gps.longitude=}")
        _logger.debug(f"AST property {self.gps.altitude_ref=}")
        _logger.debug(f"AST property {self.gps.altitude=}")
        if self.gps.timestamp is not None:
            _logger.debug(f"AST property {self.gps.timestamp.isoformat()=}")
        _logger.debug(f"AST property {self.gps.status=}")
        _logger.debug(f"AST property {self.gps.processing_method=}")
        _logger.debug(f"AST property {self.gps.map_datum=}")
        _logger.debug(f"AST property {self.iptc=}")


class NikonNineProperties(NikonBaseProperties):
    """Nikon Nine properties container.

    This class parse a sidecar file and extract ``nine`` tags (namespace
    'http://ns.nikon.com/nine/1.0/').

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
        nine_edits: `<https://www.exiftool.org/TagNames/Nikon.html#NineEdits>`_
        label:
        rating:
    """
    _ID = "nine-tags"
    about: str | None
    version: str | None
    nine_edits: str | None
    label: str | None
    rating: str | None
    trim: str | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.nine_edits = None
        self.label = None
        self.rating = None
        self.trim = None

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        for child in self._element:
            prefix = (self._shorten_name(child.tag)).split(":")[0]
            if prefix == "nine":
                xmp_property = NikonXMPProperty(child)
                match xmp_property.name:
                    case("nine:about"):
                        self.about = xmp_property.value
                        if self.about != self._ID:
                            raise NikonTagValueError("nine:about", self.about)

                    case("nine:version"):
                        self.version = xmp_property.value

                    case("nine:NineEdits"):
                        self.nine_edits = xmp_property.value

                    case ("nine:Label"):
                        self.label = xmp_property.value

                    case ("nine:Rating"):
                        self.rating = xmp_property.value

                    case ("nine:Trim"):
                        self.trim = xmp_property.value

                    case _:
                        _logger.warning(
                            f"NINE property '{xmp_property.name}' is not known"
                            f" - ignored")

        _logger.debug(f"NINE property {self.about=}")
        _logger.debug(f"NINE property {self.version=}")
        _logger.debug(f"NINE property {self.nine_edits=}")
        _logger.debug(f"NINE property {self.label=}")
        _logger.debug(f"NINE property {self.rating=}")
        _logger.debug(f"NINE property {self.trim=}")


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
        self._metadata = {}
        self._processing = {}
        self._data = None
        self._element = element
        self.sdc = None
        self.ast = None
        self.nine = None

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

        # Check the document header (x:xmptk)
        xmp_meta = NikonXMPMeta(self._element)
        _logger.debug(f"XMPTK : {xmp_meta.xmptk}")
        if xmp_meta.xmptk != "XMP Core 5.5.0":
            raise NikonTagValueError("x:xmptk", xmp_meta.xmptk)

        # Check RDF blocs (rdf:RDF)
        if len(self._element) != 1:
            raise NikonError("No or more than one child in 'x:xmpmeta'")
        for rdf_item in self._element:
            rdf = NikonRDF(rdf_item)
            # list
            for description_item in rdf_item:
                self.sdc = NikonSDCProperties(description_item)
                self.ast = NikonAsteroidProperties(description_item)
                self.nine = NikonNineProperties(description_item)
