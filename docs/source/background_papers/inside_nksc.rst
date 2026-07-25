:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

*************************
Inside Nikon Sidecar file
*************************

NX Studio (and the previous software as View-NX2, ViewNX-i, Capture
NX-D) may save image adjustments to :term:`sidecar` files in an ``NKSC_PARAM``
folder within the same folder as the original image [nksave]_.

A sidecar file is a file based on the :term:`Extensible Metadata Platform`
(:term:`XMP`) specification from Adobe. XMP data are serialized using the
`RDF/XML Syntax Specification <http://www.w3.org/TR/2004/
REC-rdf-syntax-grammar-20040210/>`_ [adxmp1]_.

.. note:: Adobe provide a free of charge SDK written in C++, but as the script
    focuses on Nikon sidecar file, I don't use this SDK to avoid to have
    additional software to install.

In a nutshell, a sidecar file is a XMP packet with the image metadata
serialized as XMP properties. Each property have a name and a value. A value
may a simple value as XML text element, or a structured value (named resource)
with a type (``astype:Type``) and a value (``rdf:value``).

These properties are grouped per set identified by a namespace [adxmp1]_, a
Nikon sidecar file contains the following sets:

* **sdc** (``http://ns.nikon.com/sdc/1.0/``): identify the software which
  created the image (here ``NX Studio 1.10W``) and the version of the sidecar
  file format (here ``nikon sidecar/1.0``).

* **ast** (``http://ns.nikon.com/asteroid/1.0/``): contains *geolocation data*
  and *image metadata*. These metadata are a subset of `Dublin Core Metadata
  Initiative <https://www.dublincore.org/specifications/dublin-core/
  dcmi-terms/>`_ and `IPTC metadata <https://www.iptc.org/std/
  photometadata/specification/IPTC-PhotoMetadata>`_.

  * **geolocation data**: are the geolocation data coming from a GPS receiver
    or manually added. These data are in a set of separated data whose name
    begins by ``GPS...``. Go to the article
    :ref:`background_papers/inside_geoloc:Inside Nikon GPS Information` for
    more details.

  * **image metadata**: are serialized in a :term:`XMP Packet`
    (``ast:XMLPackets`` element) as
    :ref:`XMP Properties <background_papers/inside_nksc:XMP properties in a nutshell>`
    and in :term:`IPTC IIM` records as
    :ref:`IIM properties <background_papers/inside_nksc:IIM properties in a nutshell>`.
    These two parts are embedded as a structure valued XMP property encoded
    in Base64.

* **nine** (``http://ns.nikon.com/nine/1.0/``): contains the image adjustments
  history in XML format with escaped characters (&lt;..). Theses image
  processing modules are proprietary and cannot be transferred in an other
  software except for format adjustment as cropping. The
  `background_papers/inside_adjustment:Inside Nikon image adjustments` section
  details the supported Nikon settings and indicates whether their parameters
  can be converted into the equivalent module of Darktable.

No public specifications are available from Nikon, so the attributes
were discovered by reading ``.nksc`` files and the help of ExifTool
by Phil Harvey [phniktag]_.

XMP properties in a nutshell
============================

An XMP property may be a simple text, a structured data identified with the
``rdf:parseType`` attribute, or an array (see section 7.3 to 7.9 [adxmp1]_).

A structured data may either a typed value or a list of sub-properties. A typed
value have two sub-properties: its value in ``rdf:value`` element, its type in
``astype:Type`` element. This format is a Nikon's proprietary format.

IIM properties in a nutshell
============================

The Information Interchange Model consists of a number of records [IIMv4]_.
Image metadata are stored in an 'Application Record' (DataSets in the
range 2:xx). As only a subset of IPTC properties is recognized, others
datasets are simply ignored (see [IIMv4]_, p. 16).


.. table:: Layout of :term:`IPTC IIM` record
    :name: background_papers/inside_nksc:Layout_IPTC_IIM

    +----------+--------+---------+---------------+---------+
    | 1 byte   | 1 byte | 1 byte  | 2 bytes       | n bytes |
    +----------+--------+---------+---------------+---------+
    | Tag      | Record | DataSet | Length [#bo]_ | Value   |
    +----------+--------+---------+---------------+---------+


Example ``Title`` field (alias XMP ``dc:title`` property)::

    |0x1c|0x02|0x05|0x00 0x13|[Description] Titre|

.. rubric:: Notes

.. [#bo] Use Big Endian Byte Ordering (the left-most byte the most
   significant bytes (see [IIMv4]_, p. 6.)


.. rubric:: References
.. [nksave] Nikon, `[Save] <https://nikonimglib.com/nxstdo/onlinehelp/en
    /save_80.html>`_, Options > [Save]

.. [nkadj] Nikon, `The Adjustments Tab <https://nikonimglib.com/nxstdo/
    onlinehelp/en/the_adjustments_tab_20.html>`_, Enhancing Pictures >
    The Adjustments Tab

.. [phniktag] Phil Harvey, `Nikon Tags <https://www.exiftool.org/
    TagNames/Nikon.html>`_
    , Tag Names > Nikon

