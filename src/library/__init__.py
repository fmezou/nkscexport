"""Supporting modules.

This package groups supporting modules used by DarkBridge but without
adherence to the project. These modules may be considered as standalone
packages and moved toward their own PyPI project.

The exported modules are as follows:

.. hlist::
    :columns: 2

    * :mod:`library.ieee754` -- Handle IEEE754 floating-point format
    * :mod:`library.namespace` -- Handle XML namespaces.
"""
__all__ = [
    "ieee754",
    "namespace"
]
