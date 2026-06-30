:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

****************************
Inside Nikon GPS Information
****************************

Nikon seems to have using DICOM specification [digps]_ for GPS Information. So
attributes definitions used in classes are based on this document. Data elements
representation are defined in [direg]_ and [dienc]_. The
:numref:`background_papers/inside_geoloc:GPSAttributes` details the GPS attribute
(tagname and encoding currently used in Nikon sidecar files, but some properties
(marked with a '*' do not comply with the specifications (see
`background_papers/inside_geoloc:Not compliant properties`)

.. table:: GPS Attributes in NKSC files
    :name: background_papers/inside_geoloc:GPSAttributes

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
====================================

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
========================

**GPS reference** (``GPSLongitudeRef`` and ``GPSLatitudeRef``) are espressed as
integer and not a character.

**Timestamps** (``GPSDateStamp`` and ``GPSTimeStamp``) are expressed as a string
as a string in the format ``YYYY:MM:DD`` and in hours-minutes-seconds as a set
of three floating number respectively.

**Processing Method** do not clearly defines in DICOM specifications [digps]_. An
analysis show a set of two fixed strings (resp. 8 and 66 characters in ASCII)
ended by NULL characters.

.. rubric:: References

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