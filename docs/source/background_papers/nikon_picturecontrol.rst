:github_url:

.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Inside nikon::PictureControl
============================

This tool allow to adjust Picture Control settings for the SDR tone range of
RAW pictures and merged pixel shift pictures, particularly to achieve a
black-and-white image or saturated colors. [nkpc]_

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
Tones are processed using the Picture Controls for the camera that took the
picture. Also, the sample used may vary from one camera model to another (here
Nikon D70s or Nikon D7100).

There is one fixed length data set (id: 1, length: 52 bytes). Picture control
settings are linearized in a buffer.

..  code-block:: hexdump
    :name: :name: background_papers/nikon_picturecontrol:PCCCData
    :caption: Camera compatible ExportData sample

    0000  4e 43 50 00 00 00 00 01  00 00 00 24 30 31 30 30  |NCP........$0100|
    0010  53 54 41 4e 44 41 52 44  00 00 00 00 00 00 00 00  |STANDARD........|
    0020  00 00 00 00 00 01 00 80  83 80 80 80 80 ff ff ff  |................|
    0030  00 00 00 00                                       |....            |

The below table exposes the layout of the picture control setting buffer
starting at offset 0x0c.

.. note:: Setting values are biased, the value stored is offset from the actual
   value by the value bias (here 0x80). Biasing is done because settings have
   to be signed values.

+-------------------+----------+--------+-------------------------------------+
| Setting           | Length   | Offset | Value                               |
+===================+==========+========+=====================================+
| Version           | 4 bytes  | 00     | Fixed string: '0100'                |
+-------------------+----------+--------+-------------------------------------+
| ControlName       | 20 bytes | 04     | Null terminated string.             |
|                   |          |        |                                     |
|                   |          |        | * SD: ``STANDARD``                  |
|                   |          |        | * NL: ``NEUTRAL``                   |
|                   |          |        | * VI: ``VIVID``                     |
|                   |          |        | * MC: ``MONOCHROME``                |
|                   |          |        | * PT: ``PORTRAIT``                  |
|                   |          |        | * LS: ``LANDSCAPE``                 |
+-------------------+----------+--------+-------------------------------------+
| ControlId         | 2 bytes  | 23     | * SD: ``0x0001``                    |
|                   |          |        | * NL: ``0x03C2``                    |
|                   |          |        | * VI: ``0x00C3``                    |
|                   |          |        | * MC: ``0x064D``                    |
|                   |          |        | * PT: ``0x0486``                    |
|                   |          |        | * LS: ``0x04C7``                    |
+-------------------+----------+--------+-------------------------------------+
| Custom            | 1 byte   | 25     | Customization level.                |
|                   |          |        |                                     |
|                   |          |        | * ``0x00``: no customization        |
|                   |          |        | * ``0x01``: Quick Adjust used       |
|                   |          |        | * ``0x02``: Custom                  |
+-------------------+----------+--------+-------------------------------------+
| QuickAdjust       | 1 byte   | 26     | * biased (-2..2)                    |
+-------------------+----------+--------+-------------------------------------+
| Sharpening        | 1 byte   | 27     | * ``0x00``: auto                    |
|                   |          |        | * biased (0..9)                     |
+-------------------+----------+--------+-------------------------------------+
| Contrast          | 1 byte   | 28     | * ``0x00``: auto                    |
|                   |          |        | * biased (-3..3)                    |
+-------------------+----------+--------+-------------------------------------+
| Brightness        | 1 byte   | 29     | * biased (-1..1)                    |
+-------------------+----------+--------+-------------------------------------+
| Saturation        | 1 byte   | 30     | * ``0x00``: auto                    |
|                   |          |        | * biased (-3..3)                    |
+-------------------+----------+--------+-------------------------------------+
| Hue               | 1 byte   | 31     | * 0x7D..0x83: biased (-3..3)        |
+-------------------+----------+--------+-------------------------------------+
| FilterEffect      | 1 byte   | 32     | Color filters on B&W pictures.      |
|                   |          |        |                                     |
|                   |          |        | * ``0xff``: no value                |
|                   |          |        | * ``0x80``: none                    |
|                   |          |        | * ``0x81``: yellow                  |
|                   |          |        | * ``0x82``: orange                  |
|                   |          |        | * ``0x83``: red                     |
|                   |          |        | * ``0x84``: green                   |
+-------------------+----------+--------+-------------------------------------+
| Toning            | 1 byte   | 33     | Tint for B&W pictures.              |
|                   |          |        |                                     |
|                   |          |        | * ``0xff``: no value                |
|                   |          |        | * ``0x80``: B&W                     |
|                   |          |        | * ``0x81``: sepia                   |
|                   |          |        | * ``0x82``: cyanotype               |
|                   |          |        | * ``0x83``: red                     |
|                   |          |        | * ``0x84``: yellow                  |
|                   |          |        | * ``0x85``: green                   |
|                   |          |        | * ``0x86``: blue-green              |
|                   |          |        | * ``0x87``: blue                    |
|                   |          |        | * ``0x88``: purple-blue             |
|                   |          |        | * ``0x89``: reddish-purple          |
+-------------------+----------+--------+-------------------------------------+
| AdjustSaturation  | 1 byte   | 34     | Saturation of the tint (see Toning) |
|                   |          |        |                                     |
|                   |          |        | * ``0xff``: no value (Toning=0x80)  |
|                   |          |        | * biased (1..7)                     |
+-------------------+----------+--------+-------------------------------------+

.. figure:: /images/picturecontrol_MC.png
   :name: background_papers/nikon_picturecontrol:PCMC
   :scale: 66%
   :align: center

   Picture Control tool settings pane for Monochrome control selected.

Latest Picture Control
----------------------
Tones are processed using the latest Picture Controls. Picture Controls and
parameters added with recent cameras can be applied to RAW pictures taken
with models that do not offer these options.

.. figure:: /images/picturecontrol_latest.png
   :name: background_papers/nikon_picturecontrol:PCLatest
   :scale: 66%
   :align: center

   Picture Control tool settings pane (Latest).

The record (length: 392 bytes) contains several dataset (id fom 0x00000100 to
0x00000200).

..  code-block:: hexdump
    :name: :name: background_papers/nikon_picturecontrol:PCLPCData
    :caption: Camera compatible ExportData sample

    0000  4e 43 50 00 00 00 01 00  00 00 00 04 30 33 31 30  |NCP.........0310|
    0010  00 00 02 00 00 00 00 14  53 54 41 4e 44 41 52 44  |........STANDARD|
    0020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 03 00  |................|
    0030  00 00 00 02 00 01 00 00  04 00 00 00 00 02 00 00  |................|
    0040  00 00 05 00 00 00 00 02  ff 01 00 00 06 00 00 00  |................|
    0050  00 02 8c 04 00 00 07 00  00 00 00 02 84 04 00 00  |................|
    0060  08 00 00 00 00 02 80 04  00 00 09 00 00 00 00 02  |................|
    0070  80 04 00 00 0a 00 00 00  00 02 80 04 00 00 0b 00  |................|
    0080  00 00 00 02 80 04 00 00  0c 00 00 00 00 02 ff 00  |................|
    0090  00 00 0d 00 00 00 00 02  ff 00 00 00 0e 00 00 00  |................|
    00a0  00 02 ff 04 00 00 0f 00  00 00 00 02 ff 01 00 00  |................|
    00b0  10 00 00 00 00 02 ff 01  00 00 11 00 00 00 00 02  |................|
    00c0  ff 01 00 00 12 00 00 00  00 02 ff 01 00 00 13 00  |................|
    00d0  00 00 00 02 ff 01 00 00  14 00 00 00 00 02 80 01  |................|
    00e0  00 00 15 00 00 00 00 02  ff 0a 00 00 16 00 00 00  |................|
    00f0  00 02 88 04 00 00 17 00  00 00 00 02 ff 04 00 00  |................|
    0100  18 00 00 00 00 02 ff 04  00 00 19 00 00 00 00 02  |................|
    0110  80 01 00 00 1a 00 00 00  00 02 80 01 00 00 1b 00  |................|
    0120  00 00 00 02 80 01 00 00  1c 00 00 00 00 02 80 01  |................|
    0130  00 00 1d 00 00 00 00 02  80 01 00 00 1e 00 00 00  |................|
    0140  00 02 80 01 00 00 1f 00  00 00 00 1c 80 80 80 80  |................|
    0150  80 80 80 80 80 80 80 80  80 80 80 80 80 80 80 80  |................|
    0160  80 80 80 80 01 01 01 00  00 00 20 00 00 00 00 14  |.......... .....|
    0170  80 00 80 80 80 00 80 80  80 00 80 80 01 01 01 00  |................|
    0180  b2 01 80 01 00 00 00 00                           |........        |

Contrary to the `background_papers/nikon_picturecontrol:Camera compatible`,
parameters are not serialized in a unique dataset. Each parameters is a
dataset. The below table exposes datasets used.

.. note:: Value are encoded on two bytes: the first one is the biased value,
   and the second is the multiplier. Multiplication is done because settings
   have to be decimal values. The formula for getting the setting value is:
   :math:`v = (bv - 128) / m` where :math:`bv` is the biased value, :math:`m`
   is the multiplier. Exemple: b'\\x7a\\x04' is -1.5.

+----------------------+-----------+----------------+------------------------------+
| Setting              | Length    | DataSet        | Value                        |
+======================+===========+================+==============================+
| Version              | 4 bytes   | ``0x00000100`` | Fixed string: '0310'         |
+----------------------+-----------+----------------+------------------------------+
| Control Name         | 20 bytes  | ``0x00000200`` | Null terminated string.      |
|                      |           |                |                              |
|                      |           |                | * A: ``AUTO``                |
|                      |           |                | * SD: ``STANDARD``           |
|                      |           |                | * NL: ``NEUTRAL``            |
|                      |           |                | * VI: ``VIVID``              |
|                      |           |                | * MC: ``MONOCHROME``         |
|                      |           |                | * FM: ``FLAT_MONOCHROME``    |
|                      |           |                | * DM: ``DEEPTONE_MONOCHROME``|
|                      |           |                | * PT: ``PORTRAIT``           |
|                      |           |                | * RP: ``RICH_TONE_PORTRAIT`` |
|                      |           |                | * LS: ``LANDSCAPE``          |
|                      |           |                | * FL: ``FLAT``               |
|                      |           |                | * FC: ``FLEXIBLE_COLOR``     |
|                      |           |                | * 01: ``DREAM`` [#cpc]_      |
|                      |           |                | * 02: ``MORNING``            |
|                      |           |                | * 03: ``POP``                |
|                      |           |                | * 04: ``SUNDAY``             |
|                      |           |                | * 05: ``SOMBER``             |
|                      |           |                | * 06: ``DRAMATIC``           |
|                      |           |                | * 07: ``SILENCE``            |
|                      |           |                | * 08: ``BLEACHED``           |
|                      |           |                | * 09: ``MELANCHOLIC``        |
|                      |           |                | * 10: ``PURE``               |
|                      |           |                | * 11: ``DENIM``              |
|                      |           |                | * 12: ``TOY``                |
|                      |           |                | * 13: ``SEPIA``              |
|                      |           |                | * 14: ``BLUE``               |
|                      |           |                | * 15: ``RED``                |
|                      |           |                | * 16: ``PINK``               |
|                      |           |                | * 17: ``CHARCOAL``           |
|                      |           |                | * 18: ``GRAPHITE``           |
|                      |           |                | * 19: ``BINARY``             |
|                      |           |                | * 20: ``CARBON``             |
+----------------------+-----------+----------------+------------------------------+
| *undefined*          | 2 bytes   | ``0x00000300`` | Fixed value: 0x0001          |
+----------------------+-----------+----------------+------------------------------+
| Custom               | 2 bytes   | ``0x00000400`` | Customization level.         |
|                      |           |                |                              |
|                      |           |                | * ``0x0200``: ?              |
|                      |           |                | * ``0x0100``: ?              |
|                      |           |                | * ``0x0000``: AUTO           |
+----------------------+-----------+----------------+------------------------------+
|  *undefined*         | 2 bytes   | ``0x00000500`` | Fixed value: 0xFF01          |
+----------------------+-----------+----------------+------------------------------+
| Sharpening           | 2 bytes   | ``0x00000600`` | * encoded (-3..9, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| Clarity              | 2 bytes   | ``0x00000700`` | * encoded (-5..5, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| Contrast             | 2 bytes   | ``0x00000800`` | * encoded (-3..3, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| Brightness           | 2 bytes   | ``0x00000900`` | * encoded (-1.5..1.5, step:  |
|                      |           |                |   0.25)                      |
+----------------------+-----------+----------------+------------------------------+
| Saturation           | 2 bytes   | ``0x00000A00`` | * encoded (-3..3, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| Hue                  | 2 bytes   | ``0x00000B00`` | * encoded (-3..3, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| Filter Effect        | 2 bytes   | ``0x00000C00`` | Same as *Filter Effect*.     |
|                      |           |                |                              |
|                      |           |                | See 'Camera compatible'      |
|                      |           |                | section above.               |
+----------------------+-----------+----------------+------------------------------+
| Toning               | 2 bytes   | ``0x00000D00`` | Same as *Toning*.            |
|                      |           |                |                              |
|                      |           |                | See 'Camera compatible'      |
|                      |           |                | section above.               |
+----------------------+-----------+----------------+------------------------------+
| Adjust Saturation    | 2 bytes   | ``0x00000E00`` | * encoded (0..7, step: 0.25) |
+----------------------+-----------+----------------+------------------------------+
| Sharpening [#A]_     | 2 bytes   | ``0x00000F00`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Clarity [#A]_        | 2 bytes   | ``0x00001000`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Contrast [#A]_       | 2 bytes   | ``0x00001100`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Saturation [#A]_     | 2 bytes   | ``0x00001200`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Mid-range sharpening | 2 bytes   | ``0x00001300`` | Null terminated string.      |
| [#A]_                |           |                |                              |
+----------------------+-----------+----------------+------------------------------+
| *undefined*          | 2 bytes   | ``0x00001400`` | Fixed value: 0x8001          |
+----------------------+-----------+----------------+------------------------------+
| *undefined*          | 2 bytes   | ``0x00001500`` | Fixed value: 0xFF0A          |
+----------------------+-----------+----------------+------------------------------+
| Mid-range sharpening | 2 bytes   | ``0x00001600`` | * encoded (-5..5, step: 0.25)|
+----------------------+-----------+----------------+------------------------------+
| *undefined*          | 2 bytes   | ``0x00001700`` | Fixed value: 0xFF04          |
+----------------------+-----------+----------------+------------------------------+
| *undefined*          | 2 bytes   | ``0x00001800`` | Fixed value: 0xFF04          |
+----------------------+-----------+----------------+------------------------------+
| Contrast profile FC  | 2 bytes   | ``0x00001900`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Highlights           | 2 bytes   | ``0x00001A00`` | * encoded (-100..100,        |
|                      |           |                |   step: 1)                   |
+----------------------+-----------+----------------+------------------------------+
| Shadows              | 2 bytes   | ``0x00001B00`` | * encoded (-100..100,        |
|                      |           |                |   step: 1)                   |
+----------------------+-----------+----------------+------------------------------+
| White level          | 2 bytes   | ``0x00001C00`` | * encoded (-100..100,        |
|                      |           |                |   step: 1)                   |
+----------------------+-----------+----------------+------------------------------+
| Black level          | 2 bytes   | ``0x00001D00`` | * encoded (-100..100,        |
|                      |           |                |   step: 1)                   |
+----------------------+-----------+----------------+------------------------------+
| Saturation [FC]      | 2 bytes   | ``0x00001E00`` | Null terminated string.      |
+----------------------+-----------+----------------+------------------------------+
| Color Blender        | 40 bytes  | ``0x00001F00`` | Obscure data.                |
+----------------------+-----------+----------------+------------------------------+
| Color grading        | 32 bytes  | ``0x00002000`` | Obscure data.                |
+----------------------+-----------+----------------+------------------------------+
| Comment              | 258 bytes | ``0x00010100`` | Null terminated string.      |
|                      |           |                |                              |
|                      |           |                | Comment of Custom Picture    |
|                      |           |                | Control.                     |
+----------------------+-----------+----------------+------------------------------+

.. [#cpc] Creative Picture Control name have a decimal number as short name.
.. [#A] Used when '[A] Auto' picture control selected.


Custom Tone Curve
-----------------

This article details the internal structure of this parameters


.. rubric:: References
.. [nkpc] Nikon, `The Picture Controls Tool <https://nikonimglib.com/
   nxstdo/onlinehelp/en/the_picture_controls_tool_22.html>`_, Adjustments >
   Basic Edit Palettes > Picture Control