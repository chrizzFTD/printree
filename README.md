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
`- . [items=3]
   |- 0: <built-in function len>
   |- 1: 42
   `- 2: x
>>> ftree({"x", len, 42})  # will return a string representation
'`- . [items=3]\n   |- 0: <built-in function len>\n   |- 1: 42\n   `- 2: x'
```

Instances of [abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable) (with the exception of [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) & [bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) should be translated into a tree-like form.
Other objects will be considered "leaf nodes":
```python
>>> dct = {
...     "multi\nlined\n\ttabbed key": 1,
...     True: {
...         "uno": {"ABC", "XYZ"},
...         "dos": r"B:\newline\tab\like.ext",
...         "tres": {
...             "leaf": b"bytes",
...             "numbers": (42, -17, 0.01)
...         },
...     },
...     "foo": [],
...     ("unsortable", ("tuple", "as", "key")):
...         ["multi\nline\nfirst", "multi\nline\nlast"]
... }
>>> dct['recursive_reference'] = dct
>>> ptree(dct)
`- . [items=5]
   |- multi
   |  lined
   |    tabbed key: 1
   |- True [items=3]
   |  |- dos: B:\newline\tab\like.ext
   |  |- tres [items=2]
   |  |  |- leaf: b'bytes'
   |  |  `- numbers [items=3]
   |  |     |- 0: -17
   |  |     |- 1: 0.01
   |  |     `- 2: 42
   |  `- uno [items=2]
   |     |- 0: ABC
   |     `- 1: XYZ
   |- foo [empty]
   |- ('unsortable', ('tuple', 'as', 'key')) [items=2]
   |  |- 0: multi
   |  |     line
   |  |     first
   |  `- 1: multi
   |        line
   |        last
   `- recursive_reference: <Recursion on dict with id=140712966998864>
```
