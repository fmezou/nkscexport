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
        stored separately [adxmp01]_.

        .. seealso::
            * `Extensible Metadata Platform SDK - Adobe
              <https://www.adobe.com/devnet/xmp.html>`_
            * `XMP-Toolkit-SDK - GitHub
              <https://github.com/adobe/XMP-Toolkit-SDK/>`_  |Invertocat|

    Resource Description Framework
    RDF
        The Resource Description Framework is a method to describe and exchange
        graph data. It was originally designed as a data model for metadata by
        the World Wide Web Consortium (W3C).

        .. seealso::
            * `Resource Description Framework - Wikipedia
              <https://en.wikipedia.org/wiki/Resource_Description_Framework>`_


.. rubric:: References

.. [adxmp01] Adobe Developer, `Overview of XMP technology,
    <https://developer.adobe.com/xmp/docs/xmp-specifications/#overview-of-xmp-technology>`_

.. |Invertocat| image:: images/GitHub_Invertocat_Black_Clearspace.*
    :alt: Invertocat
    :align: top
    :width: 20
