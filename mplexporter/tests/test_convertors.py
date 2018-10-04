import unittest
from matplotlib import ticker
from .. import StrMethodTickFormatterConvertor

class TickFormatConvertorTestCase(unittest.TestCase):

    def test_001_format_strings(self):
        conversions = [
            ("{x}", {'format_string': '', 'prefix': '', 'suffix': ''}),
            ("{x:#x}", {'format_string': '#x', 'prefix': '', 'suffix': ''}),
            ("{x:.2f}", {'format_string': '.2f', 'prefix': '', 'suffix': ''}),
            ("{x:.2%}", {'format_string': '.2%', 'prefix': '', 'suffix': ''}),
            ("P{x:.2%}", {'format_string': '.2%', 'prefix': 'P', 'suffix': ''}),
            ("P{x:.2%} 100", {'format_string': '.2%', 'prefix': 'P', 'suffix': ' 100'}),
        ]
        for mpl_fmt, d3_fmt in conversions: 
            formatter = ticker.StrMethodFormatter(mpl_fmt)
            cnvrt = StrMethodTickFormatterConvertor(formatter)
            self.assertEqual(cnvrt.output, d3_fmt)
