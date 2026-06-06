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
from xml.etree import ElementTree

from library.ieee754 import IEEE754

__all__ = [
    "NikonError",
    "NikonMissingTagError",
    "NikonTagValueError",
    "NikonResourceError",
    "NikonResourceTypeError",
    "NikonBaseProperties",
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
                    _logger.debug(f"property {self.name}: "
                                  f"binary resource = {self.value}")
                # Integer
                case "Long":
                    buffer = base64.b64decode(res_value)
                    self.value = int.from_bytes(buffer, byteorder='little')
                    _logger.debug(f"property {self.name}: "
                                  f"long resource = {self.value}")

                # List of float number (IEEE754 Double precision 64-bits)
                case "Double":
                    self.value = []
                    value = base64.b64decode(res_value)
                    for i in range(len(value) // 8):
                        self.value.append(IEEE754(value[i*8 : (i+1)*8]).value)
                        _logger.debug(
                            f"property {self.name}: "
                            f"double resource ({i}) = {self.value[i]} "
                            f"({value[i*8 : (i+1)*8].hex(':')})")

                # ASCII string
                case "Ascii":
                    self.value = res_value
                    _logger.debug("property {self.name}: "
                                  "ascii resource = {self.value}")

                case _:
                    raise NikonResourceTypeError(self.name, res_type)

        else:
            # Simple valued XMP property
            self.value = element.text
            _logger.debug(f"property {self.name}: xmltext = {self.value}")


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
                            f"property '{xmp_property.name}' is not known"
                            f" - ignored")


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
        gps_version_id: todo
        gps_latitude_ref: 0 = North, 1 = South
        gps_latitude:
        gps_longitude_ref: 2 = East, 3 = West
        gps_longitude:
        gps_map_datum:
        iptc: `<https://www.exiftool.org/TagNames/IPTC.html>`_
    """
    _ID = "core-asteroid-tags"
    about: str | None
    version: str | None
    xml_packets: bytes | None
    gps_version_id: bytes | None
    gps_latitude_ref: int | None
    gps_latitude: float | None
    gps_longitude_ref: int | None
    gps_longitude: float | None
    gps_map_datum: str | None
    iptc: bytes | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.xml_packets = None
        self.gps_version_id = None
        self.gps_latitude_ref = None
        self.gps_longitude_ref = None
        self.gps_latitude = None
        self.gps_longitude = None
        self.gps_map_datum = None

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
                        self.gps_version_id = xmp_property.value

                    case ("ast:GPSLatitudeRef"):
                        self.gps_latitude_ref = xmp_property.value

                    case ("ast:GPSLatitude"):
                        self.gps_latitude = self._from_dms(xmp_property.value)
                        _logger.debug(f"property {self.gps_latitude=}")

                    case ("ast:GPSLongitudeRef"):
                        self.gps_longitude_ref = xmp_property.value

                    case ("ast:GPSLongitude"):
                        self.gps_longitude = self._from_dms(xmp_property.value)
                        _logger.debug(f"property {self.gps_latitude=}")

                    case("ast:GPSMapDatum"):
                        self.gps_map_datum = xmp_property.value

                    case("ast:IPTC"):
                        self.iptc = xmp_property.value

                    case _:
                        _logger.warning(
                            f"property '{xmp_property.name}' is not known"
                            f" - ignored")

    def _from_dms(self, dms: list[float | None]):
        """Get coordinate in decimal degrees.

        The method convert a coordinate expressed in degrees-minutes-seconds
        in decimal degrees. This method can accept one to three float.

        Returns:
            float: coordinate in decimal degrees .
        """
        div = 1
        dd = 0.0
        for c in dms:
            if c is not None:
                dd = dd + c / div
                div = div * 60
        return dd


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
                            f"property '{xmp_property.name}' is not known"
                            f" - ignored")


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
    def __init__(self, element: ElementTree.Element):
        self._metadata = {}
        self._processing = {}
        self._data = None
        self._element = element

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
                sdc = NikonSDCProperties(description_item)
                asteroid = NikonAsteroidProperties(description_item)
                nine = NikonNineProperties(description_item)
