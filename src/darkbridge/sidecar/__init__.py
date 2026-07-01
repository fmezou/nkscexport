"""Handle sidecar files.

This package groups the sidecar files handlers used by DarkBridge. These
handlers may either parse the sidecar files or write/modify existing sidecar
files. Currently, the package support the Nikon sidecar files (:file:`.nksc`)
and Darktable sidecar.

.. toctree::
    :name: sidecar_toc
    :maxdepth: 1

    nikon
    nik_adjustment
"""
__all__ = [
    "nikon",
    "nik_adjustment"
]
