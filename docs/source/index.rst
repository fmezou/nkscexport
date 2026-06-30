:github_url:

.. image:: _static/darkbridge_assets/darkbridge-logo-transparent.svg
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

DarkBridge is written in Python and delivered a Python package named
`DarkBridge <https://pypi.org/project/DarkBridge/>`_ including a command line
interface :command:`darkbridge`. This is the documentation for **DarkBridge**
|release|.

.. image:: https://img.shields.io/github/license/fmezou/darkbridge
    :alt: License

.. image:: https://img.shields.io/readthedocs/darkbridge/develop
   :alt: Read the Docs (version)

.. image:: https://img.shields.io/pypi/v/darkbridge
    :alt: PyPI - Version

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

   user_guide/main_cli

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide
   :name: devs_toc

   dev_guide/darkbridge/package
   dev_guide/sidecar/package
   dev_guide/library/package

.. toctree::
   :maxdepth: 1
   :caption: Background Papers
   :name: background_toc

   background_papers/inside_nksc
   background_papers/inside_geoloc
   background_papers/inside_adjustment



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
