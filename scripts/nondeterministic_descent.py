"""Utilities for exploring nondeterminism in the recursive descent segment."""

from __future__ import annotations

import json
import os
import random
import sys
from collections import deque
from typing import TYPE_CHECKING
from typing import Deque
from typing import Iterable
from typing import List
from typing import Optional
from typing import TextIO
from typing import Tuple

if TYPE_CHECKING:
    from jsonpath_rfc9535.environment import JSONLikeData


HORIZONTAL_SEP = "\N{BOX DRAWINGS LIGHT HORIZONTAL}" * 2
VERTICAL_SEP = "\N{BOX DRAWINGS LIGHT VERTICAL}"
BRANCH = "\N{BOX DRAWINGS LIGHT VERTICAL AND RIGHT}" + HORIZONTAL_SEP + " "
TERMINAL_BRANCH = "\N{BOX DRAWINGS LIGHT UP AND RIGHT}" + HORIZONTAL_SEP + " "
INDENT = VERTICAL_SEP + " " * 3
TERMINAL_INDENT = " " * 4

COLOR_CODES = [
    ("\033[92m", "\033[0m"),
    ("\033[93m", "\033[0m"),
    ("\033[94m", "\033[0m"),
    ("\033[95m", "\033[0m"),
    ("\033[96m", "\033[0m"),
    ("\033[91m", "\033[0m"),
]


class AuxNode:
    def __init__(
        self,
        depth: int,
        value: object,
        children: Optional[List[AuxNode]] = None,
    ) -> None:
        self.value = value
        self.children = children or []
        self.depth = depth

    def __str__(self) -> str:
        c_start, c_stop = COLOR_CODES[self.depth % len(COLOR_CODES)]
        return f"{c_start}{self.value}{c_stop}"

    @staticmethod
    def from_(data: JSONLikeData) -> AuxNode:
        def _visit(node: AuxNode, depth: int = 0) -> None:
            if isinstance(node.value, dict):
                for val in node.value.values():
                    _node = AuxNode(depth + 1, val)
                    _visit(_node, depth + 1)
                    node.children.append(_node)

            elif isinstance(node.value, list):
                for val in node.value:
                    _node = AuxNode(depth + 1, val)
                    _visit(_node, depth + 1)
                    node.children.append(_node)

        root = AuxNode(0, data)
        _visit(root)
        return root

    @staticmethod
    def collections(data: JSONLikeData) -> AuxNode:
        def _visit(node: AuxNode, depth: int = 0) -> None:
            if isinstance(node.value, dict):
                for val in node.value.values():
                    if isinstance(val, (list, dict)):
                        _node = AuxNode(depth + 1, val)
                        _visit(_node, depth + 1)
                        node.children.append(_node)

            elif isinstance(node.value, list):
                for val in node.value:
                    if isinstance(val, (list, dict)):
                        _node = AuxNode(depth + 1, val)
                        _visit(_node, depth + 1)
                        node.children.append(_node)

        root = AuxNode(0, data)
        _visit(root)
        return root


def pptree(
    node: AuxNode,
    indent: str = "",
    buf: TextIO = sys.stdout,
) -> None:
    """Pretty print the tree rooted at `node`."""
    # Pre-order tree traversal
    buf.write(str(node) + os.linesep)

    if node.children:
        # Recursively call pptree for all but the last child of `node`.
        for child in node.children[:-1]:
            buf.write(indent + BRANCH)
            pptree(child, indent=indent + INDENT, buf=buf)

        # Terminal branch case for last, possibly only, child of `node`.
        buf.write(indent + TERMINAL_BRANCH)
        pptree(node.children[-1], indent=indent + TERMINAL_INDENT, buf=buf)

    # Base case. No children.


def pre_order_visit(node: AuxNode) -> Iterable[AuxNode]:
    yield node

    for child in node.children:
        yield from pre_order_visit(child)


def breadth_first_visit(node: AuxNode) -> Iterable[AuxNode]:
    queue: Deque[AuxNode] = deque([node])

    while queue:
        _node = queue.popleft()
        yield _node
        queue.extend(_node.children)


def nondeterministic_visit(root: AuxNode) -> Iterable[AuxNode]:
    queue: Deque[AuxNode] = deque(root.children)
    yield root

    while queue:
        _node = queue.popleft()
        yield _node
        # Visit child nodes now or queue them for later?
        visit_children = random.choice([True, False])
        for child in _node.children:
            if visit_children:
                yield child
                queue.extend(child.children)
            else:
                queue.append(child)


def get_perms(root: AuxNode) -> List[Tuple[AuxNode, ...]]:
    perms = {tuple(nondeterministic_visit(root)) for _ in range(1000)}
    perms.add(tuple(pre_order_visit(root)))
    return sorted(perms, key=lambda t: str(t))


def pp_json_path_perms(data: JSONLikeData) -> None:
    print("Input data")
    print(f"\033[92m{data}\033[0m")
    aux_tree = AuxNode.from_(data)
    print("\nTree view")
    pptree(aux_tree)

    print("\nPre order")
    print(", ".join(str(n) for n in pre_order_visit(aux_tree)))

    print("\nLevel order")
    print(", ".join(str(n) for n in breadth_first_visit(aux_tree)))

    print("\nNondeterministic order")
    for perm in get_perms(aux_tree):
        print(", ".join(str(node) for node in perm))

    print("\n---\n\nCollections only")
    aux_tree = AuxNode.collections(data)
    pptree(aux_tree)

    print("\nPre order")
    print(", ".join(str(n) for n in pre_order_visit(aux_tree)))

    print("\nLevel order")
    print(", ".join(str(n) for n in breadth_first_visit(aux_tree)))

    print("\nNondeterministic order")
    for perm in get_perms(aux_tree):
        print(", ".join(str(node) for node in perm))


if __name__ == "__main__":
    if len(sys.argv) < 2:  # noqa: PLR2004
        print("error: no data to process")
        print(f"usage: {sys.argv[0]} <JSON string>")
        sys.exit(1)

    data = json.loads(sys.argv[1])
    pp_json_path_perms(data)
