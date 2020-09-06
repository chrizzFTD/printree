import textwrap
import contextvars
from itertools import count
from collections import abc

_root = contextvars.ContextVar('root')


def ptree(obj, /) -> None:
    """Print a tree-like representation of the given object data structure.

    :py:class:`collections.abc.Iterable` instances will be branches, with the exception of :py:class:`str` and :py:class:`bytes`.
    All other objects will be leaves.

    Examples:
        >>> ptree({"x", len, 42})
        `- . [items=3]
           |- 0: <built-in function len>
           |- 1: 42
           `- 2: x

        >>> dct = {"A": {"x\\ny", (42, -17, 0.01), True}, "B": 42}
        >>> dct["C"] = dct
        >>> ptree(dct)
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
        _root.set(obj)
        for i in _itree(obj):
            print(i)
    ctx = contextvars.copy_context()
    ctx.run(f)


def ftree(obj, /) -> str:
    """Return the formatted tree representation of the given object data structure as a string."""
    def f():
        _root.set(obj)
        return "\n".join(_itree(obj))
    ctx = contextvars.copy_context()
    return ctx.run(f)


def _newline_repr(obj_repr, /, prefix) -> str:
    counter = count()
    newline = lambda x: next(counter) != 0
    return textwrap.indent(obj_repr, prefix, newline)


def _itree(obj, /, subscription=".", prefix="", last=True):
    children = []
    item_repr = f': {obj}'
    if _root.get() is obj and subscription != ".":  # recursive reference in container
        item_repr = f": <Recursion on {type(obj).__name__} with id={id(object)}>"
    elif isinstance(obj, (str, bytes)):
        # for string and bytes, indent new lines with an appropiate prefix so that
        # a string line "new\nline" is adjusted to something like:
        #      ...
        #      |- 42: new
        #      |      line
        #      ...
        newline_item_prefix = f'{prefix}{"     " if last else "|    "}{" " * len(f"{subscription}")}'
        item_repr = _newline_repr(item_repr, newline_item_prefix)
    elif isinstance(obj, abc.Iterable):
        # for other iterable objects, sort and ennumerate so that we can anticipate what
        # prefix we should use (e.g. are we the last item in the iteration?)
        ismap = isinstance(obj, abc.Mapping)
        enumerateable = obj.items() if ismap else obj
        accessor = (lambda i, v: (i, *v)) if ismap else lambda i, v: (i, i, v)
        try:
            enumerated = enumerate(sorted(enumerateable))
        except TypeError:  # un-sortable, enumerate as-is
            enumerated = enumerate(enumerateable)
        children.extend(accessor(*enum) for enum in enumerated)
        item_repr = f' [{items=}]' if (items := len(children)) else " [empty]"

    newline_subscription_prefix = f"{prefix}{'   ' if last else '|  '}"
    subscription_repr = _newline_repr(f"{subscription}", newline_subscription_prefix)
    yield f"{prefix}{'`- ' if last else '|- '}{subscription_repr}{item_repr}"
    prefix += "   " if last else "|  "
    child_count = len(children)
    for index, key, value in children:
        yield from _itree(value, subscription=key, prefix=prefix, last=index == (child_count - 1))
