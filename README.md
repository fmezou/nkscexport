![DarkBridge][logo] 

> ![GitHub License][lic] [![ReadTheDocs Status][rtds]][rtdp]\
> ![GitHub Release][pkg] ![GitHub Tag][tag]\
> [![PyPI - Version][pyv]][pyt] ![PyPI - Status][pyst] ![PyPI - Format][pyfm]

DarkBridge
==========
**Bridge Nikon sidecars to Darktable, seamlessly.**

**DarkBridge** is a utility that converts Nikon NX Studio `.nksc` sidecar files 
into sidecar files compatible with Darktable.It helps photographers migrate 
adjustment data from Nikon’s workflow to Darktable without manually recreating 
edits. Furthermore, **DarkBridge** displays the sidecar content in a 
'human-readable' way, and allows to search a metadata or image adjustment by
name in a file tree structure.

[NX Studio][nxst] (and the previous software as View-NX2, ViewNX-i, Capture 
NX-D) may save image adjustments to "sidecar" files in an `NKSC_PARAM` folder 
within the same folder as the original image. In this case, any changes to 
pictures will be saved in image adjustment (sidecar) files (extension `.nksc`)
separate from the original image data. Because changes are not applied directly
to the original image data, pictures can be edited repeatedly with no loss 
in quality. Sidecar files are also used to store labels, ratings, XMP/IPTC 
metadata, and other data in addition to image adjustments.

> ***Warning:** Image adjustments may be saved in the original image file, this 
> script do not support this mode. If an image file has not a sidecar file, the
> script will ignore it. Same for orphan sidecar files.*

For this project, the image samples have been shot with a Nikon D70s camera
and a Nikon D7100 camera using NEF format (Lossless Compressed RAW (14-bit), 
Adobe RGB). For processing images, Capture NX-D, ViewNX-i and NX Studio has 
been used.

**DarkBridge** is still in development phase: the transfer to darktable is
not yet implemented and the user experience is still in command line . 
Nevertheless, **DarkBridge** allow you to:
* *list* the metadata (including geolocation) and images ajustement including 
  the picture control from an image or a folder.
* *search* a specific metadata based on its name or a specific image ajustement.
  The search function only returns non empty metadata or active image ajustement.

The [user manual][man] expose the command line options with some usage example.

See also
--------
* [NX Studio Help](https://nikonimglib.com/nxstdo/onlinehelp/en/save_80.html)
* [Nikon Software](https://downloadcenter.nikonimglib.com/en/index.html)


[logo]: https://raw.githubusercontent.com/fmezou/darkbridge/refs/heads/develop/docs/source/assets/darkbridge/darkbridge-logo.svg
[rtds]: https://app.readthedocs.org/projects/darkbridge/badge/?version=develop
[rtdp]: https://darkbridge.readthedocs.io/en/develop/
[lic]: https://img.shields.io/github/license/fmezou/darkbridge
[pkg]: https://img.shields.io/github/v/release/fmezou/darkbridge
[tag]: https://img.shields.io/github/v/tag/fmezou/darkbridge
[pyv]: https://img.shields.io/pypi/v/darkbridge
[pyfm]: https://img.shields.io/pypi/format/darkbridge
[pyst]: https://img.shields.io/pypi/status/darkbridge
[pyt]: https://pypi.org/project/darkbridge/
[nxst]: https://downloadcenter.nikonimglib.com/en/products/564/NX_Studio.html
[man]: https://darkbridge.readthedocs.io/en/develop/user_guide/darkbridge.html
