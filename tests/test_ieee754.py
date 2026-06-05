"""Test suite for `ieee754` module.

This module defines a test suite for testing the `darkbridge.sidecar.ieee754`
module. Test cases are specified in `Single-precision floating-point format
<https://en.wikipedia.org/wiki/Single-precision_floating-point_format
#Notable_single-precision_cases>`_ and `Double-precision floating-point format
<https://en.wikipedia.org/wiki/Double-precision_floating-point_format>`_.
"""
import logging
import math
import unittest
from pathlib import Path

from darkbridge.sidecar.ieee754 import IEEE754

# Tested modules may use the logging facility, so a minimal configuration
# is set. To avoid side effects with the `unittest` console output, log
# entries are written in a file. By default, only level ERROR message
# are recorded, except for those in this module.
logging.basicConfig(
    level=logging.ERROR,
    style="{",
    format="{levelname} {name} {funcName} {message}",
    filename = Path(__file__).with_suffix(".log"),
    filemode = "w")
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
logging.getLogger("darkbridge.sidecar.ieee754").setLevel(logging.DEBUG)

_single_samples = (
    (
        "Smallest positive subnormal number",
        b"\x01\x00\x00\x00",
        1.401298464324817e-45
    ),
    (
        "Largest subnormal number",
        b"\xff\xff\x7f\x00",
        1.1754942106924411e-38
    ),
    (
        "Smallest positive normal number",
        b"\x00\x00\x80\x00",
        1.1754943508222875e-38
    ),
    (
        "Largest normal number",
        b"\xff\xff\x7f\x7f",
        3.4028234663852886e+38
    ),
    (
        "largest number less than one",
        b"\xff\xff\x7f\x3f",
        0.999999940395355225
    ),
    (
        "one",
        b"\x00\x00\x80\x3f",
        1.0
    ),
    (
        "Smallest number larger than one",
        b"\x01\x00\x80\x3f",
        1.00000011920928955
    ),
    (
        "-2.0",
        b"\x00\x00\x00\xc0",
        -2.0
    ),
    (
        "+zero",
        b"\x00\x00\x00\x00",
        0.0
    ),
    (
        "-zero",
        b"\x00\x00\x00\x80",
        -0.0
    ),
    (
        "Infinite",
        b"\x00\x00\x80\x7f",
        float("inf")
    ),
    (
        "-Infnite",
        b"\x00\x00\x80\xff",
        float("-inf")
    ),
    (
        "1/3",
        b"\xab\xaa\xaa\x3e",
        0.3333333432674408
    ),
    (
        "pi",
        b"\xdb\x0f\x49\x40",
        3.1415927410125732
    ),
)

_double_samples = [
    (
        "Smallest positive subnormal number",
        b"\x01\x00\x00\x00\x00\x00\x00\x00",
        4.9406564584124654e-324
    ),
    (
        "Largest subnormal number",
        b"\xff\xff\xff\xff\xff\xff\x0f\x00",
        2.2250738585072009e-308
    ),
    (
        "Smallest positive normal number",
        b"\x00\x00\x00\x00\00\x00\x10\x00",
        2.2250738585072014e-308
    ),
    (
        "Largest normal number",
        b"\xff\xff\xff\xff\xff\xff\xef\x7f",
        1.7976931348623157e308
    ),
    (
        "largest number less than one",
        b"\xff\xff\xff\xff\xff\xff\xef\x3f",
        0.9999999999999999
    ),
    (
        "one",
        b"\x00\x00\x00\x00\x00\x00\xf0\x3f",
        1.0
    ),
    (
        "Smallest number larger than one",
        b"\x01\x00\x00\x00\x00\x00\xf0\x3f",
        1.0000000000000002220
    ),
    (
        "-2.0",
        b"\x00\x00\x00\x00\x00\x00\x00\xc0",
        -2.0
    ),
    (
        "+zero",
        b"\x00\x00\x00\x00\x00\x00\x00\x00",
        0.0
    ),
    (
        "-zero",
        b"\x00\x00\x00\x00\x00\x00\x00\x80",
        -0.0
    ),
    (
        "Infinite",
        b"\x00\x00\x00\x00\x00\x00\xf0\x7f",
        float("inf")
    ),
    (
        "-Infnite",
        b"\x00\x00\x00\x00\x00\x00\xf0\xff",
        float("-inf")
    ),
    (
        "1/3",
        b"\x55\x55\x55\x55\x55\x55\xd5\x3f",
        0.33333333333333331483
    ),
    (
        "pi",
        b"\x18\x2d\x44\x54\xfb\x21\x09\x40",
        3.141592653589793116
    ),
]

_nan_samples = [
    ("NaN", b"\x01\x00\xc0\xff"),
    ("NaN", b"\x01\x00\x80\xff"),
    ("NaN", b"\x01\x00\xc0\xff"),
    ("NaN", b"\x01\x00\x80\xff")
]


class IEEE754TestCase(unittest.TestCase):
    def setUp(self):
        _logger.info(53*"*")

    def tearDown(self):
        _logger.info(50*"*")

    def test_single_precision(self):
        _logger.info("Starting...")
        tests = _single_samples
        for test in tests:
            _logger.info(f"** {test[0]}")
            self.assertEqual(test[2], IEEE754(test[1]).value)
        _logger.info("Completed")

    def test_double_precision(self):
        _logger.info("Starting...")
        tests = _double_samples
        for test in tests:
            _logger.info(f"** {test[0]}")
            self.assertEqual(test[2], IEEE754(test[1]).value)
        _logger.info("Completed")

    def test_nan(self):
        _logger.info("Starting...")
        tests = _nan_samples
        for test in tests:
            _logger.info(f"** {test[0]}")
            self.assertTrue(math.isnan(IEEE754(test[1]).value))
        _logger.info("Completed")

    def test_error(self):
        _logger.info("Starting...")
        with self.assertRaises(KeyError):
            IEEE754(b"\00")
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()