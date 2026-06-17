.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Inside Nikon Sidecar file
=========================
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
with a type (``astype:Type``) and a value (``rad:value``)  .

These properties are grouped per set identified by a namespace [adxmp1]_, a
Nikon sidecar file contains the following sets:

* **sdc** (``http://ns.nikon.com/sdc/1.0/``): identify the software which
  created the image (here ``NX Studio 1.10W``) and the version of the sidecar
  file format (here ``nikon sidecar/1.0``).

* **ast** (``http://ns.nikon.com/asteroid/1.0/``): contains image's metadata
  serialized in a RDF packet encoded in Base64. These metadata are a subset of
  `Dublin Core Metadata Initiative <https://www.dublincore.org/specifications/
  dublin-core/dcmi-terms/>`_ and `IPTC metadata <https://www.iptc.org/std/
  photometadata/specification/IPTC-PhotoMetadata>`_.

* **astype** (``http://ns.nikon.com/asteroid/Types/1.0/``): contains the
  localisation data (GPS) and a copy of above metadata encoded in binary.

* **nine** (``http://ns.nikon.com/nine/1.0/``): contains the image adjustments
  history in XML format with escaped characters (&lt;..). Theses image
  processing modules are proprietary and cannot be transferred in an other
  software except for format filter as cropping. The `Nikon adjustments`
  section details the supported Nikon settings and indicates whether their
  parameters can be converted into the equivalent module of Darktable.

No public specifications are available from Nikon, so the attributes
were discovered by reading ``.nsks`` files and the help of ExifTool
by Phil Harvey [phniktag]_.

GPS Information
---------------
Nikon seems to have using DICOM specification [digps]_ for GPS Information. So
attributes definitions used in classes are based on this document. Data elements
representation are defined in [direg]_ and [dienc]_. The
:numref:`InsideNKCS.GPSAttrTable` details the GPS attribute (tagname and
encoding currently used in Nikon sidecar files, but some properties (marked
with a '*' do not comply with the specifications (see `Not compliant properties`)

.. table:: GPS Attributes in NKSC files
    :name: InsideNKCS.GPSAttrTable

    =========================== =================== =========== ==========
    Name                        Tag name            VR [#vr]_   VM [#vm]_
    =========================== =================== =========== ==========
    GPS Version ID              GPSVersionID        OB          1
    GPS Altitude                GPSAltitude         DS          1
    GPS Altitude Ref            GPSAltitudeRef      US          1
    GPS Date Stamp*             GPSDateStamp        DT          1
    GPS Dest Bearing Ref [#db]_ GPSDestBearingRef   CS          1
    GPS Dest Bearing [#db]_     GPSDestBearing      DS          1
    GPS Img Direction           GPSImgDirection     DS          1
    GPS Img Direction Ref       GPSImgDirectionRef  CS          1
    GPS Latitude                GPSLatitude         DS          3
    GPS Latitude Ref*           GPSLatitudeRef      CS          1
    GPS Longitude               GPSLongitude        DS          3
    GPS Longitude Ref*          GPSLongitudeRef     CS          1
    GPS Map Datum               GPSMapDatum         UT          1
    GPS Processing Method*      GPSProcessingMethod OB          1
    GPS Speed                   GPSSpeed            DS          1
    GPS Speed Ref               GPSSpeedRef         CS          1
    GPS Status                  GPSStatus           CS          1
    GPS Time Stamp*             GPSTimeStamp        DT          1
    =========================== =================== =========== ==========

.. rubric:: Notes

.. [#vr] Value Representation (VR)
.. [#vm] Value Multiplicity (VM)
.. [#db] This property is ignored as it contains the same information as 'Img
    Direction'. (See on jpeg images produced by an iPhone XS Max).

Value Representation (VR) Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Other Byte (OB)**: An octetstream where the encoding of the contents is
  specified by the negotiated Transfer Syntax. Transfer Syntaxes require the
  use of 'Little Endian Byte Ordering' (see [diob]_]).
* **Code string (CS)**: A string of characters.
* **Decimal String (DS)**: A string of characters representing either a fixed
  point number or a floating point number.
* **Unsigned Short (US)**: Unsigned binary integer 16 bits long.
* **Date Time (DT)**: A concatenated datetime character string in the format:
  ``YYYYMMDDHHMMSS.FFFFFF&ZZXX``
* **Unlimited Text (UT)**: A character string that may contain one or more
  paragraphs.

.. note:: This table is a simplified version of value representation
    specified in DICOM specification. Please refer to [dienc]_ for having more
    information.

Not compliant properties
^^^^^^^^^^^^^^^^^^^^^^^^

**GPS reference** (``GPSLongitudeRef`` and ``GPSLatitudeRef``) are espressed as
integer and not a character.

**Timestamps** (``GPSDateStamp`` and ``GPSTimeStamp``) are expressed as a string
as a string in the format ``YYYY:MM:DD`` and in hours-minutes-seconds as a set
of three floating number respectively.

**Processing Method** do not clearly defines in DICOM specifications [digps]_. An
analysis show a set of two fixed strings (resp. 8 and 66 characters in ASCII)
ended by NULL characters.

Nikon adjustments
-----------------

THe Nikon adjustments are the following:

.. hlist::
    :columns: 2

    * `nik::GaussianBlur`
    * `nik::GrainNoise`
    * `nik::LCH`
    * `nik::LevelsCurves`
    * `nik::Straighten`
    * `nikon::ActiveDLighting`
    * `nikon::ApplicationData`
    * `nikon::Brightness`
    * `nikon::ChrAb`
    * `nikon::ColorBalance`
    * `nikon::ColorBooster`
    * `nikon::ColorShift`
    * `nikon::DLightingHQ`
    * `nikon::DLightingHS`
    * `nikon::Dehaze`
    * `nikon::Diffraction`
    * `nikon::Distortion`
    * `nikon::DustOff`
    * `nikon::ExposureSettings`
    * `nikon::FishEye`
    * `nikon::Flare`
    * `nikon::LEGeneral`
    * `nikon::LongChrAb`
    * `nikon::NXHistory`
    * `nikon::NoiseReduction`
    * `nikon::Perspective`
    * `nikon::PhotoEffects`
    * `nikon::PictureControl`
    * `nikon::PixelShiftNoiseReduction`
    * `nikon::QuickFixContrast`
    * `nikon::QuickFixToneCurve`
    * `nikon::RedEye`
    * `nikon::SizeRes`
    * `nikon::SkinSoftening`
    * `nikon::SkinTone`
    * `nikon::UnsharpMask`
    * `nikon::Vignette`
    * `nikon::WhiteBalance`
    * `nikon::transform`

Adjustment parameters
^^^^^^^^^^^^^^^^^^^^^

An adjustment parameter is characterized by its name, its type, and its value.
Parameter type may be implicit or explicit. An explicit type is expressed by
a tag name (``integer``, ``double``...) and within an attribute defining the
parameter name (``name``, ``id``...). An implicit type is not specified, the
tag name only defines the parameter name.

Adjustment parameters type
^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``binary``: is a binary string encoded in Base64. The attribute
  ``name`` define the parameter name. (seems similar to ``Export``
  parameters)
* ``double``: a decimal number or a double precision (64 bits) floating
  number. The attribute ``name`` define the parameter name.
* ``integer``: a decimal number, a single precision (32 bits) floating
  number or a boolean value with ``true`` or ``false`` [#int]_. The
  attribute ``name`` define the parameter name.
* ``dateAndTime``: a date and time stamp expressed as a set of tags
  (``year``, ``month``, ``day``, ``hour``, ``minute`` and ``second``).
  The date 1900-1-1 00:00:00 seems to be default value.
* ``points``: a 2D coordinates expressed as a set of tag
  ``pointOfPoints`` with the attributes ``x`` and ``y``. The attribute
  ``name`` define the parameter name.
* ``data``: a text string. The attribute ``id`` define the parameter name.

The list below exposes particaler case of implicit adjustment parameters.

* ``Export``: a binary string expressed as a set of two elements:
  ``ExportData`` and ``ExportDataSize``. ``ExportData`` is a binary string
  encoded in Base64. ``ExportDataSize`` is the length of the **encoded**
  string.
* ``map``: similar to ``Export`` but with ``mapData`` and ``mapSize`` as
  elements

.. rubric:: Notes

.. [#int] ``integer`` and ``double`` types are almost identical except
    that integer can be a boolean. Floating-point numbers are usually
    implemented using double in C, so single precision and double precision are
    converted in `float` number.


nikon::ColorShift
^^^^^^^^^^^^^^^^^

nikon::DLightingHS
^^^^^^^^^^^^^^^^^^

nikon::WhiteBalance
^^^^^^^^^^^^^^^^^^^^^

nik::Straighten
^^^^^^^^^^^^^^^^^

nikon::PictureControl
^^^^^^^^^^^^^^^^^^^^^^^

nikon::QuickFixToneCurve
^^^^^^^^^^^^^^^^^^^^^^^^^^

nik::GaussianBlur
^^^^^^^^^^^^^^^^^^^

nikon::LEGeneral
^^^^^^^^^^^^^^^^^^

nikon::FishEye
^^^^^^^^^^^^^^^^

nikon::Dehaze
^^^^^^^^^^^^^^^

nikon::ColorBalance
^^^^^^^^^^^^^^^^^^^^^

nikon::Flare
^^^^^^^^^^^^^^

nikon::SkinTone
^^^^^^^^^^^^^^^^^

nikon::Vignette
^^^^^^^^^^^^^^^^^

nikon::Perspective
^^^^^^^^^^^^^^^^^^^^

nikon::ChrAb
^^^^^^^^^^^^^^

nikon::UnsharpMask
^^^^^^^^^^^^^^^^^^^^

nikon::ColorBooster
^^^^^^^^^^^^^^^^^^^^^

nikon::NXHistory
^^^^^^^^^^^^^^^^^^

nikon::SkinSoftening
^^^^^^^^^^^^^^^^^^^^^^

nik::LevelsCurves
^^^^^^^^^^^^^^^^^^^

nikon::RedEye
^^^^^^^^^^^^^^^

nikon::Diffraction
^^^^^^^^^^^^^^^^^^^^

nikon::Distortion
^^^^^^^^^^^^^^^^^^^

nikon::ApplicationData
^^^^^^^^^^^^^^^^^^^^^^^^

nikon::LongChrAb
^^^^^^^^^^^^^^^^^^

nikon::ExposureSettings
^^^^^^^^^^^^^^^^^^^^^^^^^

nik::LCH
^^^^^^^^^^

nikon::QuickFixContrast
^^^^^^^^^^^^^^^^^^^^^^^^^

nik::GrainNoise
^^^^^^^^^^^^^^^^^

nikon::DustOff
^^^^^^^^^^^^^^^^

nikon::transform
^^^^^^^^^^^^^^^^^^

nikon::SizeRes
^^^^^^^^^^^^^^^^

nikon::PhotoEffects
^^^^^^^^^^^^^^^^^^^^^

nikon::Brightness
^^^^^^^^^^^^^^^^^^^

nikon::ActiveDLighting
^^^^^^^^^^^^^^^^^^^^^^^^

nikon::NoiseReduction
^^^^^^^^^^^^^^^^^^^^^^^

nikon::PixelShiftNoiseReduction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

nikon::DLightingHQ
^^^^^^^^^^^^^^^^^^^^

.. rubric:: References
.. [nksave] Nikon, `[Save] <https://nikonimglib.com/nxstdo/onlinehelp/en
    /save_80.html>`_, Options > [Save]

.. [nkadj] Nikon, `The Adjustments Tab <https://nikonimglib.com/nxstdo/
    onlinehelp/en/the_adjustments_tab_20.html>`_, Enhancing Pictures >
    The Adjustments Tab

.. [phniktag] Phil Harvey, `Nikon Tags <https://www.exiftool.org/
    TagNames/Nikon.html>`_
    , Tag Names > Nikon

.. [adxmp1] Adobe, `XMP Specification Part 1 <https://github.com/adobe/
    XMP-Toolkit-SDK/blob/main/docs/XMPSpecificationPart1.pdf>`_, pp. 5-17

.. [digps] DICOM, PS3.3 2026b - Information Object Definitions, `VL
    Photographic Geolocation Module <https://dicom.nema.org/medical/
    dicom/current/output/chtml/part03/sect_C.8.12.12.html>`_

.. [direg] DICOM, PS3.6 2026b - Data Dictionary, `Registry of DICOM
    Data Elements <https://dicom.nema.org/medical/dicom/current/
    output/chtml/part06/chapter_6.html>`_

.. [dienc] DICOM, PS3.5 2026b - Data Structures and Encoding, `Value
    Representation (VR) <https://dicom.nema.org/medical/dicom/
    current/output/chtml/part05/sect_6.2.html>`_

.. [diob] DICOM, PS3.5 2026b - Data Structures and Encoding, `Little
    Endian Byte Ordering <https://dicom.nema.org/medical/dicom/current/
    output/chtml/part05/sect_7.3.html>`_
