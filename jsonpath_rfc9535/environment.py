"""JSONPath configuration.

A JSONPathEnvironment is where you'd register functions extensions and
control recursion limits, for example.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from . import function_extensions
from .exceptions import JSONPathNameError
from .exceptions import JSONPathTypeError
from .expressions import ComparisonExpression
from .expressions import FunctionExtension
from .expressions import JSONPathLiteral
from .expressions import LogicalExpression
from .expressions import Path
from .function_extensions import ExpressionType
from .function_extensions import FilterFunction
from .lex import tokenize
from .parse import Parser
from .path import JSONPath
from .tokens import TokenStream

if TYPE_CHECKING:
    from .expressions import Expression
    from .node import JSONPathNode
    from .node import JSONPathNodeList
    from .tokens import Token


class JSONPathEnvironment:
    """JSONPath configuration.

    ## Class attributes

    Attributes:
        max_int_index (int): The maximum integer allowed when selecting array items by
            index. Defaults to `(2**53) - 1`.
        min_int_index (int): The minimum integer allowed when selecting array items by
            index. Defaults to `-(2**53) + 1`.
        max_recursion_depth: The maximum number of dict/objects and/or arrays/lists the
            recursive descent selector can visit before a `JSONPathRecursionError`
            is thrown.
        parser_class: The parser to use when parsing tokens from the lexer.
    """

    parser_class: Type[Parser] = Parser

    max_int_index = (2**53) - 1
    min_int_index = -(2**53) + 1
    max_recursion_depth = 100

    def __init__(self) -> None:
        self.parser: Parser = self.parser_class(env=self)
        """The parser bound to this environment."""

        self.function_extensions: Dict[str, FilterFunction] = {}
        """A list of function extensions available to filters."""

        self.setup_function_extensions()

    def compile(self, path: str) -> JSONPath:  # noqa: A003
        """Prepare a path string ready for repeated matching against different data.

        Arguments:
            path: A JSONPath query string.

        Returns:
            A `JSONPath` ready to match against some data.

        Raises:
            JSONPathSyntaxError: If _path_ is invalid.
            JSONPathTypeError: If filter functions are given arguments of an
                unacceptable type.
        """
        tokens = tokenize(path)
        stream = TokenStream(tokens)
        return JSONPath(env=self, segments=tuple(self.parser.parse(stream)))

    def finditer(
        self,
        path: str,
        data: Union[List[Any], Dict[str, Any], str],
    ) -> Iterable[JSONPathNode]:
        """Generate `JSONPathNode` instances for each match of _path_ in _data_.

        Arguments:
            path: A JSONPath query string.
            data: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            An iterator yielding `JSONPathNode` objects for each match.

        Raises:
            JSONPathSyntaxError: If the path is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        return self.compile(path).finditer(data)

    def findall(
        self,
        path: str,
        data: Union[List[Any], Dict[str, Any], str],
    ) -> List[object]:
        """Find all values in _data_ matching JSONPath query _path_.

        Arguments:
            path: A JSONPath query string.
            data: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            A list of matched values. If there are no matches, the list will be empty.

        Raises:
            JSONPathSyntaxError: If the path is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        return self.compile(path).findall(data)

    def query(
        self,
        path: str,
        data: Union[List[Any], Dict[str, Any], str],
    ) -> JSONPathNodeList:
        """Apply the JSONPath query _path_ to JSON-like _data_.

        Arguments:
            path: A JSONPath query string.
            data: JSON-like data to query, as you'd get from `json.load`.

        Returns:
            A list of `JSONPathNode` instance.

        Raises:
            JSONPathSyntaxError: If the path is invalid.
            JSONPathTypeError: If a filter expression attempts to use types in
                an incompatible way.
        """
        return self.compile(path).query(data)

    def setup_function_extensions(self) -> None:
        """Initialize function extensions."""
        self.function_extensions["length"] = function_extensions.Length()
        self.function_extensions["count"] = function_extensions.Count()
        self.function_extensions["match"] = function_extensions.Match()
        self.function_extensions["search"] = function_extensions.Search()
        self.function_extensions["value"] = function_extensions.Value()

    def validate_function_extension_signature(
        self, token: Token, args: List[Any]
    ) -> List[Any]:
        """Compile-time validation of function extension arguments.

        RFC 9535 requires us to reject paths that use filter functions with
        too many or too few arguments.
        """
        try:
            func = self.function_extensions[token.value]
        except KeyError as err:
            raise JSONPathNameError(
                f"function {token.value!r} is not defined", token=token
            ) from err

        self.check_well_typedness(token, func, args)
        return args

    def check_well_typedness(
        self,
        token: Token,
        func: FilterFunction,
        args: List[Expression],
    ) -> None:
        """Check the well-typedness of a function's arguments at compile-time."""
        # Correct number of arguments?
        if len(args) != len(func.arg_types):
            raise JSONPathTypeError(
                f"{token.value!r}() requires {len(func.arg_types)} arguments",
                token=token,
            )

        # Argument types
        for idx, typ in enumerate(func.arg_types):
            arg = args[idx]
            if typ == ExpressionType.VALUE:
                if not (
                    isinstance(arg, JSONPathLiteral)
                    or (isinstance(arg, Path) and arg.path.singular_query())
                    or (self._function_return_type(arg) == ExpressionType.VALUE)
                ):
                    raise JSONPathTypeError(
                        f"{token.value}() argument {idx} must be of ValueType",
                        token=token,
                    )
            elif typ == ExpressionType.LOGICAL:
                if not isinstance(
                    arg, (Path, (LogicalExpression, ComparisonExpression))
                ):
                    raise JSONPathTypeError(
                        f"{token.value}() argument {idx} must be of LogicalType",
                        token=token,
                    )
            elif typ == ExpressionType.NODES and not (
                isinstance(arg, Path)
                or self._function_return_type(arg) == ExpressionType.NODES
            ):
                raise JSONPathTypeError(
                    f"{token.value}() argument {idx} must be of NodesType",
                    token=token,
                )

    def _function_return_type(self, expr: Expression) -> Optional[ExpressionType]:
        """Return a filter function's return type.

        Returns `None` if _expr_ is not a function expression.
        """
        if not isinstance(expr, FunctionExtension):
            return None
        func = self.function_extensions.get(expr.name)
        if isinstance(func, FilterFunction):
            return func.return_type
        return None
