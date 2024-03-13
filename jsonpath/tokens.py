"""JSONPath query expression tokens, as produced by the lexer."""

from __future__ import annotations

from collections import deque
from enum import Enum
from enum import auto
from typing import Deque
from typing import Iterator
from typing import Tuple

from .exceptions import JSONPathSyntaxError


class TokenType(Enum):
    """JSONPath query token types."""

    EOF = auto()
    ILLEGAL = auto()
    SKIP = auto()

    SHORTHAND_PROPERTY = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    DOT_PROPERTY = auto()  # TODO: do we need this?
    DOUBLE_DOT = auto()
    FILTER = auto()
    INDEX = auto()
    LBRACKET = auto()
    PROPERTY = auto()
    RBRACKET = auto()
    ROOT = auto()
    SLICE = auto()
    SLICE_START = auto()
    SLICE_STEP = auto()
    SLICE_STOP = auto()
    WILD = auto()

    AND = auto()
    CURRENT = auto()
    DOUBLE_QUOTE_STRING = auto()
    EQ = auto()
    FALSE = auto()
    FLOAT = auto()
    FUNCTION = auto()
    GE = auto()
    GT = auto()
    INT = auto()
    LE = auto()
    LG = auto()
    LPAREN = auto()
    LT = auto()
    NE = auto()
    NOT = auto()
    NULL = auto()
    OP = auto()
    OR = auto()
    RPAREN = auto()
    SINGLE_QUOTE_STRING = auto()
    TRUE = auto()


class Token:
    """A JSONPath query expression token, as produced by the lexer.

    Attributes:
        kind (TokenType): The token's type.
        value (str): The _path_ substring containing text for the token.
        index (str): The index at which _value_ starts in _path_.
        path (str): A reference to the complete JSONPath string from which this
            token derives.
    """

    __slots__ = ("kind", "value", "index", "path")

    def __init__(
        self,
        kind: TokenType,
        value: str,
        index: int,
        path: str,
    ) -> None:
        self.kind = kind
        self.value = value
        self.index = index
        self.path = path

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Token(kind={self.kind.name!r}, value={self.value!r}, "
            f"index={self.index}, path={self.path!r})"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Token)
            and self.kind == other.kind
            and self.value == other.value
            and self.index == other.index
            and self.path == other.path
        )

    def __hash__(self) -> int:
        return hash((self.kind, self.value, self.index, self.path))

    def position(self) -> Tuple[int, int]:
        """Return the line and column number for the start of this token."""
        line_number = self.value.count("\n", 0, self.index) + 1
        column_number = self.index - self.value.rfind("\n", 0, self.index)
        return (line_number, column_number - 1)


class TokenStream:
    """Step through or iterate a stream of tokens."""

    def __init__(self, token_iter: Iterator[Token]):
        self.iter = token_iter
        self._pushed: Deque[Token] = deque()
        self.current = Token(TokenType.SKIP, "", -1, "")
        next(self)

    class TokenStreamIterator:
        """An iterable token stream."""

        def __init__(self, stream: TokenStream):
            self.stream = stream

        def __iter__(self) -> Iterator[Token]:
            return self

        def __next__(self) -> Token:
            tok = self.stream.current
            if tok.kind is TokenType.EOF:
                self.stream.close()
                raise StopIteration
            next(self.stream)
            return tok

    def __iter__(self) -> Iterator[Token]:
        return self.TokenStreamIterator(self)

    def __next__(self) -> Token:
        tok = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        elif self.current.kind is not TokenType.EOF:
            try:
                self.current = next(self.iter)
            except StopIteration:
                self.close()
        return tok

    def __str__(self) -> str:  # pragma: no cover
        return f"current: {self.current}\nnext: {self.peek}"

    def next_token(self) -> Token:
        """Return the next token from the stream."""
        return next(self)

    @property
    def peek(self) -> Token:
        """Look at the next token."""
        current = next(self)
        result = self.current
        self.push(current)
        return result

    def push(self, tok: Token) -> None:
        """Push a token back to the stream."""
        self._pushed.append(self.current)
        self.current = tok

    def close(self) -> None:
        """Close the stream."""
        self.current = Token(TokenType.EOF, "", -1, "")

    def expect(self, *typ: TokenType) -> None:
        """Raise an exception if the current token type is not one of _type_."""
        if self.current.kind not in typ:
            if len(typ) == 1:
                _typ = repr(typ[0])
            else:
                _typ = f"one of {[t.name for t in typ]!r}"
            raise JSONPathSyntaxError(
                f"expected {_typ}, found {self.current.kind.name!r}",
                token=self.current,
            )

    def expect_peek(self, *typ: TokenType) -> None:
        """Raise an exception if the next token type is not one of _type_."""
        if self.peek.kind not in typ:
            if len(typ) == 1:
                _typ = repr(typ[0].name)
            else:
                _typ = f"one of {[t.name for t in typ]!r}"
            raise JSONPathSyntaxError(
                f"expected {_typ}, found {self.peek.kind.name!r}",
                token=self.peek,
            )
