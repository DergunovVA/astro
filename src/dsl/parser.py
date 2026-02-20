"""
DSL Parser - построение AST из токенов

Парсер принимает последовательность токенов от Lexer и строит
Abstract Syntax Tree (AST) для последующего выполнения.

Использует рекурсивный спуск с приоритетами операторов:
    1. NOT (самый высокий)
    2. AND
    3. OR (самый низкий)

Грамматика:
    expression := term (OR term)*
    term := factor (AND factor)*
    factor := NOT factor | comparison
    comparison := primary (op primary)?
    primary := identifier | number | string | boolean | list | property | aggregator | '(' expression ')'

Примеры:
    >>> from src.dsl.lexer import tokenize
    >>> from src.dsl.parser import Parser
    >>>
    >>> tokens = tokenize("Sun.Sign == Aries")
    >>> parser = Parser(tokens)
    >>> ast = parser.parse()
    >>> print(ast.type)
    NodeType.COMPARISON
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Any, Optional


class NodeType(Enum):
    """Типы узлов AST"""

    # Операторы
    BINARY_OP = auto()  # AND, OR - бинарные логические операторы
    UNARY_OP = auto()  # NOT - унарный логический оператор
    COMPARISON = auto()  # ==, !=, <, >, <=, >=, IN - операторы сравнения

    # Доступ к данным
    PROPERTY = auto()  # Sun.Sign, Mars.House - доступ к свойству объекта
    AGGREGATOR = auto()  # planets.Dignity, aspects.Type - агрегатор

    # Литералы
    IDENTIFIER = auto()  # Sun, Aries, Mercury - идентификаторы
    NUMBER = auto()  # 123, 45.6 - числовые литералы
    STRING = auto()  # "text", 'text' - строковые литералы
    BOOLEAN = auto()  # True, False - булевы литералы
    LIST = auto()  # [1, 2, 3], [Aries, Leo] - списки


@dataclass
class ASTNode:
    """
    Узел Abstract Syntax Tree

    Attributes:
        type: Тип узла (NodeType)
        value: Значение узла (оператор, идентификатор, число и т.д.)
        left: Левый дочерний узел (для бинарных операторов)
        right: Правый дочерний узел (для бинарных операторов)
        operand: Операнд (для унарных операторов)
        object: Объект (для PROPERTY: Sun в Sun.Sign)
        property: Свойство (для PROPERTY: Sign в Sun.Sign)
        children: Список дочерних узлов (для LIST)
    """

    type: NodeType
    value: Any = None

    # Для бинарных операторов (BINARY_OP, COMPARISON)
    left: Optional["ASTNode"] = None
    right: Optional["ASTNode"] = None

    # Для унарных операторов (UNARY_OP)
    operand: Optional["ASTNode"] = None

    # Для доступа к свойствам (PROPERTY)
    object: Optional["ASTNode"] = None
    property: Optional[str] = None

    # Для агрегаторов (AGGREGATOR)
    aggregator: Optional[str] = None  # 'planets', 'aspects', 'houses'

    # Для списков (LIST)
    children: List["ASTNode"] = field(default_factory=list)

    def __repr__(self) -> str:
        """Читаемое представление узла"""
        if self.type == NodeType.BINARY_OP:
            return f"BinaryOp({self.value}: {self.left} {self.right})"
        elif self.type == NodeType.UNARY_OP:
            return f"UnaryOp({self.value}: {self.operand})"
        elif self.type == NodeType.COMPARISON:
            return f"Comparison({self.value}: {self.left} {self.right})"
        elif self.type == NodeType.PROPERTY:
            return f"Property({self.object}.{self.property})"
        elif self.type == NodeType.AGGREGATOR:
            return f"Aggregator({self.aggregator}.{self.property})"
        elif self.type == NodeType.LIST:
            return f"List({self.children})"
        else:
            return f"{self.type.name}({self.value})"


class ParserError(Exception):
    """Ошибка парсинга"""

    def __init__(self, message: str, token=None):
        self.message = message
        self.token = token

        if token:
            super().__init__(
                f"{message} на позиции (строка {token.line}, колонка {token.column})"
            )
        else:
            super().__init__(message)


class Parser:
    """
    Парсер DSL формул

    Использует рекурсивный спуск для построения AST из токенов.
    Поддерживает приоритеты операторов и скобки.

    Example:
        >>> from src.dsl.lexer import tokenize
        >>> tokens = tokenize("Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]")
        >>> parser = Parser(tokens)
        >>> ast = parser.parse()
    """

    def __init__(self, tokens: List):
        """
        Инициализация парсера

        Args:
            tokens: Список токенов от Lexer
        """
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None

    def parse(self) -> ASTNode:
        """
        Парсинг токенов в AST

        Returns:
            Корневой узел AST

        Raises:
            ParserError: Если формула некорректна
        """
        from src.dsl.lexer import TokenType

        if not self.tokens:
            raise ParserError("Пустая формула")

        # Проверяем, что формула не пустая (не только EOF)
        if len(self.tokens) == 1 and self.tokens[0].type == TokenType.EOF:
            raise ParserError("Пустая формула")

        ast = self._parse_expression()

        # Проверяем, что дошли до конца
        if self.current and self.current.type != TokenType.EOF:
            raise ParserError(f"Неожиданный токен: {self.current.value}", self.current)

        return ast

    def _advance(self) -> None:
        """Переход к следующему токену"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None

    def _expect(self, token_type) -> None:
        """
        Проверка типа текущего токена

        Args:
            token_type: Ожидаемый тип токена

        Raises:
            ParserError: Если тип не совпадает
        """
        if not self.current or self.current.type != token_type:
            raise ParserError(
                f"Ожидался {token_type.name}, получен {self.current.type.name if self.current else 'EOF'}",
                self.current,
            )

    def _parse_expression(self) -> ASTNode:
        """
        expression := term (OR term)*

        OR имеет самый низкий приоритет
        """
        from src.dsl.lexer import TokenType

        left = self._parse_term()

        while self.current and self.current.type == TokenType.OR:
            op = self.current.value
            self._advance()
            right = self._parse_term()
            left = ASTNode(type=NodeType.BINARY_OP, value=op, left=left, right=right)

        return left

    def _parse_term(self) -> ASTNode:
        """
        term := factor (AND factor)*

        AND имеет приоритет выше OR, но ниже NOT
        """
        from src.dsl.lexer import TokenType

        left = self._parse_factor()

        while self.current and self.current.type == TokenType.AND:
            op = self.current.value
            self._advance()
            right = self._parse_factor()
            left = ASTNode(type=NodeType.BINARY_OP, value=op, left=left, right=right)

        return left

    def _parse_factor(self) -> ASTNode:
        """
        factor := NOT factor | comparison

        NOT имеет самый высокий приоритет
        """
        from src.dsl.lexer import TokenType

        if self.current and self.current.type == TokenType.NOT:
            op = self.current.value
            self._advance()
            operand = self._parse_factor()
            return ASTNode(type=NodeType.UNARY_OP, value=op, operand=operand)

        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        """
        comparison := primary (op primary)?

        op := '==' | '!=' | '<' | '>' | '<=' | '>=' | 'IN'
        """
        from src.dsl.lexer import TokenType

        left = self._parse_primary()

        # Операторы сравнения
        comparison_ops = {
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
            TokenType.IN,
        }

        if self.current and self.current.type in comparison_ops:
            op = self.current.value
            self._advance()
            right = self._parse_primary()
            return ASTNode(type=NodeType.COMPARISON, value=op, left=left, right=right)

        return left

    def _parse_primary(self) -> ASTNode:
        """
        primary := number | string | boolean | identifier | list | property | aggregator | '(' expression ')'

        Основные элементы формулы
        """
        from src.dsl.lexer import TokenType

        if not self.current:
            raise ParserError("Неожиданный конец формулы")

        # Скобки - приоритет
        if self.current.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            self._advance()
            return expr

        # Числа
        if self.current.type == TokenType.NUMBER:
            value_str = self.current.value
            # Конвертируем строку в число
            value = int(value_str) if "." not in value_str else float(value_str)
            self._advance()
            return ASTNode(type=NodeType.NUMBER, value=value)

        # Строки
        if self.current.type == TokenType.STRING:
            value = self.current.value
            self._advance()
            return ASTNode(type=NodeType.STRING, value=value)

        # Булевы значения
        if self.current.type == TokenType.BOOLEAN:
            value = self.current.value == "True"
            self._advance()
            return ASTNode(type=NodeType.BOOLEAN, value=value)

        # Списки
        if self.current.type == TokenType.LBRACKET:
            return self._parse_list()

        # Агрегаторы (planets, aspects, houses)
        if self.current.type in {
            TokenType.PLANETS,
            TokenType.ASPECTS,
            TokenType.HOUSES,
        }:
            return self._parse_aggregator()

        # Идентификаторы и свойства (Sun, Sun.Sign)
        if self.current.type == TokenType.IDENTIFIER:
            return self._parse_identifier_or_property()

        raise ParserError(f"Неожиданный токен: {self.current.value}", self.current)

    def _parse_list(self) -> ASTNode:
        """
        Парсинг списка: [1, 2, 3] или [Aries, Leo, Sagittarius]
        """
        from src.dsl.lexer import TokenType

        self._expect(TokenType.LBRACKET)
        self._advance()

        children = []

        # Пустой список
        if self.current and self.current.type == TokenType.RBRACKET:
            self._advance()
            return ASTNode(type=NodeType.LIST, children=children)

        # Первый элемент
        children.append(self._parse_list_element())

        # Остальные элементы (через запятую)
        while self.current and self.current.type == TokenType.COMMA:
            self._advance()
            children.append(self._parse_list_element())

        self._expect(TokenType.RBRACKET)
        self._advance()

        return ASTNode(type=NodeType.LIST, children=children)

    def _parse_list_element(self) -> ASTNode:
        """
        Элемент списка: число, строка, булево или идентификатор
        """
        from src.dsl.lexer import TokenType

        if not self.current:
            raise ParserError("Неожиданный конец списка")

        if self.current.type == TokenType.NUMBER:
            value_str = self.current.value
            # Конвертируем строку в число
            value = int(value_str) if "." not in value_str else float(value_str)
            self._advance()
            return ASTNode(type=NodeType.NUMBER, value=value)

        if self.current.type == TokenType.STRING:
            value = self.current.value
            self._advance()
            return ASTNode(type=NodeType.STRING, value=value)

        if self.current.type == TokenType.BOOLEAN:
            value = self.current.value == "True"
            self._advance()
            return ASTNode(type=NodeType.BOOLEAN, value=value)

        if self.current.type == TokenType.IDENTIFIER:
            value = self.current.value
            self._advance()
            return ASTNode(type=NodeType.IDENTIFIER, value=value)

        raise ParserError(
            f"Недопустимый элемент списка: {self.current.value}", self.current
        )

    def _parse_aggregator(self) -> ASTNode:
        """
        Парсинг агрегатора: planets.Dignity, aspects.Type, houses.Ruler
        """
        from src.dsl.lexer import TokenType

        aggregator = self.current.value  # 'planets', 'aspects', 'houses'
        self._advance()

        # Ожидаем точку
        self._expect(TokenType.DOT)
        self._advance()

        # Ожидаем свойство
        self._expect(TokenType.IDENTIFIER)
        property_name = self.current.value
        self._advance()

        return ASTNode(
            type=NodeType.AGGREGATOR, aggregator=aggregator, property=property_name
        )

    def _parse_identifier_or_property(self) -> ASTNode:
        """
        Парсинг идентификатора или доступа к свойству

        identifier: Sun, Aries, Mercury
        property: Sun.Sign, Mars.House, Venus.Retrograde
        """
        from src.dsl.lexer import TokenType

        identifier = self.current.value
        self._advance()

        # Проверяем, есть ли точка (доступ к свойству)
        if self.current and self.current.type == TokenType.DOT:
            self._advance()

            # Ожидаем имя свойства
            self._expect(TokenType.IDENTIFIER)
            property_name = self.current.value
            self._advance()

            return ASTNode(
                type=NodeType.PROPERTY,
                object=ASTNode(type=NodeType.IDENTIFIER, value=identifier),
                property=property_name,
            )

        # Просто идентификатор
        return ASTNode(type=NodeType.IDENTIFIER, value=identifier)


def parse(formula: str) -> ASTNode:
    """
    Convenience function для парсинга формулы

    Args:
        formula: Текст формулы

    Returns:
        Корневой узел AST

    Raises:
        LexerError: Если формула некорректна на уровне токенизации
        ParserError: Если формула некорректна на уровне синтаксиса

    Example:
        >>> ast = parse("Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]")
        >>> print(ast.type)
        NodeType.BINARY_OP
    """
    from src.dsl.lexer import tokenize

    tokens = tokenize(formula)
    parser = Parser(tokens)
    return parser.parse()
