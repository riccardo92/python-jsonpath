from .environment import JSONPathEnvironment
from .exceptions import JSONPathError
from .exceptions import JSONPathIndexError
from .exceptions import JSONPathNameError
from .exceptions import JSONPathSyntaxError
from .exceptions import JSONPathTypeError
from .expressions import NOTHING
from .lex import Lexer
from .node import JSONPathNode
from .node import JSONPathNodeList
from .parse import Parser
from .path import JSONPath

__all__ = (
    "JSONPathEnvironment",
    "JSONPathError",
    "JSONPathIndexError",
    "JSONPathNameError",
    "JSONPathSyntaxError",
    "JSONPathTypeError",
    "JSONPointerError",
    "JSONPointerIndexError",
    "JSONPointerKeyError",
    "JSONPointerResolutionError",
    "JSONPointerTypeError",
    "RelativeJSONPointerError",
    "RelativeJSONPointerIndexError",
    "RelativeJSONPointerSyntaxError",
    "NOTHING",
    "Lexer",
    "JSONPathNode",
    "JSONPathNodeList",
    "Parser",
    "JSONPath",
)

# For convenience
DEFAULT_ENV = JSONPathEnvironment()
compile = DEFAULT_ENV.compile  # noqa: A001
findall = DEFAULT_ENV.findall
finditer = DEFAULT_ENV.finditer
query = DEFAULT_ENV.query
