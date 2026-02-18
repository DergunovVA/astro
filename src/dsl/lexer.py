"""
DSL Lexer - Tokenizer for astrological formulas

Converts formula strings into token streams for parsing.

Example:
    >>> lexer = Lexer("Sun.Sign == Aries")
    >>> tokens = lexer.tokenize()
    >>> print(tokens)
    [
        Token(type=IDENTIFIER, value='Sun', line=1, column=0),
        Token(type=DOT, value='.', line=1, column=3),
        Token(type=IDENTIFIER, value='Sign', line=1, column=4),
        Token(type=EQ, value='==', line=1, column=9),
        Token(type=IDENTIFIER, value='Aries', line=1, column=12),
    ]
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    """Types of tokens in the DSL"""

    # Operators (logical)
    AND = auto()  # AND, &&
    OR = auto()  # OR, ||
    NOT = auto()  # NOT, !

    # Operators (comparison)
    EQ = auto()  # ==
    NEQ = auto()  # !=
    LT = auto()  # <
    GT = auto()  # >
    LTE = auto()  # <=
    GTE = auto()  # >=
    IN = auto()  # IN

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    DOT = auto()  # .
    COMMA = auto()  # ,

    # Aggregator keywords (special)
    PLANETS = auto()  # planets (aggregator)
    ASPECTS = auto()  # aspects (aggregator)
    HOUSES = auto()  # houses (aggregator)

    # Literals
    IDENTIFIER = auto()  # Sun, Moon, Mars, Aries, etc.
    NUMBER = auto()  # 123, 45.6
    STRING = auto()  # "text", 'text'
    BOOLEAN = auto()  # True, False

    # Special
    EOF = auto()  # End of file
    UNKNOWN = auto()  # Unknown token (error)


@dataclass
class Token:
    """A single token in the formula"""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', L{self.line}:C{self.column})"


class LexerError(Exception):
    """Raised when lexer encounters invalid syntax"""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Ошибка на строке {line}, позиция {column}: {message}")


class Lexer:
    """
    Tokenizer for astrological DSL formulas

    Converts text formulas into token streams for parsing.

    Features:
    - Recognizes operators: AND, OR, NOT, ==, !=, IN, etc.
    - Recognizes aggregators: planets, aspects, houses
    - Supports identifiers, numbers, strings
    - Tracks line and column for error reporting

    Usage:
        lexer = Lexer("Sun.Sign == Aries AND Moon.House == 1")
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    """

    # Keywords that map to special token types
    KEYWORDS = {
        # Logical operators
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NOT": TokenType.NOT,
        # Comparison operator
        "IN": TokenType.IN,
        # Aggregators (special keywords)
        "planets": TokenType.PLANETS,
        "aspects": TokenType.ASPECTS,
        "houses": TokenType.HOUSES,
        # Boolean literals
        "True": TokenType.BOOLEAN,
        "False": TokenType.BOOLEAN,
    }

    # Two-character operators
    TWO_CHAR_OPS = {
        "==": TokenType.EQ,
        "!=": TokenType.NEQ,
        "<=": TokenType.LTE,
        ">=": TokenType.GTE,
        "&&": TokenType.AND,
        "||": TokenType.OR,
    }

    # Single-character operators and delimiters
    SINGLE_CHAR_TOKENS = {
        "<": TokenType.LT,
        ">": TokenType.GT,
        "!": TokenType.NOT,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        ".": TokenType.DOT,
        ",": TokenType.COMMA,
    }

    def __init__(self, text: str):
        """
        Initialize lexer with formula text

        Args:
            text: Formula string to tokenize
        """
        self.text = text
        self.pos = 0  # Current position in text
        self.line = 1  # Current line number
        self.column = 0  # Current column number
        self.current_char = self.text[0] if text else None

    def advance(self):
        """Move to next character, updating position tracking"""
        if self.current_char == "\n":
            self.line += 1
            self.column = 0
        else:
            self.column += 1

        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self, offset: int = 1) -> Optional[str]:
        """
        Look ahead at next character(s) without advancing

        Args:
            offset: How many characters to look ahead (default: 1)

        Returns:
            Next character or None if at end
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """Skip # comments (single-line)"""
        if self.current_char == "#":
            while self.current_char is not None and self.current_char != "\n":
                self.advance()
            self.advance()  # Skip the newline

    def read_number(self) -> Token:
        """
        Read numeric literal (int or float)

        Returns:
            Token with NUMBER type

        Examples:
            123 -> Token(NUMBER, '123')
            45.6 -> Token(NUMBER, '45.6')
        """
        start_column = self.column
        num_str = ""

        # Read integer part
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()

        # Check for decimal point
        if self.current_char == "." and self.peek() and self.peek().isdigit():
            num_str += self.current_char
            self.advance()

            # Read fractional part
            while self.current_char is not None and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()

        return Token(TokenType.NUMBER, num_str, self.line, start_column)

    def read_string(self, quote: str) -> Token:
        """
        Read string literal with quotes

        Args:
            quote: Quote character (' or ")

        Returns:
            Token with STRING type

        Examples:
            "hello" -> Token(STRING, 'hello')
            'world' -> Token(STRING, 'world')
        """
        start_column = self.column
        self.advance()  # Skip opening quote

        value = ""
        while self.current_char is not None and self.current_char != quote:
            # Handle escape sequences
            if self.current_char == "\\":
                self.advance()
                if self.current_char in ["\\", quote, "n", "t"]:
                    escape_map = {"\\": "\\", "n": "\n", "t": "\t"}
                    value += escape_map.get(self.current_char, self.current_char)
                    self.advance()
                else:
                    raise LexerError(
                        f"Неизвестная escape-последовательность: \\{self.current_char}",
                        self.line,
                        self.column,
                    )
            else:
                value += self.current_char
                self.advance()

        if self.current_char != quote:
            raise LexerError(
                f"Незакрытая строка (ожидается {quote})", self.line, self.column
            )

        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, self.line, start_column)

    def read_identifier(self) -> Token:
        """
        Read identifier or keyword

        Returns:
            Token with IDENTIFIER or keyword type

        Examples:
            Sun -> Token(IDENTIFIER, 'Sun')
            AND -> Token(AND, 'AND')
            planets -> Token(PLANETS, 'planets')
        """
        start_column = self.column
        value = ""

        # Read alphanumeric and underscores
        while self.current_char is not None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            value += self.current_char
            self.advance()

        # Check if it's a keyword
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)

        return Token(token_type, value, self.line, start_column)

    def tokenize(self) -> List[Token]:
        """
        Convert entire formula into list of tokens

        Returns:
            List of Token objects

        Raises:
            LexerError: If invalid syntax is encountered

        Example:
            >>> lexer = Lexer("Sun.Sign == Aries")
            >>> tokens = lexer.tokenize()
            >>> len(tokens)
            6  # Sun, ., Sign, ==, Aries, EOF
        """
        tokens = []

        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Skip comments
            if self.current_char == "#":
                self.skip_comment()
                continue

            # Numbers
            if self.current_char.isdigit():
                tokens.append(self.read_number())
                continue

            # Strings
            if self.current_char in ['"', "'"]:
                tokens.append(self.read_string(self.current_char))
                continue

            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == "_":
                tokens.append(self.read_identifier())
                continue

            # Two-character operators
            two_char = self.current_char + (self.peek() or "")
            if two_char in self.TWO_CHAR_OPS:
                start_column = self.column
                self.advance()
                self.advance()
                tokens.append(
                    Token(
                        self.TWO_CHAR_OPS[two_char], two_char, self.line, start_column
                    )
                )
                continue

            # Single-character tokens
            if self.current_char in self.SINGLE_CHAR_TOKENS:
                start_column = self.column
                char = self.current_char
                self.advance()
                tokens.append(
                    Token(self.SINGLE_CHAR_TOKENS[char], char, self.line, start_column)
                )
                continue

            # Unknown character
            raise LexerError(
                f"Неизвестный символ: '{self.current_char}'", self.line, self.column
            )

        # Add EOF token
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens


# Convenience function for quick tokenization
def tokenize(formula: str) -> List[Token]:
    """
    Quick tokenization of formula string

    Args:
        formula: Formula string

    Returns:
        List of tokens

    Example:
        >>> tokens = tokenize("Sun.Sign == Aries")
        >>> [t.type.name for t in tokens]
        ['IDENTIFIER', 'DOT', 'IDENTIFIER', 'EQ', 'IDENTIFIER', 'EOF']
    """
    lexer = Lexer(formula)
    return lexer.tokenize()
