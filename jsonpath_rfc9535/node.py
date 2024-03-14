"""JSONPath node and node list definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List
from typing import Tuple
from typing import Union

if TYPE_CHECKING:
    from .environment import JSONLikeData


class JSONPathNode:
    """A JSON-like value and its location in a JSON document.

    Attributes:
        value: The JSON-like value at this node.
        location: The keys and/or indices that make up the normalized path to _value_.
    """

    __slots__ = (
        "value",
        "parts",
        "root",
    )

    def __init__(
        self,
        *,
        value: object,
        parts: Tuple[Union[int, str], ...],
        root: JSONLikeData,
    ) -> None:
        self.value: object = value
        self.parts: Tuple[Union[int, str], ...] = parts
        self.root = root

    def path(self) -> str:
        """Return the normalized path to this node."""
        return "$" + "".join(
            (f"['{p}']" if isinstance(p, str) else f"[{p}]" for p in self.parts)
        )

    def __str__(self) -> str:
        return f"JSONPathNode({self.path()})"


class JSONPathNodeList(List[JSONPathNode]):
    """A list JSONPathNode instances.

    This is a `list` subclass with some helper methods.
    """

    def values(self) -> List[object]:
        """Return the values from this node list."""
        return [node.value for node in self]

    def values_or_singular(self) -> object:
        """Return values from this node list, or a single value if there's one node."""
        if len(self) == 1:
            return self[0].value
        return [node.value for node in self]

    def empty(self) -> bool:
        """Return `True` if this node list is empty."""
        return not self

    def __str__(self) -> str:
        return f"NodeList{super().__str__()}"
