"""Handle the sidecar files.

This package groups the sidecar files handlers used by DarkBridge. These
handlers may either parse the sidecar files or write/modify existing sidecar
files. Currently, the package support the Nikon sidecar files (:file:`.nksc`)
and Darktable sidecar.

The exported modules are as follows:

.. hlist::
    :columns: 2

    * :mod:`darkbridge.sidecar.nikon` -  Handle Nikon sidecar files (read only)
"""
__all__ = [
    "nikon"
]
