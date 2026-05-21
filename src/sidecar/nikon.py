"""
The `sidecar.nikon` module implements handlers for the Nikon sidecar
file. The article named ":ref:`Inside Nikon Sidecar file`" details the
data structure and tags used by Nikon.

Using sidecar.nikon
-------------------
.. todo:: describe how using the module

sidecar.nikon reference manual
------------------------------
"""
import base64
import io
import logging
from xml.etree import ElementTree


__all__ = [
    "NikonError",
    "NikonMissingTagError",
    "NikonTagValueError",
    "NikonResourceError",
    "NikonResourceTypeError",
    "NikonSideCar",
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
    "NIKON_SUPPORTED_FORMAT"
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


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class NikonError(Exception):
    """
    Base class for sidecar parser exceptions.

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
    """
    Raised when an expected tag is missing.

    Args:
        name: name of the missing tag.

    Attributes:
        name: name of the missing tag.
    """
    name: str | None

    def __init__(self, name: str | None):
        self.name = name
        NikonError.__init__(self, f"Expected tag '{name}' is missing.")


class NikonTagValueError(NikonError):
    """
    Raised when a tag value is not expected.

    Args:
        name: name of the tag.
        value: value of the erroneous tag.

    Attributes:
        name: name of the tag.
        value: value of the erroneous tag.
    """
    name: str | None
    value: str | None

    def __init__(self, name: str, value: str | None):
        self.name = name
        self.value = value
        NikonError.__init__(self, f"Unexpected value '{value}' for the "
                                 f"tag '{name}'.")


class NikonResourceError(NikonError):
    """
    Raised when a resource is erroneous (unknown tag).

    Args:
        prop_name : name of the property
        tag_name: name of the erroneous tag.

    Attributes:
        prop_name : name of the property
        tag_name: name of the erroneous tag.
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
    """
    Raised when a resource is erroneous (unknown type).

    Args:
        prop_name : name of the property
        type_name: name of the erroneous type.

    Attributes:
        prop_name : name of the property
        type_name: name of the erroneous type.
    """
    prop_name: str | None
    type_name: str | None

    def __init__(self, prop_name: str | None, type_name: str | None):
        self.prop_name = prop_name
        self.type_name = type_name
        msg = f"Unknown type '{type_name}' used for the resource value of {prop_name} property"
        NikonError.__init__(self, msg)


class NikonBaseProperties(object):
    """
    Base class for Nikon Properties class.

    Args:
        element: XML element containing the metadata.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message`
            details the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

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
        """
        Shorten a tag or attribute name based on the namespace table.

        Args:
            expanded_name: name of the tag or attribute in expanded
                format (i.e. ``{uri}tag``). An empty string or without
                uri is accepted.

        Return:
            name in a short format (i.e. ``prefix:tag``). An empty
            string or without uri as :attr:`expanded_name` return the
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
        """
        Expand a tag or attribute name based on the namespace table.

        Args:
            short_name: name of the tag or attribute in short format
                (i.e. ``prefix:tag``). An empty string or without
                prefix is accepted.

        Returns:
            name in a expanded format (i.e. ``{uri}tag``). An empty
            string or without uri as :attr:`short_name` return the
            unchanged value.
        """
        if ":" in short_name:
            prefix, tag = short_name.split(":")
            expanded_name = "{{{}}}{}".format(self._namespaces[prefix], tag)
        else:
            expanded_name = short_name
        return expanded_name


class NikonXMPProperty(NikonBaseProperties):
    """
    Nikon XMP property.

    This class parses an XML element as a ``XMP`` property and decode
    the resource. The resource may be a simple text or a structured
    data identified with the ``rdf:parseType`` attribute.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: element containing the property.

    Raises:
        NikonResourceError: a resource is erroneous (unknown tag).
        NikonResourceTypeError: a resource is erroneous (unknown type)

    Attributes:
        name: not relevant here.
        value: property's value, the type of the attribute depends on the
            resource type (binary, double,...).
    """
    name: str
    value: None | str | float | int | bytes

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
                case "Binary": # Binary buffer
                    self.value = base64.b64decode(res_value)
                    _logger.debug("property {}: binary resource = {}".
                          format(self.name, self.value))

                case "Long": # Integer
                    bytes = base64.b64decode(res_value)
                    self.value = int.from_bytes(bytes, byteorder='little')
                    _logger.debug("property {}: long resource = {}".
                          format(self.name, self.value))

                case "Double": # List of float number
                    self.value = base64.b64decode(res_value)
                    _logger.debug("property {}: double resource = ({} bits) {}".
                          format(self.name,
                                 len(self.value)*8,
                                 self.value.hex(":")))

                case "Ascii": # ASCII string
                    self.value = res_value
                    _logger.debug("property {}: ascii resource = {}".
                          format(self.name, self.value))

                case _:
                    raise NikonResourceTypeError(self.name, res_type)

        else:
            # Simple valued XMP property
            self.value = element.text
            _logger.debug("property {}: xmltext = {}".
                  format(self.name, self.value))


class NikonXMPMeta(NikonBaseProperties):
    """
    Nikon XMP Meta container.

    This class parse a sidecar file and extract ``xmpmeta`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'x:xmpmeta' element.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: not relevant here.
        version: not relevant here.
        xmptk: the toolkit name ('XMP Core 5.5.0' for example)
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
            _logger.debug("{} = {}".format(name, element.attrib[name]))


class NikonRDF(NikonBaseProperties):
    """
    Nikon RDF container.

    This class parse a sidecar file and extract ``rdf:RDF`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'rdf:RDF' tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: not relevant here.
        version: not relevant here.
    """
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)

        if self._shorten_name(self._element.tag) != "rdf:RDF":
            raise NikonMissingTagError("rdf:RDF")


class NikonRDFDescription(NikonBaseProperties):
    """
    Nikon RDF Description container. (NOT USEFUL)

    This class parse a sidecar file and extract ``rdf:Description`` tags.

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'rdf:Description' tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: not relevant here.
        version: not relevant here.
    """
    def __init__(self, element: ElementTree.Element):
        super().__init__(element)

        if self._shorten_name(self._element.tag) != "rdf:Description":
            raise NikonMissingTagError("rdf:Description")


class NikonSDCProperties(NikonBaseProperties):
    """
    Nikon SDC properties container.

    This class parse a sidecar file and extract ``sdc`` tags (namespace
    'http://ns.nikon.com/sdc/1.0/').

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'rdf:Description' tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: identifier of the sidecar file format. The identifier
            have to be 'nikon sidecar/1.0'.
        version: version identifier of the sidecar format
        app_name: name of the application that created the sidecar file.
        app_version: version of the application that created the sidecar
            file.
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
                        _logger.warning("property '{}' is not known - "
                              "ignored".format(xmp_property.name))


class NikonAsteroidProperties(NikonBaseProperties):
    """
    Nikon Asteroid properties container.

    This class parse a sidecar file and extract ``ast`` tags (namespace
    'http://ns.nikon.com/asteroid/1.0/').

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'rdf:Description' tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: identifier of the sidecar file format. The identifier
            have to be 'core-asteroid-tags'.
        version: version identifier of the sidecar format (currently
            11.0.0.3000)
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
    xml_packets: str | None
    gps_version_id: str | None
    gps_latitude_ref: str | None
    gps_latitude: str | None
    gps_longitude_ref: str | None
    gps_longitude: str | None
    gps_map_datum: str | None
    iptc: str | None

    def __init__(self, element: ElementTree.Element):
        super().__init__(element)
        self.about = None
        self.version= None
        self.xml_packets = None
        self.gps_version_id = None
        self.gps_latitude_ref = 0
        self.gps_longitude_ref = 2
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0
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
                        self.gps_latitude = xmp_property.value

                    case ("ast:GPSLongitudeRef"):
                        self.gps_longitude_ref = xmp_property.value

                    case ("ast:GPSLongitude"):
                        self.gps_longitude = xmp_property.value

                    case("ast:GPSMapDatum"):
                        self.gps_map_datum = xmp_property.value

                    case("ast:IPTC"):
                        self.iptc = xmp_property.value

                    case _:
                        _logger.warning("property '{}' is not known - "
                              "ignored".format(xmp_property.name))


class NikonNineProperties(NikonBaseProperties):
    """
    Nikon Nine properties container.

    This class parse a sidecar file and extract ``nine`` tags (namespace
    'http://ns.nikon.com/nine/1.0/').

    The article named ":ref:`Inside Nikon Sidecar file`" details the data
    structure and tags used by Nikon.

    Args:
        element: XML element containing the 'rdf:Description' tag.

    Raises:
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

    Attributes:
        about: identifier of the sidecar file format. The identifier
            have to be 'nine-tags'.
        version: version identifier of the sidecar format (currently
            2.0.0)
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
                        _logger.warning("property '{}' is not known - "
                              "ignored".format(xmp_property.name))


class NikonSideCar(object):
    """
    Nikon Side car file.

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
        NikonError: generic error, the :attr:`NikonError.message` details
            the error.
        NikonMissingTagError: a tag value is not expected.
        NikonTagValueError: an expected tag is missing

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
            NikonMissingTagError: a tag value is not expected.
            NikonTagValueError: an expected tag is missing

        Returns:
            bool: `True` if the execution went well. In case of failure, an
            error log is written on the standard error (``stderr``).
        """

        # Check the document header (x:xmptk)
        xmp_meta = NikonXMPMeta(self._element)
        _logger.debug("XMPTK : {}".format(xmp_meta.xmptk))
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
