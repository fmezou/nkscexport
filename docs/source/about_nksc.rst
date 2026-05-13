.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Nikon Sidecar file
==================
NX Studio (and the previous software as View-NX2, ViewNX-i, Capture
NX-D) may save image adjustments to :term:`sidecar` files in an ``NKSC_PARAM``
folder within the same folder as the original image [nksc]_.

Inside Nikon Sidecar file
-------------------------
A sidecar file is a file based on the :term:`Extensible Metadata Platform`
(:term:`XMP`) specification from Adobe. Adobe provide a free of charge SDK
written in C++, but as the script focuses on Nikon sidecar file, I don't use
this SDK to avoid to have additional software to install.

In a nutshell, a sidecar have several sections stored in a :term:`Resource
Description Framework` (:term:`RDF`) block, each of these sections have its
own namespaces [#f1]_:

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
  software except for format filter as cropping.

No public specifications are available from Nikon, so the attributes
were discovered by reading ``.nsks`` files and the help of ExifTool
by Phil Harvey [phniktag]_.

Transferable filter
-------------------

.. todo:: list the tansferable filter. The below list are for memory

    * nikon::ColorShift
    * nikon::DLightingHS
    * nikon::WhiteBalance
    * nik::Straighten
    * nikon::PictureControl
    * nikon::QuickFixToneCurve
    * nik::GaussianBlur
    * nikon::LEGeneral
    * nikon::FishEye
    * nikon::Dehaze
    * nikon::ColorBalance
    * nikon::Flare
    * nikon::SkinTone
    * nikon::Vignette
    * nikon::Perspective
    * nikon::ChrAb
    * nikon::UnsharpMask
    * nikon::ColorBooster
    * nikon::NXHistory
    * nikon::SkinSoftening
    * nik::LevelsCurves
    * nikon::RedEye
    * nikon::Diffraction
    * nikon::Distortion
    * nikon::ApplicationData
    * nikon::LongChrAb
    * nikon::ExposureSettings
    * nik::LCH
    * nikon::QuickFixContrast
    * nik::GrainNoise
    * nikon::DustOff
    * nikon::transform
    * nikon::SizeRes
    * nikon::PhotoEffects
    * nikon::Brightness
    * nikon::ActiveDLighting
    * nikon::NoiseReduction
    * nikon::PixelShiftNoiseReduction
    * nikon::DLightingHQ

nikon::ColorShift
^^^^^^^^^^^^^^^^^^^

nikon::DLightingHS
^^^^^^^^^^^^^^^^^^^^

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
.. [nksc] NX Studio Help,
    https://nikonimglib.com/nxstdo/onlinehelp/en/save_80.html
.. [phniktag] Nikon Tags,
    https://www.exiftool.org/TagNames/Nikon.html

.. rubric:: Footnotes
.. [#f1] namespace use URL format but they don't exist (not resolved)
