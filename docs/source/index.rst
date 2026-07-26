.. This file is a part of DarkBridge, to convert Nikon sidecars to Darktable.
   Copyright (C) 2026 DarkBridge developper
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.
   ############################################################################

.. image:: assets/darkbridge/darkbridge-logo-transparent.svg
    :align: center

##########
DarkBridge
##########

**Bridge Nikon sidecars to Darktable, seamlessly.**

**DarkBridge** is a utility that converts Nikon NX Studio ``.nksc`` sidecar
files into sidecar files compatible with Darktable. It helps photographers
migrate adjustment data from Nikon’s workflow to Darktable without manually
recreating edits. Furthermore, **DarkBridge** displays the sidecar content in a
'human-readable' way, and allows to search a metadata or image adjustment by
name in a file tree structure.

`NX Studio <https://downloadcenter.nikonimglib.com/en/products/564/NX_Studio.html>`_
(and the previous software as View-NX2, ViewNX-i, Capture NX-D) may save image
adjustments to "sidecar" files in an ``NKSC_PARAM`` folder within the same
folder as the original image. In this case, any changes to pictures will be
saved in image adjustment (sidecar) files (extension ``.nksc``) separate from
the original image data. Because changes are not applied directly to the
original image data, pictures can be edited repeatedly with no loss in quality.
Sidecar files are also used to store labels, ratings, XMP/IPTC metadata, and
other data in addition to image adjustments.

.. warning:: Image adjustments may be saved in the original image file, this
   script do not support this mode. If an image file has not a sidecar file,
   **DarkBridge** will ignore it. Same for orphan sidecar files.

For this project, the image samples have been shot with a Nikon D70s camera
and a Nikon D7100 camera using NEF format (Lossless Compressed RAW (14-bit),
Adobe RGB). For processing images, Capture NX-D, ViewNX-i and NX Studio has
been used.

**DarkBridge** is still in development phase: the transfer to darktable is
not yet implemented and the user experience is still in command line.

Nevertheless, **DarkBridge** allow you to:

* *list* the metadata (including geolocation) and images ajustement including
  the picture control from an image or a folder.

* *search* a specific metadata based on its name or a specific image ajustement.
  The search function only returns non empty metadata or active image ajustement.

The `user manual <https://darkbridge.readthedocs.io/en/develop/user_guide/
darkbridge.html>`_ expose the command line options with some usage example.

DarkBridge is written in Python and delivered a Python package named
`DarkBridge <https://pypi.org/project/DarkBridge/>`_ including a command line
interface :command:`darkbridge`. This is the documentation for **DarkBridge**
|release|.

.. image:: https://img.shields.io/github/license/fmezou/darkbridge
    :alt: License

.. image:: https://img.shields.io/readthedocs/darkbridge/develop
   :alt: Read the Docs (version)
   :target: https://darkbridge.readthedocs.io/en/develop

.. image:: https://img.shields.io/pypi/v/darkbridge
    :alt: PyPI - Version
    :target: https://pypi.org/project/darkbridge/

.. image:: https://img.shields.io/pypi/status/darkbridge
    :alt: PyPI - Status

.. image:: https://img.shields.io/pypi/format/darkbridge
    :alt: PyPI - Format


#################
Table Of Contents
#################

:ref:`users_toc` is designed for a *end-user audience* and details
use cases. It mainly documents the script (:mod:`darkbridge.main_cli`)
delivered with the python package in charge of the user interface (in
text mode) and operations scheduling.

:ref:`devs_toc` are designed for a *developer audience* for contributing
to the project. This documentation describes scripts, modules, exceptions,
classes, functions and data composing the project. Each script or module
includes a section named "Using..." explaining how to use the script or
module with some examples.

:ref:`background_toc` are designed for a *developer audience* by providing
technical background papers regarding the architecture, data structure and
similar topics.

.. toctree::
   :maxdepth: 1
   :caption: Users Guide
   :name: users_toc

   user_guide/darkbridge

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide
   :name: devs_toc

   dev_guide/darkbridge/package
   dev_guide/darkbridge/sidecar/package
   dev_guide/darkbridge/library/package

.. toctree::
   :maxdepth: 1
   :caption: Background Papers
   :name: background_toc

   background_papers/inside_nksc
   background_papers/inside_geoloc
   background_papers/inside_adjustment
   background_papers/nik_adaptivepaste
   background_papers/nik_crop
   background_papers/nik_gaussianblur
   background_papers/nik_grainnoise
   background_papers/nik_lch
   background_papers/nik_levelscurves
   background_papers/nik_newton
   background_papers/nik_rotate
   background_papers/nik_straighten
   background_papers/nikon_activedlighting
   background_papers/nikon_applicationdata
   background_papers/nikon_brightness
   background_papers/nikon_chrab
   background_papers/nikon_colorbalance
   background_papers/nikon_colorbooster
   background_papers/nikon_colorshift
   background_papers/nikon_dehaze
   background_papers/nikon_diffraction
   background_papers/nikon_distortion
   background_papers/nikon_dlightinghq
   background_papers/nikon_dlightinghs
   background_papers/nikon_dustoff
   background_papers/nikon_exposuresettings
   background_papers/nikon_fisheye
   background_papers/nikon_flare
   background_papers/nikon_legeneral
   background_papers/nikon_longchrab
   background_papers/nikon_noisereduction
   background_papers/nikon_nxhistory
   background_papers/nikon_perspective
   background_papers/nikon_photoeffects
   background_papers/nikon_picturecontrol
   background_papers/nikon_pixelshiftnoisereduction
   background_papers/nikon_quickfixcontrast
   background_papers/nikon_quickfixtonecurve
   background_papers/nikon_redeye
   background_papers/nikon_sizeres
   background_papers/nikon_skinsoftening
   background_papers/nikon_skintone
   background_papers/nikon_transform
   background_papers/nikon_unsharpmask
   background_papers/nikon_vignette
   background_papers/nikon_whitebalance


.. toctree::
   :maxdepth: 2
   :caption: Indices and tables
   :name: index_toc

   modindex
   genindex
   glossary

###############
Work to be done
###############

.. todolist::
