import textwrap
import contextvars
from pprint import isrecursive
from itertools import count
from collections import abc

_recursive_ids = contextvars.ContextVar('recursive')


class TreePrinter:
    """Default formatter for printree.

    Uses unicode characters.
    """
    ROOT = '┐'
    LEVEL_NEXT = '│  '
    LEVEL_LAST = '   '
    BRANCH_NEXT = '├─ '
    BRANCH_LAST = '└─ '
    ARROW = '→'

    def __init__(self, depth: int = None, annotated: bool = False):
        """

        :param depth: If the data structure being printed is too deep, the next contained level is replaced by [...]. By default, there is no constraint on the depth (0) of the objects being formatted.
        :param annotated:
        """
        self.level = 0
        self.depth = depth
        self.annotated = annotated

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value):
        if not (isinstance(value, int) or value is None):
            raise ValueError(f"Expected depth to be an int or None. Got '{type(value).__name__}' instead.")
        self._depth = value if value else float("inf")

    def format_branch(self, obj, items: list) -> str:
        """Get the string representation of a branch element in the tree."""
        contents = f'items={len(items)}' if len(items) else "empty"
        return f' {self.ARROW} {type(obj).__name__}[{contents}]' if self.annotated else ''

    def ptree(self, obj):
        self.level = 0
        def f():
            _recursive_ids.set(set())
            for i in _itree(obj, self, subscription=self.ROOT, depth=self.depth):
                print(i)
        contextvars.copy_context().run(f)

    def ftree(self, obj):
        self.level = 0
        def f():
            _recursive_ids.set(set())
            return "\n".join(_itree(obj, self, subscription=self.ROOT, depth=self.depth))
        return contextvars.copy_context().run(f)


class AsciiPrinter(TreePrinter):
    """A formatter that uses ASCII characters only."""
    ROOT = '.'
    LEVEL_NEXT = '|  '
    BRANCH_NEXT = '|- '
    BRANCH_LAST = '`- '
    ARROW = '->'


def ptree(obj, depth:int=None, annotated:bool=False) -> None:
    """Print a tree-like representation of the given object data structure.

    :py:class:`collections.abc.Iterable` instances will be branches, with the exception of :py:class:`str` and :py:class:`bytes`.
    All other objects will be leaves.

    :param formatter: Optional :class:`printree.Formatter` to use to generate each part of the tree. An instance of the given class will be created at execution time.

    Examples:
        >>> ptree({"x", len, 42})  # will print to the output console
        ┐
        ├─ 0: x
        ├─ 1: <built-in function len>
        └─ 2: 42

        >>> dct = {"A": ("x\\ny", (42, -17, 0.01), True), "B": 42}
        >>> dct["C"] = dct
        >>> ptree(dct, formatter=AsciiPrinter())
        .
        |- A
        |  |- 0: True
        |  |- 1: x\ny
        |  `- 2
        |     |- 0: 42
        |     |- 1: -17
        |     `- 2: 0.01
        |- B: 42
        `- C: <Recursion on dict with id=2955241181376>
    """
    TreePrinter(depth=depth, annotated=annotated).ptree(obj)


def ftree(obj, depth:int=None, annotated:bool=False) -> str:
    """Return the formatted tree representation of the given object data structure as a string."""
    return TreePrinter(depth=depth, annotated=annotated).ftree(obj)


def _newline_repr(obj_repr, prefix) -> str:
    counter = count()
    newline = lambda x: next(counter) != 0
    return textwrap.indent(obj_repr, prefix, newline)


def _itree(obj, formatter, subscription, prefix="", last=False, level=0, depth=0):
    formatter.level = level
    sprout = level > 0
    children = []
    objid = id(obj)
    recursive = isrecursive(obj)
    recursive_ids = _recursive_ids.get()
    newlevel = formatter.LEVEL_LAST if last else formatter.LEVEL_NEXT
    newline_prefix = f"{prefix}{newlevel}"
    newprefix = f"{prefix}{formatter.BRANCH_LAST if last else formatter.BRANCH_NEXT}" if sprout else ""
    subscription_repr = f'{newprefix}{_newline_repr(f"{subscription}", newline_prefix)}'
    if recursive and objid in recursive_ids:
        item_repr = f"{': ' if sprout else ''}<Recursion on {type(obj).__name__} with id={objid}>"
    elif isinstance(obj, (str, bytes)):
        # Indent new lines with a prefix so that a string like "new\nline" adjusts to:
        #      ...
        #      |- 42: new
        #      |      line
        #      ...
        # for this, calculate how many characters each new line should have for padding
        prefix_len = len(prefix)  # how much we have to copy before subscription string
        last_line = subscription_repr.expandtabs().splitlines()[-1]
        newline_padding = len(last_line[prefix_len:]) + prefix_len + 2  # last 2 are ": "
        item_repr = _newline_repr(f"{': ' if sprout else ''}{obj}", f"{last_line[:prefix_len] + newlevel:<{newline_padding}}")
    elif isinstance(obj, abc.Iterable):
        # for other iterable objects, enumerate to track subscription and child count
        ismap = isinstance(obj, abc.Mapping)
        enumerateable = obj.items() if ismap else obj
        accessor = (lambda i, v: (i, *v)) if ismap else lambda i, v: (i, i, v)
        enumerated = enumerate(enumerateable)
        children.extend(accessor(*enum) for enum in enumerated)
        item_repr = formatter.format_branch(obj, children)
        if children and level == depth:
            item_repr = f"{item_repr} [...]"
            children.clear()  # avoid deeper traversal
    else:
        item_repr = f"{': ' if sprout else ''}{obj}"
    if recursive:
        recursive_ids.add(objid)

    yield f"{subscription_repr}{item_repr}"
    child_count = len(children)
    prefix += newlevel if sprout else ""  # only add level prefix starting at level 1
    for index, key, value in children:
        yield from _itree(value, formatter, key, prefix, index == (child_count - 1), level + 1, depth)
