import textwrap
import contextvars
from pprint import isrecursive
from itertools import count
from collections import abc

_recursive_ids = contextvars.ContextVar('recursive')


class UnicodeFormatter:
    """Formatter details"""
    level = 0
    ROOT = ' ──┐'
    LEVEL_NEXT = '│  '
    LEVEL_LAST = '   '
    BRANCH_NEXT = '├─ '
    BRANCH_LAST = '└─ '

    @classmethod
    def format_branch(cls, obj: list) -> str:
        """Get the string representation of a branch element in the tree."""
        items = len(obj)
        return f' [items={items}]' if items else " [empty]"

    @classmethod
    def format_leaf(cls, obj) -> str:
        """Get the string representation of a leaf element in the tree."""
        return f': {obj}'


class AsciiFormatter(UnicodeFormatter):
    """Ascii Formatter details"""
    ROOT = ' --.'
    LEVEL_NEXT = '|  '
    BRANCH_NEXT = '|- '
    BRANCH_LAST = '`- '


def ptree(obj, formatter=None) -> None:
    """Print a tree-like representation of the given object data structure.

    :py:class:`collections.abc.Iterable` instances will be branches, with the exception of :py:class:`str` and :py:class:`bytes`.
    All other objects will be leaves.

    :param formatter: Optional formatter object to use Defaults to :class:`printree.UnicodeFormat`.

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
    formatter = formatter() if formatter else UnicodeFormatter()
    def f():
        _recursive_ids.set(set())
        for i in _itree(obj, formatter, subscription=formatter.ROOT):
            print(i)
    ctx = contextvars.copy_context()
    ctx.run(f)


def ftree(obj, formatter=None) -> str:
    """Return the formatted tree representation of the given object data structure as a string."""
    formatter = formatter() if formatter else UnicodeFormatter()
    def f():
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
    if recursive and objid in recursive_ids:
        item_repr = f": <Recursion on {type(obj).__name__} with id={objid}>"
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
        try:
            enumerated = enumerate(sorted(enumerateable))
        except (TypeError, RecursionError):  # un-sortable, enumerate as-is
            enumerated = enumerate(enumerateable)
        children.extend(accessor(*enum) for enum in enumerated)
        item_repr = formatter.format_branch(children)
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
