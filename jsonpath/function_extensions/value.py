"""The standard `value` function extension."""

from __future__ import annotations

from typing import TYPE_CHECKING

from jsonpath.expressions import NOTHING
from jsonpath.function_extensions import ExpressionType
from jsonpath.function_extensions import FilterFunction

if TYPE_CHECKING:
    from jsonpath.node import JSONPathNodeList


class Value(FilterFunction):
    """A type-aware implementation of the standard `value` function."""

    arg_types = [ExpressionType.NODES]
    return_type = ExpressionType.VALUE

    def __call__(self, nodes: JSONPathNodeList) -> object:
        """Return the first node in a node list if it has only one item."""
        if len(nodes) == 1:
            return nodes[0].value
        return NOTHING
