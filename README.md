# printree
Tree-like formatting for python containers.

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
...         "uno": {"A", "B", "C"},
...         "dos": r"B:\newline\tab\like.ext",
...         "tres": {
...             "leaf": "string",
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
   |  |  |- leaf: string
   |  |  `- numbers [items=3]
   |  |     |- 0: -17
   |  |     |- 1: 0.01
   |  |     `- 2: 42
   |  `- uno [items=3]
   |     |- 0: A
   |     |- 1: B
   |     `- 2: C
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
