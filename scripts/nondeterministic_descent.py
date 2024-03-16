"""Command line utility for inspecting nondeterministic recursive descent orderings."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from jsonpath_rfc9535.utils.nondeterministic_descent import AuxNode
from jsonpath_rfc9535.utils.nondeterministic_descent import all_perms
from jsonpath_rfc9535.utils.nondeterministic_descent import breadth_first_visit
from jsonpath_rfc9535.utils.nondeterministic_descent import pp_tree
from jsonpath_rfc9535.utils.nondeterministic_descent import pre_order_visit

if TYPE_CHECKING:
    from jsonpath_rfc9535 import JSONLikeData


def pp_json_path_perms(data: JSONLikeData) -> None:  # noqa: D103
    print("Input data")
    print(f"\033[92m{data}\033[0m")
    aux_tree = AuxNode.from_(data)
    print("\nTree view")
    pp_tree(aux_tree)

    print("\nPre order")
    print(", ".join(str(n) for n in pre_order_visit(aux_tree)))

    print("\nLevel order")
    print(", ".join(str(n) for n in breadth_first_visit(aux_tree)))

    print("\nNondeterministic order")
    for perm in all_perms(aux_tree):
        print(", ".join(str(node) for node in perm))

    print("\n---\n\nCollections only")
    aux_tree = AuxNode.from_(data, collections_only=True)
    pp_tree(aux_tree)

    print("\nPre order")
    print(", ".join(str(n) for n in pre_order_visit(aux_tree)))

    print("\nLevel order")
    print(", ".join(str(n) for n in breadth_first_visit(aux_tree)))

    print("\nNondeterministic order")
    for perm in all_perms(aux_tree):
        print(", ".join(str(node) for node in perm))


if __name__ == "__main__":
    if len(sys.argv) < 2:  # noqa: PLR2004
        print("error: no data to process")
        print(f"usage: {sys.argv[0]} <JSON string>")
        sys.exit(1)

    data = json.loads(sys.argv[1])
    pp_json_path_perms(data)
