:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

********
Glossary
********

.. glossary::
    :sorted:

    sidecar files
    sidecar
    .nksc
        File used to save image adjustments. This file may be in a folder or
        within the same folder as the original image. Because changes are not
        applied directly to the original image data, pictures can be edited
        repeatedly with no loss in quality. Sidecar files are also used to store
        labels, ratings, XMP/IPTC metadata, and other data in addition to image
        adjustments.

    Extensible Metadata Platform
    XMP
        XMP standardizes a data model, a serialization format and core
        properties for the definition and processing of extensible metadata
        embedded into popular image, video and document file formats (JPEG and
        PDF...). Although metadata can alternatively be stored in a sidecar
        file, embedding metadata avoids problems that occur when metadata is
        stored separately [adxmp]_.

        .. seealso::
            * `Extensible Metadata Platform SDK - Adobe
              <https://www.adobe.com/devnet/xmp.html>`_
            * `XMP-Toolkit-SDK - GitHub
              <https://github.com/adobe/XMP-Toolkit-SDK/>`_  |Invertocat|

    XMP Packet
        An XMP packet is a set of XMP metadata properties. Each property has a
        name and a value. Each property name in an XMP packet shall be unique
        within that packets [adxmp1]_. An XMP Packet is serialized using a
        subset of the :term:`RDF` metadata syntax. A single XMP packet shall be
        serialized using a single ``rdf:RDF`` XML element.

    IPTC Information Interchange Model
    IPTC IIM
        The IIM standard defines for each field for what purposes it may be
        used and how the value is stored as binary data. It is still in use,
        mainly by “IPTC Fields” for photo metadata. Metadata elements of IIM
        are quite well-known as “IPTC fields” in the “IPTC header” of digital
        image files.

        The :term:`Extensible Metadata Platform` (XMP) has superseded IIM's
        image file header structure, but the properties of the IPTC Core
        are synchronized between the technical structures of XMP and IIM by
        a vast majority of imaging software.

        .. seealso::
            * `Information Interchange Model (IIM) - IPTC
              <https://www.iptc.org/IIM/>`_

    International Press Telecommunications Council
    IPTC
        It is a consortium of the world's news agencies, other news providers
        and news industry vendors and acts as the global standards body of the
        news media.

        The IPTC defined a set of metadata properties that can be applied
        to images, part of a broader standard developed in the early 1990s
        and known as the :term:`IPTC Information Interchange Model` (IIM).

        .. seealso::
            * `International Press Telecommunications Council - Wikipedia
              <https://en.wikipedia.org/wiki/International_Press_
              Telecommunications_Council>`_

    Resource Description Framework
    RDF
        The Resource Description Framework is a method to describe and exchange
        graph data. It was originally designed as a data model for metadata by
        the World Wide Web Consortium (W3C).

        .. seealso::
            * `Resource Description Framework - Wikipedia
              <https://en.wikipedia.org/wiki/Resource_Description_Framework>`_


.. rubric:: References

.. [adxmp] Adobe Developer, `Overview of XMP technology,
    <https://developer.adobe.com/xmp/docs/xmp-specifications/#overview-of-xmp-technology>`_

.. [adxmp1] Adobe, `XMP Specification Part 1 <https://github.com/adobe/
    XMP-Toolkit-SDK/blob/main/docs/XMPSpecificationPart1.pdf>`_, pp. 5-17

.. [IIMv4] IPTC, `Information Interchange Model Version 4 <https://www.iptc.org
   /std/IIM/4.2/specification/IIMV4.2.pdf>`_, pp. 11-13, pp. 24-44

.. |Invertocat| image:: assets/github/GitHub_Invertocat_Black_Clearspace.*
    :alt: Invertocat
    :align: top
    :width: 20
