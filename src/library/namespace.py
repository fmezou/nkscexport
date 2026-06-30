"""Handle XML namespaces.

The :mod:`library.namespace` module manage XML name by expanding or
shortening name based on `namespaces <https://en.wikipedia.org/
wiki/XML_namespace>`_. It is mainly used to keep XML name in a short form to
smooth the name of metadata or image adjustment in report or source code.

Using ``namespace``
-------------------

For this short tutorial, we have a dummy XML document which use the namespace
``http://ns.nikon.com/nine/1.0/`` associated to the ``nine`` prefix used as
sample.

.. code-block:: XML
   :caption: XML dummy document

    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about=""
                         xmlns:nine="http://ns.nikon.com/nine/1.0/">
            <nine:about>nine-tags</nine:about>
            <nine:version>2.0.0</nine:version>
        </rdf:Description>
    </rdf:RDF>

We create an instance of :class:`NameSpace` with the pair prefix, URI as
declared with ``xmlns`` attribute (here nine=
"http://ns.nikon.com/nine/1.0/"). This pair is expressed as a dictionnary
with the prefix as key.

>>> from library.namespace import NameSpace
>>> ns = NameSpace({"nine": "http://ns.nikon.com/nine/1.0/"})

We can expand or shorten the XML name.

>>> ns.expand_name("nine:about")
'{http://ns.nikon.com/nine/1.0/}about'
>>> ns.shorten_name("{http://ns.nikon.com/nine/1.0/}about")
'nine:about'

Reference
---------

.. autoclass:: NameSpace
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:
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
            ``{"nine": "http://ns.nikon.com/nine/1.0/"}``
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
