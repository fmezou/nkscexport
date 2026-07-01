"""Handle IEEE754 floating-point format.

The :mod:`library.ieee754` module reads float numbers in a `IEEE754`_
representation. This module do not implement the full specification of
the standard and only read IEEE754 representation. The implementation
supports the following subset:

* 32 bits - simple (binary32)
* 64 bits - double (binary64)

.. _IEEE754: https://en.wikipedia.org/wiki/IEEE_754

Using ``ieee754``
-----------------
The simple examples below shows how converting a IEEE754 representation of
a float number expressed as a binary string in a `float` object.

We can read simple precision float number as shown below.

>>> from library.ieee754 import IEEE754
>>> IEEE754(b"\\xab\\xaa\\xaa\\x3e").value
0.3333333432674408
>>> IEEE754(b"\\xab\\xaa\\xaa\\x3e").value
0.3333333432674408
>>> IEEE754(b"\\x00\\x00\\x00\\x00").value
0.0
>>> IEEE754(b"\\x00\\x00\\x80\\x7f").value
inf

And the same with double precision.

>>> IEEE754( b"\\x00\\x00\\x00\\x00\\x00\\x00\\xf0\\x3f").value
1.0
>>> IEEE754(b"\\x00\\x00\\x00\\x00\\x00\\x00\\xf0\\xff").value
-inf
>>> IEEE754(b"\\x55\\x55\\x55\\x55\\x55\\x55\\xd5\\x3f").value
0.3333333333333333

The module supports only simple and double precision based on the lenght
of the binary string; Any value other than 4 bytes (32 bits) or 8 bytes
(64 bits) raise an :exc:`KeyError` Exception. The example below have a 56 bits
lenght binary string.

>>> IEEE754(b"\\x55\\x55\\x55\\x55\\x55\\x55\\xd5").value
KeyError: 'Unsupported IEEE754 Precision (56 bits)'

Reference
---------

.. autoclass:: IEEE754
   :member-order: bysource
   :members:
   :private-members:
   :show-inheritance:
"""
import logging


__all__ = [
    "IEEE754",
]

# This module can be used as library or as a script, a nullHandler is
# added to avoid output in the absence of any logging configuration.
# https://docs.python.org/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

# Predefined layout of IEEE 754 representation, key is the word
# width in bit (32 or 64) with layout of each part (sign, exponent,
# fraction) with the position# of the least significant bit (lsb) and
# its width in bits
_LAYOUT = {
    # IEEE754 Simple precision 32-bits
    32: {
        "sign": {"lsb": 31, "width": 1},
        "exponent": {"lsb": 23, "width": 8},
        "fraction": {"lsb": 0, "width": 23}
    },
    # IEEE754 Double precision 64-bits
    64: {
        "sign": {"lsb": 63, "width": 1},
        "exponent": {"lsb": 52, "width": 11},
        "fraction": {"lsb": 0, "width": 52}
    }
}

class IEEE754:
    """IEEE754 float number.

    The function supports single precision (32 bits), double
    precision (64 bits).

    Args:
        buffer: Bytes object of IEEE754 representation of the float
            number with the most significant byte is at the end of the
            byte array (``byteorder = little``).

    Raises:
        KeyError: Unsupported IEEE754 Precision.

    Attributes:
        value: Value of the float number.
    """
    value: float | None
    _word: int
    _bias: int
    _layout: dict
    def __init__(self, buffer: bytes):
        self.value = None
        self._bias = 0
        self._layout = {}

        # Get the layout of the IEEE 754 representation
        self._word = int.from_bytes(buffer, byteorder='little')
        length = len(buffer) * 8
        match length:
            case 32 | 64:
                self._layout = _LAYOUT[length]
                e_biased_max = (1 << self._layout["exponent"]["width"]) - 1
                e_bias = (1 << (self._layout["exponent"]["width"] - 1)) - 1
                e_max = e_biased_max - 1 - e_bias
                e_min = 1 - e_bias

            case _:
                raise KeyError(
                    f"Unsupported IEEE754 Precision ({length} bits)")

        # Get part and compute
        sign = (-1) ** self._get_value("sign")
        e_biased = self._get_value("exponent")
        fraction = self._get_value("fraction")

        # Compute the fraction part
        real = 0.0
        f = fraction
        for i in range(-self._layout["fraction"]["width"], 0):
            real += (f & 1) * 2**i
            f = f >> 1

        # Final compute with the special value
        if e_biased == 0: # Subnormal numbers and zeros
            if fraction == 0:
                self.value = sign * 0.0
            else:
                self.value = sign * 2**(e_min) * (0.0 + real)
        elif e_biased == e_biased_max: # Infinite or NaN
            if fraction == 0:
                self.value = sign * float('inf')
            else:
                self.value = float('nan')
        else : # Normalized number
            # implicit leading bit to 1
            self.value = sign * 2**(e_biased - e_bias) * (1.0 + real)

    def _get_value(self, part: str) -> int:
        """Return the value of part.

        This method extract the value from the IEEE representation and
        return it as an integer value.

        Args:
            part: name of the part ("sign", "exponent", "fraction"). Another
                name raise the :exc:`KeyError` exception.

        Returns:
            Value of the part as an integer
        """
        lsb = self._layout[part]["lsb"]
        width = self._layout[part]["width"]
        mask = ((1 << width) - 1) << lsb
        return (self._word & mask) >> lsb

if __name__ == "__main__":
    import doctest
    doctest.testmod()