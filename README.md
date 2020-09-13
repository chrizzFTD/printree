# printree

[![Build Status](https://travis-ci.org/chrizzFTD/printree.svg?branch=master)](https://travis-ci.org/chrizzFTD/printree)
[![Coverage Status](https://coveralls.io/repos/github/chrizzFTD/printree/badge.svg?branch=master)](https://coveralls.io/github/chrizzFTD/printree?branch=master)
[![Documentation Status](https://readthedocs.org/projects/printree/badge/?version=latest)](https://printree.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/printree.svg)](https://badge.fury.io/py/printree)
[![PyPI](https://img.shields.io/pypi/pyversions/printree.svg)](https://pypi.python.org/pypi/printree)

Tree-like formatting for arbitrary python data structures.

## Instalation
```bash
pip install printree
```

## Usage
`printree` aims to be similar to pretty print ([pprint](https://docs.python.org/3/library/pprint.html)) but in the form of a tree:

```python
>>> from printree import ptree, ftree
>>> ptree({"x", len, 42})  # will print to the output console
┐
├─ 0: x
├─ 1: <built-in function len>
└─ 2: 42
>>> ftree({"x", len, 42})  # will return a string representation
'┐\n├─ 0: x\n├─ 1: <built-in function len>\n└─ 2: 42'
```

Instances of [abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable) (with the exception of [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) & [bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) will be represented as branches.
All other objects will be considered "leaf nodes":
```python
>>> from printree import ptree
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
...     ("tuple", "as", "key"):
...         {"multi\nlined\n\ttabbed key": "multi\nline\n\ttabbed value"}
... }
>>> dct["recursion"] = [1, dct, 2]
>>> ptree(dct)
┐
├─ foo
├─ True
│  ├─ uno
│  │  ├─ 0: XYZ
│  │  └─ 1: ABC
│  ├─ dos: B:\newline\tab\like.ext
│  └─ tres
│     ├─ leaf: b'bytes'
│     └─ numbers
│        ├─ 0: 42
│        ├─ 1: -17
│        └─ 2: 0.01
├─ ('tuple', 'as', 'key')
│  └─ multi
│     lined
│       tabbed key: multi
│                   line
│                       tabbed value
└─ recursion
   ├─ 0: 1
   ├─ 1: <Recursion on dict with id=2735472957952>
   └─ 2: 2
```
The `annotated` and `depth` options modify verbosity of the output when creating the tree representation:
```python
>>> ptree(dct, depth=2, annotated=True)
┐ → dict[items=4]
├─ foo → list[empty]
├─ True → dict[items=3]
│  ├─ uno: [...]
│  ├─ dos: [...]
│  └─ tres: [...]
├─ ('tuple', 'as', 'key') → dict[items=1]
│  └─ multi
│     lined
│       tabbed key: [...]
└─ recursion → list[items=3]
   ├─ 0: [...]
   ├─ 1: <Recursion on dict with id=2365220724288>
   └─ 2: [...]
``` 

## Customizing formatting
Different representations can be achieved by subclassing the `TreePrinter` object. 
An `AsciiPrinter` is provided as an example:
```python
>>> from printree import AsciiPrinter
>>> obj = [42, {"foo": (True, False)}]
>>> AsciiPrinter().ptree(obj)
.
|- 0: 42
`- 1
   `- foo
      |- 0: True
      `- 1: False
```
New formatters can change each of the string representations of the tree.
The main members to override from the provided classes are:
- `ROOT`
- `LEVEL_NEXT`
- `LEVEL_LAST`
- `BRANCH_NEXT`
- `BRANCH_LAST`
- `ARROW`

The `level` attribute will be automatically set on the printer instance to indicate the current depth in the traversal of the tree.

For example, to make the formatter print with a different color on every branch level, this could be an approach:

```python
from printree import TreePrinter

class ColoredTree(TreePrinter):
    colors = {
        0: '\033[31m',  # red
        1: '\033[32m',  # green
        2: '\033[33m',  # yellow
        3: '\033[36m',  # cyan
        4: '\033[35m',  # magenta
    }
    _RESET = '\033[0m'

    def __getattribute__(self, item):
        if item in ("LEVEL_NEXT", "LEVEL_LAST", "BRANCH_NEXT", "BRANCH_LAST"):
            return f"{self.color}{getattr(super(), item)}{self._RESET}"
        return super().__getattribute__(item)

    @property
    def color(self):
        return self.colors[self.level % len(self.colors)]

    @property
    def ROOT(self):  # for root (level 0), prefer the color of the children (level 1) 
        return f'{self.colors[1]}{super().ROOT}{self._RESET}'


multiline = {"foo": {False: {"AB\nCD": "xy", 42:len}, True: []}, ("bar",): []}
dct = {"A": multiline, "B": (multiline,), "C\nD": "x\ny", "F": (1, "2")}

import os
os.system("")  # required on windows only

ColoredTree().ptree(dct)
```
Which outputs:
![](colored_example.svg)
