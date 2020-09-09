# printree

[![Build Status](https://travis-ci.org/chrizzFTD/printree.svg?branch=master)](https://travis-ci.org/chrizzFTD/printree)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/printree/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/printree?branch=master)
[![Documentation Status](https://readthedocs.org/projects/printree/badge/?version=latest)](https://printree.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/printree.svg)](https://badge.fury.io/py/printree)
[![PyPI](https://img.shields.io/pypi/pyversions/printree.svg)](https://pypi.python.org/pypi/printree)

Tree-like formatting for arbitrary python data structures.

Similar to pretty print ([pprint](https://docs.python.org/3/library/pprint.html)) but in the form of a tree:

```python
>>> from printree import ptree, ftree
>>> ptree({"x", len, 42})  # will print to the output console
 ──┐ [items=3]
   ├─ 0: x
   ├─ 1: <built-in function len>
   └─ 2: 42
>>> ftree({"x", len, 42})  # will return a string representation
' ──┐ [items=3]\n   ├─ 0: <built-in function len>\n   ├─ 1: x\n   └─ 2: 42'
```

Instances of [abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable) (with the exception of [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) & [bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) should be translated into a tree-like form.
All other objects will be considered "leaf nodes":
```python
>>> dct = {
...     "foo": [],
...     True: {
...         "uno": {"ABC", "XYZ"},
...         "dos": r"B:\newline\tab\like.ext",
...         "tres": {
...             "leaf": b"bytes",
...             "numbers": (42, -17, 0.01)
...         },
...     },
...     ("unsortable", ("tuple", "as", "key")):
...         {"multi\nlined\n\ttabbed key": "multi\nline\n\ttabbed value"}
... }
>>> dct["recursion"] = [1, dct, 2]
>>> ptree(dct)
 ──┐ [items=4]
   ├─ foo [empty]
   ├─ True [items=3]
   │  ├─ dos: B:\newline\tab\like.ext
   │  ├─ tres [items=2]
   │  │  ├─ leaf: b'bytes'
   │  │  └─ numbers [items=3]
   │  │     ├─ 0: -17
   │  │     ├─ 1: 0.01
   │  │     └─ 2: 42
   │  └─ uno [items=2]
   │     ├─ 0: ABC
   │     └─ 1: XYZ
   ├─ ('unsortable', ('tuple', 'as', 'key')) [items=1]
   │  └─ multi
   │     lined
   │            tabbed key: multi
   │                        line
   │                            tabbed value
   └─ recursion [items=3]
      ├─ 0: 1
      ├─ 1: <Recursion on dict with id=2355961208192>
      └─ 2: 2
```
By default, a [UnicodeFormatter](printree/_ptree.py) is used, but an AsciiFormatter is provided as well:
```python
>>> from printree import ptree, AsciiFormatter
>>> obj = [42, {"foo": (True, False)}]
>>> ptree(obj, AsciiFormatter)
 --. [items=2]
   |- 0: 42
   `- 1 [items=1]
      `- foo [items=2]
         |- 0: False
         `- 1: True
```
