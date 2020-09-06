import unittest
from io import StringIO
from unittest.mock import patch
from printree import ftree, ptree


class TestTree(unittest.TestCase):
    def test_sorted_with_recursion(self):
        """Confirm multiline key, value and recursion build a similar tree to:
            `- . [items=3]
               |- A
               |  B: x
               |       y
               |- B [items=2]
               |  |- 0: 1
               |  `- 1: 2
               `- C: <Recursion on dict with id=140712966998864>
        """
        dct = {"A\nB": "x\ny", "B": (1, 2)}
        dct["C"] = dct
        actual = ftree(dct)
        expected = '`- . [items=3]\n   |- A\n   |  B: x\n   |       y\n   |- B [items=2]\n   |  |- 0: 1\n   |  `- 1: 2\n   `- C: <Recursion on dict with id='
        self.assertIn(expected, actual)

        with patch('sys.stdout', new=StringIO()) as redirected:
            ptree(dct)  # should be exactly as the ftree result, plus a new line
            self.assertEqual(redirected.getvalue(), actual+'\n')
