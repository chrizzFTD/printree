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
    ROOT = ' ──┐'
    LEVEL_NEXT = '│  '
    LEVEL_LAST = '   '
    BRANCH_NEXT = '├─ '
    BRANCH_LAST = '└─ '

    def __init__(self, depth: int = None):
        self.level = 0
        self.depth = depth

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value):
        if not (isinstance(value, int) or value is None):
            raise ValueError(f"Expected depth to be an int or None. Got '{type(value).__name__}' instead.")
        self._depth = value if value is not None else float("inf")

    def format_branch(self, obj, items: list) -> str:
        """Get the string representation of a branch element in the tree."""
        return ''
        contents = f'items={len(items)}' if len(items) else "empty"
        # return f' [{contents}] ({type(obj).__name__})'
        return f' [{contents}]'

    def format_leaf(self, obj) -> str:
        """Get the string representation of a leaf element in the tree."""
        return f': {obj}'

    def ptree(self, obj):
        ptree(obj, formatter=self)

    def ftree(self, obj):
        return ftree(obj, formatter=self)


class AsciiPrinter(TreePrinter):
    """A formatter that uses ASCII characters only."""
    ROOT = ' --.'
    LEVEL_NEXT = '|  '
    BRANCH_NEXT = '|- '
    BRANCH_LAST = '`- '


def ptree(obj, formatter=TreePrinter()) -> None:
    """Print a tree-like representation of the given object data structure.

    :py:class:`collections.abc.Iterable` instances will be branches, with the exception of :py:class:`str` and :py:class:`bytes`.
    All other objects will be leaves.

    :param formatter: Optional :class:`printree.Formatter` to use to generate each part of the tree. An instance of the given class will be created at execution time.

    Examples:
        >>> ptree({"x", len, 42})
         ──┐ [items=3]
           ├─ 0: x
           ├─ 1: 42
           └─ 2: <built-in function len>

        >>> dct = {"A": {"x\\ny", (42, -17, 0.01), True}, "B": 42}
        >>> dct["C"] = dct
        >>> ptree(dct, formatter=AsciiFormatter)
        `- . [items=3]
           |- A [items=3]
           |  |- 0: True
           |  |- 1: x
           |  |     y
           |  `- 2 [items=3]
           |     |- 0: -17
           |     |- 1: 0.01
           |     `- 2: 42
           |- B: 42
           `- C: <Recursion on dict with id=140712966998864>
    """
    def f():
        formatter.level = 0
        _recursive_ids.set(set())
        for i in _itree(obj, formatter, subscription=formatter.ROOT):
            print(i)
    ctx = contextvars.copy_context()
    ctx.run(f)


def ftree(obj, formatter=TreePrinter()) -> str:
    """Return the formatted tree representation of the given object data structure as a string."""
    def f():
        formatter.level = 0
        _recursive_ids.set(set())
        return "\n".join(_itree(obj, formatter, subscription=formatter.ROOT))
    ctx = contextvars.copy_context()
    return ctx.run(f)


def _newline_repr(obj_repr, prefix) -> str:
    counter = count()
    newline = lambda x: next(counter) != 0
    return textwrap.indent(obj_repr, prefix, newline)


def _itree(obj, formatter, subscription, prefix="", last=True, level=0):
    formatter.level = level
    children = []
    level_suffix = formatter.LEVEL_LAST if last else formatter.LEVEL_NEXT
    newline_prefix = f"{prefix}{level_suffix}"
    subscription_repr = _newline_repr(f"{subscription}", newline_prefix)
    recursive_ids = _recursive_ids.get()
    recursive = isrecursive(obj)
    objid = id(obj)
    typename = type(obj).__name__
    if recursive and objid in recursive_ids:
        item_repr = f": <Recursion on {typename} with id={objid}>"
    elif formatter.level == formatter.depth:
        item_repr = " [...]"
    elif isinstance(obj, (str, bytes)):
        # for text, indent new lines with an appropiate prefix so that
        # a string like "new\nline" is adjusted to something like:
        #      ...
        #      |- 42: new
        #      |      line
        #      ...
        # for this, calculate how many characters each new line should have for padding
        # based on the last line from the subscription repr
        prefix_len = len(newline_prefix)
        no_prefix = subscription_repr.splitlines()[-1].expandtabs()[prefix_len:]
        newline_padding = len(no_prefix) + prefix_len + 2  # last 2 are ": " below
        item_repr = _newline_repr(f': {obj}', f"{newline_prefix:<{newline_padding}}")
    elif isinstance(obj, abc.Iterable):
        # for other iterable objects, sort and ennumerate so that we can anticipate what
        # prefix we should use (e.g. are we the last item in the iteration?)
        ismap = isinstance(obj, abc.Mapping)
        enumerateable = obj.items() if ismap else obj
        accessor = (lambda i, v: (i, *v)) if ismap else lambda i, v: (i, i, v)
        enumerated = enumerate(enumerateable)
        children.extend(accessor(*enum) for enum in enumerated)
        item_repr = formatter.format_branch(obj, children)
    else:
        item_repr = formatter.format_leaf(obj)

    if recursive:
        recursive_ids.add(objid)

    # implementation detail: if there's no prefix, we're root
    fullprefix = f"{prefix}{formatter.BRANCH_LAST if last else formatter.BRANCH_NEXT}{subscription_repr}" if prefix else formatter.ROOT
    yield f"{fullprefix}{item_repr}"
    prefix += level_suffix
    child_count = len(children)
    for index, key, value in children:
        yield from _itree(value, formatter, key, prefix, index == (child_count - 1), level + 1)
