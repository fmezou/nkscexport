NkscExport 
==========
[![ReadTheDocs Status][rtds]][rtdp] ![GitHub License][lic] 
![GitHub Release][pkg] ![GitHub Tag][tag]

Convert sidecar files from Nikon NX Studio (`.nksc`) in sidecar files compliant 
with Darktable.

[NX Studio][nxst] (and the previous software as View-NX2, ViewNX-i, Capture NX-D) may
save image adjustments to "sidecar" files in an `NKSC_PARAM` folder within the
same folder as the original image. In this case, any changes to pictures will be
saved in image adjustment (sidecar) files (extension `.nksc`) separate from the
original image data. Because changes are not applied directly to the original
image data, pictures can be edited repeatedly with no loss in quality. Sidecar
files are also used to store labels, ratings, XMP/IPTC metadata, and other data
in addition to image adjustments.

> ***warning:** Image adjustments may be saved in the original image file, this 
> script don't support this mode. If an image file have not a side car file, the
> script will ignore it. Same for orphan sidecar files.*

See also
--------
* [NX Studio Help](https://nikonimglib.com/nxstdo/onlinehelp/en/save_80.html)
* [Nikon Software](https://downloadcenter.nikonimglib.com/en/index.html)


[rtds]: https://app.readthedocs.org/projects/nkscexport/badge/?version=develop
[rtdp]: https://nkscexport.readthedocs.io/en/develop/
[lic]: https://img.shields.io/github/license/fmezou/nkscexport
[pkg]: https://img.shields.io/github/v/release/fmezou/lappdeploy
[tag]: https://img.shields.io/github/v/tag/fmezou/nkscexport
[nxst]: https://downloadcenter.nikonimglib.com/en/products/564/NX_Studio.html
