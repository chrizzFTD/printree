import unittest
from io import StringIO
from unittest.mock import patch
from printree import ptree, ftree, AsciiPrinter


class TestTree(unittest.TestCase):
    def test_no_container(self):
        """Confirm a non container formats without issues next to the root."""
        actual = ftree(42)
        expected = '┐42'
        self.assertEqual(actual, expected)

    def test_invalid_arguments(self):
        """Ensure we fail with invalid depth arguments."""
        with self.assertRaises(TypeError):
            ftree(42, depth="")

        with self.assertRaises(ValueError):
            ftree(42, depth=-1)

    def test_flat_list(self):
        """Confirm a flat list outputs as expected:
            ┐
            ├── 0: x
            ├── 1: <built-in function len>
            └── 2: 42
        """
        actual = ftree(["x", len, 42])
        expected = '┐\n├── 0: x\n├── 1: <built-in function len>\n└── 2: 42'
        self.assertEqual(actual, expected)

    def test_ascii_with_recursion(self):
        """Confirm multiline key, value and recursion build a similar tree to:

            .
            |-- AB
            |   CD
            |        EF
            |                GH      IJ: xx
            |                            y
            |                            y
            |                                zz
            |-- B
            |   C
            |   |-- 0: 1
            |   |      hello
            |   `-- 1: 2
            |         world
            |-- C
            |   D: x
            |      y
            |-- C
            |   E: x
            |-- C: x
            |      y
            |-- foo
            |-- True
            |   |-- uno
            |   |   |-- 0: A
            |   |   |      B
            |   |   |      C
            |   |   `-- 1: X
            |   |         Y
            |   |         Z
            |   |-- dos: B:\newline\tab\like.ext
            |   `-- tres
            |      |-- leaf: b'bytes'
            |      `-- (42, -17, 0.01)
            |         |-- AB
            |         |   CD
            |         |       EF
            |         |               GH      IJ: xx
            |         |                           y
            |         |                           y
            |         |                               zz
            |         |-- B
            |         |   C
            |         |   |-- 0: 1
            |         |   |      hello
            |         |   `-- 1: 2
            |         |         world
            |         |-- C
            |         |   D: x
            |         |      y
            |         |-- C
            |         |   E: x
            |         `-- C: x
            |               y
            |-- ('tuple', 'as', 'key')
            |   `-- multi
            |      lined
            |        tabbed key: multi
            |                    line
            |                        tabbed value
            |-- recursion
            |   |-- 0: 1
            |   |-- 1: <Recursion on dict with id=1559765928064>
            |   `-- 2: 2
            |-- G
            |   |-- .: <Recursion on dict with id=1559765928064>
            |   `--
            |      |-- 0: 1
            |      |-- 1: 2
            |      `-- 2: <Recursion on list with id=1559766300544>
            `-- ZAB
               CD
                    EF
                            GH      IJ: xx
                                        yy
                                            zz
        """
        multiline = {
            "AB\nCD\n\tEF\n\t\tGH\tIJ": "xx\ny\ny\n\tzz",
            "B\nC": ("1\nhello", "2\nworld"),
            "C\nD": "x\ny", "C\nE": "x", "C": "x\ny"
        }
        dct = {
            **multiline,
            "foo": [],
            True: {
                "uno": ("A\nB\nC", "X\nY\nZ"),
                "dos": r"B:\newline\tab\like.ext",
                "tres": {
                    "leaf": b"bytes",
                    (42, -17, 0.01): multiline,
                },
            },
            ("tuple", "as", "key"):
                {"multi\nlined\n\ttabbed key": "multi\nline\n\ttabbed value"}
        }
        dct["recursion"] = [1, dct, 2]
        rec = [1, 2]
        rec.append(rec)
        dct["G"] = {".": dct, "": rec}
        dct["ZAB\nCD\n\tEF\n\t\tGH\tIJ"] = "xx\nyy\n\tzz"
        dctid = id(dct)
        recid = id(rec)
        expected = f".\n|-- AB\n|   CD\n|   \tEF\n|   \t\tGH\tIJ: xx\n|                           y\n|                           y\n|                           \tzz\n|-- B\n|   C\n|   |-- 0: 1\n|   |      hello\n|   `-- 1: 2\n|          world\n|-- C\n|   D: x\n|      y\n|-- C\n|   E: x\n|-- C: x\n|      y\n|-- foo\n|-- True\n|   |-- uno\n|   |   |-- 0: A\n|   |   |      B\n|   |   |      C\n|   |   `-- 1: X\n|   |          Y\n|   |          Z\n|   |-- dos: B:\\newline\\tab\\like.ext\n|   `-- tres\n|       |-- leaf: b'bytes'\n|       `-- (42, -17, 0.01)\n|           |-- AB\n|           |   CD\n|           |   \tEF\n|           |   \t\tGH\tIJ: xx\n|           |                               y\n|           |                               y\n|           |                               \tzz\n|           |-- B\n|           |   C\n|           |   |-- 0: 1\n|           |   |      hello\n|           |   `-- 1: 2\n|           |          world\n|           |-- C\n|           |   D: x\n|           |      y\n|           |-- C\n|           |   E: x\n|           `-- C: x\n|                  y\n|-- ('tuple', 'as', 'key')\n|   `-- multi\n|       lined\n|       \ttabbed key: multi\n|                           line\n|                           \ttabbed value\n|-- recursion\n|   |-- 0: 1\n|   |-- 1: <Recursion on dict with id={dctid}>\n|   `-- 2: 2\n|-- G\n|   |-- .: <Recursion on dict with id={dctid}>\n|   `-- \n|       |-- 0: 1\n|       |-- 1: 2\n|       `-- 2: <Recursion on list with id={recid}>\n`-- ZAB\n    CD\n    \tEF\n    \t\tGH\tIJ: xx\n                            yy\n                            \tzz"
        ascii = AsciiPrinter()
        actual = ascii.ftree(dct)
        self.assertEqual(expected, actual)
        with patch('sys.stdout', new=StringIO()) as redirected:
            ascii.ptree(dct)  # should be exactly as the ftree result, plus a new line
            self.assertEqual(redirected.getvalue(), actual+'\n')

    def test_unsortable_recursion(self):
        a = []
        b = [a]
        a.append(b)
        actual = AsciiPrinter().ftree([a, b])
        expected = f'.\n|-- 0\n|   `-- 0\n|       `-- 0: <Recursion on list with id={id(a)}>\n`-- 1: <Recursion on list with id={id(b)}>'
        self.assertEqual(expected, actual)

    def test_annotated(self):
        """Test that annotated shows as expected:

            ┐ → list[items=1]
            └── 0 → dict[items=3]
               ├── A: x
               │      y
               ├── B → list[empty]
               └── C → tuple[items=3]
                  ├── 0: True
                  ├── 1: False
                  └── 2 → dict[items=1]
                     └── X
                        Y → tuple[items=4]
                        ├── 0: 1
                        ├── 1: 2
                        ├── 2: 3
                        └── 3: <Recursion on list with id=1643795438976>
        """
        inner = []
        ann = {"A": "x\ny", "B": [], "C": (True, False, {"X\nY": (1, 2, 3, inner)})}
        inner.append(ann)
        expected = f'┐ → list[items=1]\n└── 0 → dict[items=3]\n    ├── A: x\n    │      y\n    ├── B → list[empty]\n    └── C → tuple[items=3]\n        ├── 0: True\n        ├── 1: False\n        └── 2 → dict[items=1]\n            └── X\n                Y → tuple[items=4]\n                ├── 0: 1\n                ├── 1: 2\n                ├── 2: 3\n                └── 3: <Recursion on list with id={id(inner)}>'
        actual = ftree(inner, annotated=True)
        self.assertEqual(expected, actual)

    def test_depth(self):
        """Verify specifying depth limits the traversal of the tree:

            ┐ → dict[items=4]
            ├── foo → list[empty]
            ├── True → dict[items=3] [...]
            ├── ('tuple', 'as', 'key') → dict[items=1] [...]
            └── recursion → list[items=3] [...]
        """
        dct = {
            "foo": [],
            True: {
                "uno": ("ABC", "XYZ"),
                "dos": r"B:\newline\tab\like.ext",
                "tres": {
                    "leaf": b"bytes",
                    "numbers": (42, -17, 0.01)
                },
            },
            ("tuple", "as", "key"):
                {"multi\nlined\n\ttabbed key": "multi\nline\n\ttabbed value"}
        }

        dct["recursion"] = [1, dct, 2]

        expected = "┐ → dict[items=4]\n├── foo → list[empty]\n├── True → dict[items=3] [...]\n├── ('tuple', 'as', 'key') → dict[items=1] [...]\n└── recursion → list[items=3] [...]"
        actual = ftree(dct, depth=1, annotated=True)
        self.assertEqual(expected, actual)
        with patch('sys.stdout', new=StringIO()) as redirected:
            ptree(dct, depth=1, annotated=True)  # should be exactly as the ftree result, plus a new line
            self.assertEqual(redirected.getvalue(), actual+'\n')

        expected = f"┐ → dict[items=4]\n├── foo → list[empty]\n├── True → dict[items=3]\n│   ├── uno → tuple[items=2] [...]\n│   ├── dos: B:\\newline\\tab\\like.ext\n│   └── tres → dict[items=2] [...]\n├── ('tuple', 'as', 'key') → dict[items=1]\n│   └── multi\n│       lined\n│       \ttabbed key: multi\n│                           line\n│                           \ttabbed value\n└── recursion → list[items=3]\n    ├── 0: 1\n    ├── 1: <Recursion on dict with id={id(dct)}>\n    └── 2: 2"
        actual = ftree(dct, depth=2, annotated=True)
        self.assertEqual(expected, actual)
