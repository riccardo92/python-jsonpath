"""JSONPath child and descendant segment definitions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Tuple

from .exceptions import JSONPathRecursionError
from .node import JSONPathNode

if TYPE_CHECKING:
    from .environment import JSONPathEnvironment
    from .selectors import JSONPathSelector
    from .tokens import Token


class JSONPathSegment(ABC):
    """Base class for all JSONPath segments."""

    __slots__ = ("env", "token", "selectors")

    def __init__(
        self,
        *,
        env: JSONPathEnvironment,
        token: Token,
        selectors: Tuple[JSONPathSelector, ...],
    ) -> None:
        self.env = env
        self.token = token
        self.selectors = selectors

    @abstractmethod
    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterable[JSONPathNode]:
        """Apply this segment to each `JSONPathNode` in _nodes_."""


class JSONPathChildSegment(JSONPathSegment):
    """The JSONPath child selection segment."""

    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterable[JSONPathNode]:
        """Select children of each node in _nodes_."""
        for node in nodes:
            for selector in self.selectors:
                yield from selector.resolve(node)

    def __str__(self) -> str:
        return f"[{', '.join(str(itm) for itm in self.selectors)}]"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, JSONPathChildSegment)
            and self.selectors == __value.selectors
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash((self.selectors, self.token))


class JSONPathRecursiveDescentSegment(JSONPathSegment):
    """The JSONPath recursive descent segment."""

    def resolve(self, nodes: Iterable[JSONPathNode]) -> Iterable[JSONPathNode]:
        """Select descendants of each node in _nodes_."""
        for node in nodes:
            for _node in self._visit(node):
                for selector in self.selectors:
                    yield from selector.resolve(_node)

    def _visit(self, node: JSONPathNode, depth: int = 1) -> Iterable[JSONPathNode]:
        if depth > self.env.max_recursion_depth:
            raise JSONPathRecursionError("recursion limit exceeded", token=self.token)

        yield node

        if isinstance(node.value, dict):
            for key, val in node.value.items():
                if isinstance(val, (dict, list)):
                    _node = JSONPathNode(
                        value=val,
                        parts=node.parts + (key,),
                        root=node.root,
                    )
                    yield from self._visit(_node, depth + 1)
        elif isinstance(node.value, list):
            for i, val in enumerate(node.value):
                if isinstance(val, (dict, list)):
                    _node = JSONPathNode(
                        value=val,
                        parts=node.parts + (i,),
                        root=node.root,
                    )
                    yield from self._visit(_node, depth + 1)

    def __str__(self) -> str:
        return f"..[{', '.join(str(itm) for itm in self.selectors)}]"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, JSONPathRecursiveDescentSegment)
            and self.selectors == __value.selectors
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash(("..", self.selectors, self.token))
