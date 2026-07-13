:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Inside nikon::PictureControl
============================

This tool allow to adjust Picture Control settings for the SDR tone range
of RAW pictures and merged pixel shift pictures, particularly to achieve
a black-and-white image or saturated colors. [nkpc]_

.. figure:: /images/picturecontrol_recorded_values.png
   :name: background_papers/nikon_picturecontrol:PCRecordedValue
   :scale: 66%
   :align: center

   Picture Control tool settings pane (Out of the box image).

This article describes parameters of the Picture Control image adjustment
expressed as a XML element as shown below. The point to note is the ``Export``
parameter expressed as an obscure data, so this article focuses on it and
exposes the internal structure of this item. The methodology is based on
changing parameters in the control pane and observe the changes in ``Export``
data block.

..  code-block:: XML
    :caption: nikon::PictureControl sample

    <filter id="nikon::PictureControl">
        <active>true</active>
        <parameters>
            <Export>
                <ExportData>TkNQAAAAAAEA...A&#xA;////AAAAAA==&#xA;</ExportData>
                <ExportDataSize>74</ExportDataSize>
            </Export>
            <SelectedPictureControl>0</SelectedPictureControl>
            <AutoContrast>255</AutoContrast>
            <AutoSaturation>255</AutoSaturation>
            <SelectedPictureControlVersion2>0</SelectedPictureControlVersion2>
            <SavedPicConProcess>1</SavedPicConProcess>
            <PictureControl>0</PictureControl>
        </parameters>
    </filter>

There are three parameters variants:
`background_papers/nikon_picturecontrol:Camera compatible`,
`background_papers/nikon_picturecontrol:Latest Picture Control` and
`background_papers/nikon_picturecontrol:Custom Tone Curve`. Each of these
variants have its own obscure data structure as explained in the further
sections, but based on the same layout. In a nutshell, parameters are
serialized in a record composed of several data sets as shown below.

+------------+-------------+------------+-----------+-----+----------------+
| 4 bytes    | 4 bytes     | 4 bytes    | n bytes   | ... |     4 bytes    |
+------------+-------------+------------+-----------+-----+----------------+
| **Record** | **DataSet** | **Length** | **Value** | ... | **End Marker** |
+------------+-------------+------------+-----------+-----+----------------+

* **Record**: is the identifier of the record (value set at
  ``b'NCP\x0'``).
* **DataSet**: is the identifier of the data set.
* **Length**: is the length in bytes of the data set (Big Endian Byte
  Ordering).
* **Value**: is the value of the data set. A data set may be a simple
  value or a structured one (see further sections for more details.
* **...**: is the next dataset if any.
* **End Marker**: is the identifier of the end of the record (value set
  at 0).

Camera compatible
-----------------
For this variant, there one fixed length data set (id: 1, length: 52 bytes).
Picture control settings are linearized in a buffer.

..  code-block:: hexdump
    :name: :name: background_papers/nikon_picturecontrol:PCCCData
    :caption: Camera compatible ExportData sample

    0000  4e 43 50 00 00 00 00 01  00 00 00 24 30 31 30 30  |NCP........$0100|
    0010  53 54 41 4e 44 41 52 44  00 00 00 00 00 00 00 00  |STANDARD........|
    0020  00 00 00 00 00 01 00 80  83 80 80 80 80 ff ff ff  |................|
    0030  00 00 00 00                                       |....            |

The below table exposes the layout of the picture control setting buffer
starting at offset 0x0c.

+-------------------+----------+--------+-------------------------------+
| Setting           | Length   | Offset | Value                         |
+===================+==========+========+===============================+
| Version           | 4 bytes  | 00     | Fixed string: '0100'          |
+-------------------+----------+--------+-------------------------------+
| Control Name      | 19 bytes | 04     | Picture Control Name expressed|
|                   |          |        | as a null terminated string.  |
|                   |          |        |                               |
|                   |          |        | * ``STANDARD`` (SD)           |
|                   |          |        | * ``NEUTRAL`` (NL)            |
|                   |          |        | * ``VIVID`` (VI)              |
|                   |          |        | * ``MONOCHROME`` (MC          |
|                   |          |        | * ``PORTRAIT`` (PT)           |
|                   |          |        | * ``LANDSCAPE`` (LS)          |
+-------------------+----------+--------+-------------------------------+
| Control Id        | 2 bytes  | 23     | Picture control identifier.   |
|                   |          |        |                               |
|                   |          |        | * SD: ``0x0001``              |
|                   |          |        | * NL: ``0x03C2``              |
|                   |          |        | * VI: ``0x00C3``              |
|                   |          |        | * MC: ``0x064D``              |
|                   |          |        | * PT: ``0x0486``              |
|                   |          |        | * LS: ``0x04C7``              |
+-------------------+----------+--------+-------------------------------+
| Custom            | 1 bytes  | 25     | Indicates the setting's       |
|                   |          |        | customization level.          |
|                   |          |        |                               |
|                   |          |        | * ``0x00``: no customization  |
|                   |          |        | * ``0x01``: Quick Adjust used |
|                   |          |        | * ``0x02``: Custom            |
+-------------------+----------+--------+-------------------------------+
| Quick Adjust      | 1 bytes  | 26     | * 0x7C..0x82: biased [#bs]_   |
|                   |          |        |   (-2..2)                     |
+-------------------+----------+--------+-------------------------------+
| Sharpening        | 1 bytes  | 27     | * 0x00: auto                  |
|                   |          |        | * 0x80..0x89: biased [#bs]_   |
|                   |          |        |   (0..9)                      |
+-------------------+----------+--------+-------------------------------+
| Contrast          | 1 bytes  | 28     | * 0x00: auto                  |
|                   |          |        | * 0x7D..0x83: biased [#bs]_   |
|                   |          |        |   (-3..3)                     |
+-------------------+----------+--------+-------------------------------+
| Brightness        | 1 bytes  | 29     | * 0x7F..0x81: biased [#bs]_   |
|                   |          |        |   (-1..1)                     |
+-------------------+----------+--------+-------------------------------+
| Saturation        | 1 bytes  | 30     | * 0x00: auto                  |
|                   |          |        | * 0x7D..0x83: biased [#bs]_   |
|                   |          |        |   (-3..3)                     |
+-------------------+----------+--------+-------------------------------+
| Hue               | 1 bytes  | 31     | * 0x7D..0x83: biased [#bs]_   |
|                   |          |        |   (-3..3)                     |
+-------------------+----------+--------+-------------------------------+
| Filter Effect     | 1 bytes  | 32     | Simulate the effects of color |
|                   |          |        | filters on B&W pictures.      |
|                   |          |        |                               |
|                   |          |        | * ``0xff``: no value          |
|                   |          |        | * ``0x80``: none              |
|                   |          |        | * ``0x81``: yellow            |
|                   |          |        | * ``0x82``: orange            |
|                   |          |        | * ``0x83``: red               |
|                   |          |        | * ``0x84``: green             |
+-------------------+----------+--------+-------------------------------+
| Toning            | 1 bytes  | 33     | Choose a tint for B&W         |
|                   |          |        | pictures.                     |
|                   |          |        |                               |
|                   |          |        | * ``0xff``: no value          |
|                   |          |        | * ``0x80``: B&W               |
|                   |          |        | * ``0x81``: sepia             |
|                   |          |        | * ``0x82``: cyanotype         |
|                   |          |        | * ``0x83``: red               |
|                   |          |        | * ``0x84``: yellow            |
|                   |          |        | * ``0x85``: green             |
|                   |          |        | * ``0x86``: blue-green        |
|                   |          |        | * ``0x87``: blue              |
|                   |          |        | * ``0x88``: purple-blue       |
|                   |          |        | * ``0x89``: reddish-purple    |
+-------------------+----------+--------+-------------------------------+
| Adjust Saturation | 1 bytes  | 34     | Adjust the saturation of the  |
|                   |          |        | tint selected for 'Toning'    |
|                   |          |        | expected for 'B&W'.           |
|                   |          |        |                               |
|                   |          |        | * ``0xff``: no value          |
|                   |          |        | * 0x81..87: biased [#bs]_     |
|                   |          |        |   (1..7)                      |
+-------------------+----------+--------+-------------------------------+

.. figure:: /images/picturecontrol_MC.png
   :name: background_papers/nikon_picturecontrol:PCMC
   :scale: 66%
   :align: center

   Picture Control tool settings pane for Monochrome control selected.

.. [#bs] The setting value is biased, the value stored is offset from the actual
   value by the value bias (here 0x80). Biasing is done because settings have
   to be signed values.

Latest Picture Control
----------------------

.. figure:: /images/picturecontrol_latest.png
   :name: background_papers/nikon_picturecontrol:PCLatest
   :scale: 66%
   :align: center

   Picture Control tool settings pane (Latest).


Custom Tone Curve
-----------------





This article details the internal structure of this parameters


.. rubric:: References
.. [nkpc] Nikon, `The Picture Controls Tool <https://nikonimglib.com/
   nxstdo/onlinehelp/en/the_picture_controls_tool_22.html>`_, Adjustments >
   Basic Edit Palettes > Picture Control