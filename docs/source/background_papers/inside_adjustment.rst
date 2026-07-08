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

    * `background_papers/nik_adaptivepaste:Inside nik::AdaptivePaste`
    * `background_papers/nik_crop:Inside nik::Crop`
    * `background_papers/nik_gaussianblur:Inside nik::GaussianBlur`
    * `background_papers/nik_grainnoise:Inside nik::GrainNoise`
    * `background_papers/nik_lch:Inside nik::LCH`
    * `background_papers/nik_levelscurves:Inside nik::LevelsCurves`
    * `background_papers/nik_newton:Inside nik::Newton`
    * `background_papers/nik_rotate:Inside nik::Rotate`
    * `background_papers/nik_straighten:Inside nik::Straighten`
    * `background_papers/nikon_activedlighting:Inside nikon::ActiveDLighting`
    * `background_papers/nikon_applicationdata:Inside nikon::ApplicationData`
    * `background_papers/nikon_brightness:Inside nikon::Brightness`
    * `background_papers/nikon_chrab:Inside nikon::ChrAb`
    * `background_papers/nikon_colorbalance:Inside nikon::ColorBalance`
    * `background_papers/nikon_colorbooster:Inside nikon::ColorBooster`
    * `background_papers/nikon_colorshift:Inside nikon::ColorShift`
    * `background_papers/nikon_dehaze:Inside nikon::Dehaze`
    * `background_papers/nikon_diffraction:Inside nikon::Diffraction`
    * `background_papers/nikon_distortion:Inside nikon::Distortion`
    * `background_papers/nikon_dlightinghq:Inside nikon::DLightingHQ`
    * `background_papers/nikon_dlightinghs:Inside nikon::DLightingHS`
    * `background_papers/nikon_dustoff:Inside nikon::DustOff`
    * `background_papers/nikon_exposuresettings:Inside nikon::ExposureSettings`
    * `background_papers/nikon_fisheye:Inside Nikon::FishEye`
    * `background_papers/nikon_flare:Inside nikon::Flare`
    * `background_papers/nikon_legeneral:Inside nikon::LEGeneral`
    * `background_papers/nikon_longchrab:Inside nikon::LongChrAb`
    * `background_papers/nikon_noisereduction:Inside nikon::NoiseReduction`
    * `background_papers/nikon_nxhistory:Inside nikon::NXHistory`
    * `background_papers/nikon_perspective:Inside nikon::Perspective`
    * `background_papers/nikon_photoeffects:Inside nikon::PhotoEffects`
    * `background_papers/nikon_picturecontrol:Inside nikon::PictureControl`
    * `background_papers/nikon_pixelshiftnoisereduction:Inside nikon::PixelShiftNoiseReduction`
    * `background_papers/nikon_quickfixcontrast:Inside nikon::QuickFixContrast`
    * `background_papers/nikon_quickfixtonecurve:Inside nikon::QuickFixToneCurve`
    * `background_papers/nikon_redeye:Inside nikon::RedEye`
    * `background_papers/nikon_sizeres:Inside nikon::SizeRes`
    * `background_papers/nikon_skinsoftening:Inside nikon::SkinSoftening`
    * `background_papers/nikon_skintone:Inside nikon::SkinTone`
    * `background_papers/nikon_transform:Inside nikon::transform`
    * `background_papers/nikon_unsharpmask:Inside nikon::UnsharpMask`
    * `background_papers/nikon_vignette:Inside nikon::Vignette`
    * `background_papers/nikon_whitebalance:Inside nikon::WhiteBalance`

Adjustment parameters
=====================

An adjustment parameter is characterized by its name, its type, and its value.
Parameter type may be implicit or explicit. An explicit type is expressed by
a tag name (``integer``, ``double``...) and within an attribute defining the
parameter name (``name``, ``id``...). An implicit type is not specified, the
tag name only defines the parameter name.

.. code-block:: XML

   <SelectedPictureControl>0</SelectedPictureControl>

   <double name="rotateAngle">0</double>

Adjustment parameters type
==========================

* ``binary``: is a binary string encoded in Base64. The attribute
  ``name`` define the parameter name. (seems similar to ``Export``
  parameters)

  .. code-block:: XML

     <binary name="Data">AAAAAADI...AAAAAA</binary>


* ``double``: a decimal number or a double precision (64 bits) floating
  number. The attribute ``name`` define the parameter name.

  .. code-block:: XML

     <double name="rotateAngle">0</double>

* ``integer``: a decimal number, a single precision (32 bits) floating
  number or a boolean value with ``true`` or ``false`` [#int]_. The
  attribute ``name`` define the parameter name.

  .. code-block:: XML

     <integer name="autoCrop">0</integer>

* ``dateAndTime``: a date and time stamp expressed as a set of tags
  (``year``, ``month``, ``day``, ``hour``, ``minute`` and ``second``).
  The date 1900-1-1 00:00:00 seems to be default value.

  .. code-block:: XML

     <dateAndTime>
        <year>1900</year>
        <month>1</month>
        <day>1</day>
        <hour>0</hour>
        <minute>0</minute>
        <second>0</second>
     </dateAndTime>

* ``points``: a set of 2D coordinates expressed as a set of tags
  ``pointOfPoints`` with the attributes ``x`` and ``y``. The attribute
  ``name`` define the parameter name.

  .. code-block:: XML

     <points name="QuickFixToneCurve.pointsOut">
        <pointOfPoints x="0" y="0"/>
        <pointOfPoints x="1" y="1"/>
     </points>

* ``point``: a 2D coordinates expressed as a set of attributes (``x``
  and ``y``). The attribute ``name`` define the parameter name. Please
  note that data structure is not the same than ``points`` above.

  .. code-block:: XML

     <point name="cropStart" x="991" y="546"/>

* ``data``: a text string. The attribute ``id`` define the parameter name.

  .. code-block:: XML

     <data id="app:softname">Nikon Transfer 2.13 W</data>

The list below exposes particular cases of implicit adjustment parameters.

* ``Export``: a binary string expressed as a set of two elements:
  ``ExportData`` and ``ExportDataSize``. ``ExportData`` is a binary string
  encoded in Base64. ``ExportDataSize`` is the length of the **encoded**
  string.

  .. code-block:: XML

     <Export>
        <ExportData>TkNQAAAAAAEAAAA...AAA==</ExportData>
        <ExportDataSize>74</ExportDataSize>
     </Export>

* ``map``: similar to ``Export`` but with ``mapData`` and ``mapSize`` as
  elements

  .. code-block:: XML

     <map>
        <mapdata>rhn0ugeaaa.../qkpfvli</mapdata>
        <mapsize>174338</mapsize>
     </map>

* ``historystep``: an ordered list whose entries are tagged vith
  ``historystep``. Each entry (aka. step) is an unitary image adjustment
  to apply to the image. For example, cropping an image should be done after
  image processing modifying the image size as lens correction or perspective
  controls).

  .. code-block:: XML

     <historystep>
        <version>20</version>
           <feather>0</feather>
           ...
           <filter id="nik::AdaptivePaste">
           ...
           </filter>
     </historystep>
     <historystep>
        <version>20</version>
           <feather>0</feather>
           ...
           <filter id="nik::Newton">
           ...
           </filter>
     </historystep>


* ``adjustmentData``: an obscure data structure with one item named
  ``NkOneStepAdjustment`` expressed as a boolean:

  .. code-block:: XML

      <adjustmentData>
          <data id="NkOneStepAdjustment">true</data>
      </adjustmentData>


.. rubric:: Notes

.. [#int] ``integer`` and ``double`` types are almost identical except
    that integer can be a boolean. Floating-point numbers are usually
    implemented using double in C, so single precision and double precision are
    converted in `float` number.
