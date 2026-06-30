:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

******************************
Inside Nikon image adjustments
******************************

THe Nikon image adjustments (aka. filters) are the following:

.. hlist::
    :columns: 2

    * `background_papers/inside_adjustment:nik::GaussianBlur`
    * `background_papers/inside_adjustment:nik::GrainNoise`
    * `background_papers/inside_adjustment:nik::LCH`
    * `background_papers/inside_adjustment:nik::LevelsCurves`
    * `background_papers/inside_adjustment:nik::Straighten`
    * `background_papers/inside_adjustment:nikon::ActiveDLighting`
    * `background_papers/inside_adjustment:nikon::ApplicationData`
    * `background_papers/inside_adjustment:nikon::Brightness`
    * `background_papers/inside_adjustment:nikon::ChrAb`
    * `background_papers/inside_adjustment:nikon::ColorBalance`
    * `background_papers/inside_adjustment:nikon::ColorBooster`
    * `background_papers/inside_adjustment:nikon::ColorShift`
    * `background_papers/inside_adjustment:nikon::DLightingHQ`
    * `background_papers/inside_adjustment:nikon::DLightingHS`
    * `background_papers/inside_adjustment:nikon::Dehaze`
    * `background_papers/inside_adjustment:nikon::Diffraction`
    * `background_papers/inside_adjustment:nikon::Distortion`
    * `background_papers/inside_adjustment:nikon::DustOff`
    * `background_papers/inside_adjustment:nikon::ExposureSettings`
    * `background_papers/inside_adjustment:nikon::FishEye`
    * `background_papers/inside_adjustment:nikon::Flare`
    * `background_papers/inside_adjustment:nikon::LEGeneral`
    * `background_papers/inside_adjustment:nikon::LongChrAb`
    * `background_papers/inside_adjustment:nikon::NXHistory`
    * `background_papers/inside_adjustment:nikon::NoiseReduction`
    * `background_papers/inside_adjustment:nikon::Perspective`
    * `background_papers/inside_adjustment:nikon::PhotoEffects`
    * `background_papers/inside_adjustment:nikon::PictureControl`
    * `background_papers/inside_adjustment:nikon::PixelShiftNoiseReduction`
    * `background_papers/inside_adjustment:nikon::QuickFixContrast`
    * `background_papers/inside_adjustment:nikon::QuickFixToneCurve`
    * `background_papers/inside_adjustment:nikon::RedEye`
    * `background_papers/inside_adjustment:nikon::SizeRes`
    * `background_papers/inside_adjustment:nikon::SkinSoftening`
    * `background_papers/inside_adjustment:nikon::SkinTone`
    * `background_papers/inside_adjustment:nikon::UnsharpMask`
    * `background_papers/inside_adjustment:nikon::Vignette`
    * `background_papers/inside_adjustment:nikon::WhiteBalance`
    * `background_papers/inside_adjustment:nikon::transform`

Adjustment parameters
=====================

An adjustment parameter is characterized by its name, its type, and its value.
Parameter type may be implicit or explicit. An explicit type is expressed by
a tag name (``integer``, ``double``...) and within an attribute defining the
parameter name (``name``, ``id``...). An implicit type is not specified, the
tag name only defines the parameter name.

Adjustment parameters type
==========================

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
=================

nikon::DLightingHS
==================

nikon::WhiteBalance
===================

nik::Straighten
===============

nikon::PictureControl
=====================

nikon::QuickFixToneCurve
========================

nik::GaussianBlur
=================

nikon::LEGeneral
================

nikon::FishEye
==============

nikon::Dehaze
=============

nikon::ColorBalance
===================

nikon::Flare
============

nikon::SkinTone
===============

nikon::Vignette
===============

nikon::Perspective
==================

nikon::ChrAb
============

nikon::UnsharpMask
==================

nikon::ColorBooster
===================

nikon::NXHistory
================

nikon::SkinSoftening
====================

nik::LevelsCurves
=================

nikon::RedEye
=============

nikon::Diffraction
==================

nikon::Distortion
=================

nikon::ApplicationData
======================

nikon::LongChrAb
================

nikon::ExposureSettings
=======================

nik::LCH
========

nikon::QuickFixContrast
=======================

nik::GrainNoise
===============

nikon::DustOff
==============

nikon::transform
================

nikon::SizeRes
==============

nikon::PhotoEffects
===================

nikon::Brightness
=================

nikon::ActiveDLighting
======================

nikon::NoiseReduction
=====================

nikon::PixelShiftNoiseReduction
===============================

nikon::DLightingHQ
==================

