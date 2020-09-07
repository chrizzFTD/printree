import unittest
from io import StringIO
from unittest.mock import patch
from printree import ftree, ptree


class TestTree(unittest.TestCase):
    def test_sorted_with_recursion(self):
        """Confirm multiline key, value and recursion build a similar tree to:

            `- . [items=5]
               |- A [items=1]
               |  `- b'xy' [items=1]
               |     `- (True, False) [items=1]
               |        `- AB
               |           CD
               |            EF
               |                    GH      IJ: xx
               |                                y
               |                                y
               |                                    zz
               |- B [items=1]
               |  `- 0 [items=1]
               |     `- b'xy' [items=1]
               |        `- (True, False) [items=1]
               |           `- AB
               |              CD
               |                    EF
               |                            GH      IJ: xx
               |                                        y
               |                                        y
               |                                            zz
               |- C
               |  D: x
               |     y
               |- F [items=2]
               |  |- 0: 1
               |  `- 1: 2
               `- G [items=2]
                  |-  [items=3]
                  |  |- 0: 1
                  |  |- 1: 2
                  |  `- 2: <Recursion on list with id=1731749379200>
                  `- .: <Recursion on dict with id=1731749449088>
        """
        multiline = {b"xy": {(True, False): {"AB\nCD\n\tEF\n\t\tGH\tIJ": "xx\ny\ny\n\tzz"}}}
        dct = {"A": multiline, "B": (multiline,), "C\nD": "x\ny", "F": (1, "2")}
        rec = [1, 2]
        rec.append(rec)
        dct["G"] = {".": dct, "": rec}
        dctid = id(dct)
        recid = id(rec)
        expected = f"`- . [items=5]\n   |- A [items=1]\n   |  `- b'xy' [items=1]\n   |     `- (True, False) [items=1]\n   |        `- AB\n   |           CD\n   |           \tEF\n   |           \t\tGH\tIJ: xx\n   |                                y\n   |                                y\n   |                                \tzz\n   |- B [items=1]\n   |  `- 0 [items=1]\n   |     `- b'xy' [items=1]\n   |        `- (True, False) [items=1]\n   |           `- AB\n   |              CD\n   |              \tEF\n   |              \t\tGH\tIJ: xx\n   |                                        y\n   |                                        y\n   |                                        \tzz\n   |- C\n   |  D: x\n   |     y\n   |- F [items=2]\n   |  |- 0: 1\n   |  `- 1: 2\n   `- G [items=2]\n      |-  [items=3]\n      |  |- 0: 1\n      |  |- 1: 2\n      |  `- 2: <Recursion on list with id={recid}>\n      `- .: <Recursion on dict with id={dctid}>"
        actual = ftree(dct)
        self.assertEqual(expected, actual)
        with patch('sys.stdout', new=StringIO()) as redirected:
            ptree(dct)  # should be exactly as the ftree result, plus a new line
            self.assertEqual(redirected.getvalue(), actual+'\n')
