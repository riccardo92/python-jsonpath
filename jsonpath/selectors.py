"""JSONPath selector definitions."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping
from collections.abc import Sequence
from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Iterable
from typing import Optional

from .exceptions import JSONPathIndexError
from .exceptions import JSONPathTypeError
from .expressions import FilterContext
from .node import JSONPathNode

if TYPE_CHECKING:
    from .environment import JSONPathEnvironment
    from .expressions import FilterExpression
    from .tokens import Token


class JSONPathSelector(ABC):
    """Base class for all JSONPath selectors."""

    __slots__ = ("env", "token")

    def __init__(self, *, env: JSONPathEnvironment, token: Token) -> None:
        self.env = env
        self.token = token

    @abstractmethod
    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Apply the segment/selector to _node_.

        Arguments:
            node: A node matched by preceding segments/selectors.

        Returns:
            The `JSONPathNode` instances created by applying this selector to _node_.
        """


class PropertySelector(JSONPathSelector):
    """The property or key selector."""

    __slots__ = ("name",)

    def __init__(
        self,
        *,
        env: JSONPathEnvironment,
        token: Token,
        name: str,
    ) -> None:
        super().__init__(env=env, token=token)
        self.name = name

    def __str__(self) -> str:
        return repr(self.name)

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, PropertySelector)
            and self.name == __value.name
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash((self.name, self.token))

    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Select a value from a mappings by its key."""
        if isinstance(node.value, Mapping):
            with suppress(KeyError):
                yield JSONPathNode(
                    value=node.value[self.name],
                    location=node.location + (self.name,),
                    root=node.root,
                )


class IndexSelector(JSONPathSelector):
    """The array index selector."""

    __slots__ = ("index", "_as_key")

    def __init__(
        self,
        *,
        env: JSONPathEnvironment,
        token: Token,
        index: int,
    ) -> None:
        if index < env.min_int_index or index > env.max_int_index:
            raise JSONPathIndexError("index out of range", token=token)

        super().__init__(env=env, token=token)
        self.index = index
        self._as_key = str(self.index)

    def __str__(self) -> str:
        return str(self.index)

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, IndexSelector)
            and self.index == __value.index
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash((self.index, self.token))

    def _normalized_index(self, obj: Sequence[object]) -> int:
        if self.index < 0 and len(obj) >= abs(self.index):
            return len(obj) + self.index
        return self.index

    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Select an element from an array by index."""
        if isinstance(node.value, Sequence) and not isinstance(node.value, str):
            norm_index = self._normalized_index(node.value)
            with suppress(IndexError):
                _node = JSONPathNode(
                    value=node.value[self.index],
                    location=node.location + (norm_index,),
                    root=node.root,
                )
                yield _node


class SliceSelector(JSONPathSelector):
    """Sequence slicing selector."""

    __slots__ = ("slice",)

    def __init__(
        self,
        *,
        env: JSONPathEnvironment,
        token: Token,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        super().__init__(env=env, token=token)
        self._check_range(start, stop, step)
        self.slice = slice(start, stop, step)

    def __str__(self) -> str:
        stop = self.slice.stop if self.slice.stop is not None else ""
        start = self.slice.start if self.slice.start is not None else ""
        step = self.slice.step if self.slice.step is not None else "1"
        return f"{start}:{stop}:{step}"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, SliceSelector)
            and self.slice == __value.slice
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash((str(self), self.token))

    def _check_range(self, *indices: Optional[int]) -> None:
        for i in indices:
            if i is not None and (
                i < self.env.min_int_index or i > self.env.max_int_index
            ):
                raise JSONPathIndexError("index out of range", token=self.token)

    def _normalized_index(self, obj: Sequence[object], index: int) -> int:
        if index < 0 and len(obj) >= abs(index):
            return len(obj) + index
        return index

    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Select a range of values from an array/sequence."""
        if isinstance(node.value, Sequence) and self.slice.step != 0:
            idx = self.slice.start or 0
            step = self.slice.step or 1
            for obj in node.value[self.slice]:
                norm_index = self._normalized_index(node.value, idx)
                _node = JSONPathNode(
                    value=obj,
                    location=node.location + (norm_index,),
                    root=node.root,
                )
                yield _node
                idx += step


class WildSelector(JSONPathSelector):
    """The wildcard selector."""

    def __init__(self, *, env: JSONPathEnvironment, token: Token) -> None:
        super().__init__(env=env, token=token)

    def __str__(self) -> str:
        return "*"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, WildSelector) and self.token == __value.token

    def __hash__(self) -> int:
        return hash(self.token)

    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Select all items from a sequence/array or values from a mapping/object."""
        if isinstance(node.value, Mapping):
            for key, val in node.value.items():
                _node = JSONPathNode(
                    value=val,
                    location=node.location + (key,),
                    root=node.root,
                )
                yield _node

        elif isinstance(node.value, Sequence) and not isinstance(node.value, str):
            for i, val in enumerate(node.value):
                _node = JSONPathNode(
                    value=val,
                    location=node.location + (i,),
                    root=node.root,
                )
                yield _node


class Filter(JSONPathSelector):
    """Filter sequence/array items or mapping/object values with a filter expression."""

    __slots__ = ("expression",)

    def __init__(
        self,
        *,
        env: JSONPathEnvironment,
        token: Token,
        expression: FilterExpression,
    ) -> None:
        super().__init__(env=env, token=token)
        self.expression = expression

    def __str__(self) -> str:
        return f"?{self.expression}"

    def __eq__(self, __value: object) -> bool:
        return (
            isinstance(__value, Filter)
            and self.expression == __value.expression
            and self.token == __value.token
        )

    def __hash__(self) -> int:
        return hash((str(self.expression), self.token))

    def resolve(self, node: JSONPathNode) -> Iterable[JSONPathNode]:
        """Select sequence items or mapping values where with filter expression."""
        if isinstance(node.value, Mapping):
            for key, val in node.value.items():
                context = FilterContext(
                    env=self.env,
                    current=val,
                    root=node.root,
                )
                try:
                    if self.expression.evaluate(context):
                        yield JSONPathNode(
                            value=val,
                            location=node.location + (key,),
                            root=node.root,
                        )
                except JSONPathTypeError as err:
                    if not err.token:
                        err.token = self.token
                    raise

        elif isinstance(node.value, Sequence) and not isinstance(node.value, str):
            for i, value in enumerate(node.value):
                context = FilterContext(
                    env=self.env,
                    current=value,
                    root=node.root,
                )
                try:
                    if self.expression.evaluate(context):
                        yield JSONPathNode(
                            value=value,
                            location=node.location + (i,),
                            root=node.root,
                        )
                except JSONPathTypeError as err:
                    if not err.token:
                        err.token = self.token
                    raise
