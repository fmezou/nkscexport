"""Handle XML namespaces.

The `library.namespace` module manage XML name by expanding or shortening
name based on `namespaces <https://en.wikipedia.org/wiki/XML_namespace>`_.

The exported classes, exceptions and functions (and any other objects)
are as follows:

Classes
-------
.. hlist::
    :columns: 2

    * :class:`NameSpace` -- XML Namespace basic tools


Using ``namespace``
-------------------

>>> from library.namespace import NameSpace
>>> ns = NameSpace({"x": "adobe:ns:meta/"})
>>> ns.expand_name("x:xmptk")
'{adobe:ns:meta/}xmptk'
>>> ns.shorten_name("{adobe:ns:meta/}xmptk")
'x:xmptk'

Reference manual
----------------
"""
import logging


__all__ = [
    "NameSpace"
]


# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class NameSpace:
    """XML Namespace basic tools.

    This class offers method to shorten or expand XML name base on a
    namespace dictionary.

    Args:
        namespaces: Dictionary containing the nanapace prefix and assiocted
            namespace uri as defined in ``xmlns`` attribute. Example:
            ``ns = {"x": "adobe:ns:meta/"}``
    """
    _ns: dict
    _rev_ns: dict
    def __init__(self, namespaces: dict):
        # Build reverse XML Namespaces table for shortening attribute names
        self._ns = namespaces
        self._rev_ns = {}
        for p, u in namespaces.items():
            self._rev_ns[u] = p

    def shorten_name(self, name: str) -> str:
        """Shorten a tag or attribute name based on the namespace table.

        Args:
            name: Name of the tag or attribute in expanded format (i.e.
                ``{uri}tag``). An empty string or without uri is accepted.

        Return:
            Name in a short format (i.e. ``prefix:tag``). An empty
            string or without uri in :data:`expanded_name` returns the
            unchanged value.
        """
        if "}" in name:
            uri, tag = name.split("}")
            short_name = "{}:{}".format(self._rev_ns[uri.removeprefix("{")], tag)
        else:
            short_name = name

        return short_name

    def expand_name(self, name: str) -> str:
        """Expand a tag or attribute name based on the namespace table.

        Args:
            name: Name of the tag or attribute in short format (i.e.
                ``prefix:tag``). An empty string or without prefix is
                accepted.

        Returns:
            Name in expanded format (i.e. ``{uri}tag``). An empty
            string or without prefix in :data:`short_name` return the
            unchanged value.
        """
        if ":" in name:
            prefix, tag = name.split(":")
            expanded_name = "{{{}}}{}".format(self._ns[prefix], tag)
        else:
            expanded_name = name
        return expanded_name
