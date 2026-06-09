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


class NikonGPSProperty(NikonBaseProperties):
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

      * ``A`` measurement is in progress,
      * ``V`` measurement interrupted

    * ``GPSProcessingMethod``: The name of the method used for location
      finding (``GPS``, ``CELLID``, ``MANUAL``).
    * ``GPSMapDatum``: The geodetic survey data used by the GPS receiver.
      ``WGS-84`` is used in most cases.

    .. note:: others GPS properties are ignored.

    This class can be used in a formatted string and returns the latitude
    and longitude.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon. In a nutshell, Nikon seems to have
    using DICOM specification (see :ref:`InsideNKCS.GPSAttrTable`).

    Raises:
        ValueError: argument has the right type but an
            inappropriate value.

    Attributes:
        props: Dictionary of properties of the SDC set.
    """
    props: dict
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.props = {}

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        for child in self._element:
            if self._shorten_name(child.tag).startswith("ast:GPS"):
                xmp_property = NikonXMPProperty(child)
                match xmp_property.name:
                    case ("ast:GPSVersionID"):
                        # The version of GPS information as a binary string.
                        self.props["GPSVersionID"] \
                            = int.from_bytes(xmp_property.value, "little")

                    case ("ast:GPSLatitudeRef"):
                        # Whether the latitude is north (``0``) or south
                        # (``1``). *This attribute do not match with the
                        # DICOM specifications* [digps]_.
                        match xmp_property.value:
                            case 0:
                                self.props["GPSLatitudeRef"] = "N"

                            case 1:
                                self.props["GPSLatitudeRef"] = "S"

                            case _:
                                raise ValueError(
                                    f"Unsupported latitude reference "
                                    f"({xmp_property.value})")

                    case ("ast:GPSLatitude"):
                        # The latitude expressed in degrees-minutes-seconds
                        # as a set of three floating number.
                        self.props["GPSLatitude"] \
                            = self._from_dms(xmp_property.value)

                    case ("ast:GPSLongitudeRef"):
                        # Whether the longitude is east (``2``) or west
                        # (``3``). *This attribute do not match with the
                        # DICOM specifications* [digps]_.
                        match xmp_property.value:
                            case 2:
                                self.props["GPSLongitudeRef"] = "E"

                            case 3:
                                self.props["GPSLongitudeRef"] = "W"

                            case _:
                                raise ValueError(
                                    f"Unsupported longitude reference "
                                    f"({xmp_property.value})")

                    case ("ast:GPSLongitude"):
                        # The longitude expressed in degrees-minutes-seconds
                        # as a set of three floating number.
                        self.props["GPSLongitude"] \
                            = self._from_dms(xmp_property.value)

                    case ("ast:GPSAltitudeRef"):
                        # The altitude used as the reference altitude in
                        # meters as a binary string.
                        self.props["GPSAltitudeRef"] \
                            = int.from_bytes(xmp_property.value, 'little')

                    case ("ast:GPSAltitude"):
                        # The altitude based on the reference in
                        # ``GPSAltitudeRef`` in meters.
                        self.props["GPSAltitude"] = xmp_property.value

                    case ("ast:GPSTimeStamp"):
                        self._set_timestamp(xmp_property.value)

                    case ("ast:GPSDateStamp"):
                        self._set_datestamp(xmp_property.value)

                    case ("ast:GPSStatus"):
                        # The status of the GPS receiver when the image is
                        # recorded. ``A`` measurement is in progress, ``V``
                        # measurement interrupted.
                        match xmp_property.value:
                            case "A" | "V":
                                self.props["GPSStatus"] = xmp_property.value

                            case _:
                                raise ValueError(
                                    f"Unsupported longitude reference "
                                    f"({xmp_property.value})")

                    case("ast:GPSMapDatum"):
                        # The geodetic survey data used by the GPS receiver.
                        # ``WGS-84`` is used in most cases.
                        self.props["GPSMapDatum"] = xmp_property.value

                    case("ast:GPSProcessingMethod"):
                        # The name of the method used for location
                        # finding as a set of two fixed strings ended by NULL
                        # characters.
                        type = str(xmp_property.value[0:7].strip(b"\x00"),
                                   encoding='ascii')
                        if type != "ASCII":
                            raise ValueError(
                                f"Processing method encoding is unknown "
                                f"({type})")
                        else:
                            self.props["GPSProcessingMethod"]\
                                = str(xmp_property.value[8:].strip(b"\x00"),
                                      encoding='ascii')

                    case("ast:IPTC"):
                        self.props[xmp_property.name] = xmp_property.value

                    case _:
                        _logger.warning(
                            f"GPS property '{xmp_property.name}' is not known"
                            f" - {xmp_property.value=} ignored")

        for key in list(self.props):
            _logger.info(f"GPS property {key}={self.props[key]}")

    def _set_timestamp(self, timestamp: list[float]):
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
        if "GPSDateTimeStamp" in self.props:
            self.props["GPSDateTimeStamp"] \
                = dt.datetime.combine(self.timestamp, time)
        else:
            self.props["GPSDateTimeStamp"] = time

    def _set_datestamp(self, datestamp: str):
        """Set the datetime stamp.

        Args:
            datestamp: The date as a string in the format: YYYY:MM:DD.
                *This attribute do not match with the DICOM
                specifications* [digps]_.

        Raises:
            ValueError: argument has the right type but an
                inappropriate value.
        """
        date = dt.date.strptime(datestamp, "%Y:%m:%d")
        if "GPSDateTimeStamp" in self.props:
            self.props["GPSDateTimeStamp"] \
                = dt.datetime.combine(date, self.props["GPSDateTimeStamp"])
        else:
            self.props["GPSDateTimeStamp"] = date

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

        The method format the latitude and the longitude coordinate as two
        number expressed in decimal degree (5 precision digits) and the
        reference as suffix.

        lat: ll.lllll (r), long: lll.lllll (r)
        """
        s = ""
        if "GPSLatitude" in self.props and "GPSLongitude" in self.props:
            s = (f"lat: {self.props["GPSLatitude"]:.5f} "
                 f"({self.props["GPSLatitudeRef"]}) "
                 f"long: {self.props["GPSLongitude"]:.5f} "
                 f"({self.props["GPSLongitudeRef"]})")
        return s


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
    'http://ns.nikon.com/sdc/1.0/'). The properties read are copied into
    the attribute :attr:`props` which can contain the following entries:

    * ``sdc:appname``: Name of the application that created the sidecar
      file.
    * ``sdc:appversion``: Version identifier of the application that
      created the sidecar file.

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
        version: Version identifier of the sidecar format.
        props: Dictionary of properties of the SDC set.
    """
    _ID = "nikon sidecar/1.0"
    about: str | None
    version: str | None
    props: dict
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.props = {}

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        for child in self._element:
            prefix = (self._shorten_name(child.tag)).split(":")[0]
            if prefix == "sdc":
                xmp_property = NikonXMPProperty(child)
                match xmp_property.name:
                    case "sdc:about":
                        self.about = xmp_property.value
                        if self.about != self._ID:
                            raise NikonTagValueError("sdc:about", self.about)

                    case "sdc:version":
                        self.version = xmp_property.value

                    case "sdc:appversion":
                        self.props['appversion'] = xmp_property.value

                    case "sdc:appname":
                        self.props['appname'] = xmp_property.value

                    case _:
                        _logger.warning(
                            f"SDC property '{xmp_property.name}' is not known"
                            f" - ignored")

        _logger.info(f"SDC property {self.about=}")
        _logger.info(f"SDC property {self.version=}")
        _logger.info(f"SDC property {self.props=}")
        for key in list(self.props):
            _logger.info(f"SDC property {key}={self.props[key]}")


class NikonAsteroidProperties(NikonBaseProperties):
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
        NikonError: Generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: A tag value is not expected.
        NikonTagValueError: An expected tag is missing.

    Attributes:
        about: Identifier of the sidecar file format. The identifier
            have to be ``core-asteroid-tags``.
        version: version identifier of the sidecar format (currently
            ``11.0.0.3000``)
        props: Dictionary of properties of the SDC set.
    """
    _ID = "core-asteroid-tags"
    about: str | None
    version: str | None
    props: dict
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.props = {}

        name = self._shorten_name(self._element.tag)
        if name != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")

        self.props["GPS"] = NikonGPSProperty(self._element)
        for child in self._element:
            prefix = (self._shorten_name(child.tag)).split(":")[0]
            if prefix == "ast":
                xmp_property = NikonXMPProperty(child)
                if not xmp_property.name.startswith("ast:GPS"):
                    match xmp_property.name:
                        case "ast:about":
                            self.about = xmp_property.value
                            if self.about != self._ID:
                                raise NikonTagValueError(
                                    "ast:about", self.about)

                        case "ast:version":
                            self.version = xmp_property.value

                        case "ast:XMLPackets":
                            self.props["XMLPackets"] = xmp_property.value

                        case("ast:IPTC"):
                            self.props["IPTC"] = xmp_property.value

                        case _:
                            _logger.warning(
                                f"AST property '{xmp_property.name}' is not known"
                                f" - {xmp_property.value=} ignored")

        _logger.info(f"AST property about={self.about}")
        _logger.info(f"AST property version={self.version}")
        for key in list(self.props):
            _logger.info(f"AST property {key}={self.props[key]}")
        for key in list(self.props["GPS"].props):
            _logger.info(f"AST property {key}={self.props["GPS"].props[key]}")


class NikonNineProperties(NikonBaseProperties):
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
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.trim = None
        self.props = {}

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
                        self.props["NineEdits"] = xmp_property.value

                    case ("nine:Label"):
                        self.props["Label"] = xmp_property.value

                    case ("nine:Rating"):
                        self.props["Rating"] = xmp_property.value

                    case ("nine:Trim"):
                        self.trim = xmp_property.value

                    case _:
                        _logger.warning(
                            f"NINE property '{xmp_property.name}' is not known"
                            f" - ignored")

        _logger.info(f"NINE property about={self.about}")
        _logger.info(f"NINE property version={self.version}")
        for key in list(self.props):
            _logger.info(f"NINE property {key}={self.props[key]}")
        _logger.info(f"NINE property trim={self.trim}")


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
        if "GPS" in self.ast.props:
            is_geotagged = self.ast.props["GPS"].is_completed
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

