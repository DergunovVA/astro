"""
Тесты для DSL Parser

Проверяет построение AST из токенов для всех конструкций DSL.
"""

import pytest
from src.dsl.parser import Parser, ASTNode, NodeType, ParserError, parse
from src.dsl.lexer import tokenize


class TestBasicParsing:
    """Тесты базового парсинга"""

    def test_simple_identifier(self):
        """Парсинг простого идентификатора"""
        tokens = tokenize("Sun")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.IDENTIFIER
        assert ast.value == "Sun"

    def test_number(self):
        """Парсинг числа"""
        tokens = tokenize("42")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.NUMBER
        assert ast.value == 42

    def test_float_number(self):
        """Парсинг дробного числа"""
        tokens = tokenize("3.14")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.NUMBER
        assert ast.value == 3.14

    def test_string(self):
        """Парсинг строки"""
        tokens = tokenize('"Aries"')
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.STRING
        assert ast.value == "Aries"

    def test_boolean_true(self):
        """Парсинг True"""
        tokens = tokenize("True")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BOOLEAN
        assert ast.value is True

    def test_boolean_false(self):
        """Парсинг False"""
        tokens = tokenize("False")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BOOLEAN
        assert ast.value is False


class TestPropertyAccess:
    """Тесты доступа к свойствам"""

    def test_simple_property(self):
        """Sun.Sign"""
        tokens = tokenize("Sun.Sign")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.PROPERTY
        assert ast.property == "Sign"
        assert ast.object.type == NodeType.IDENTIFIER
        assert ast.object.value == "Sun"

    def test_property_with_number(self):
        """Mars.House"""
        tokens = tokenize("Mars.House")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.PROPERTY
        assert ast.property == "House"
        assert ast.object.value == "Mars"

    def test_multiple_identifiers(self):
        """Venus.Retrograde"""
        tokens = tokenize("Venus.Retrograde")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.PROPERTY
        assert ast.property == "Retrograde"
        assert ast.object.value == "Venus"


class TestComparisons:
    """Тесты операторов сравнения"""

    def test_equality(self):
        """Sun.Sign == Aries"""
        tokens = tokenize("Sun.Sign == Aries")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "=="
        assert ast.left.type == NodeType.PROPERTY
        assert ast.left.property == "Sign"
        assert ast.right.type == NodeType.IDENTIFIER
        assert ast.right.value == "Aries"

    def test_inequality(self):
        """Mars.House != 12"""
        tokens = tokenize("Mars.House != 12")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "!="
        assert ast.right.type == NodeType.NUMBER
        assert ast.right.value == 12

    def test_less_than(self):
        """Venus.Degree < 30"""
        tokens = tokenize("Venus.Degree < 30")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "<"

    def test_greater_than(self):
        """Mars.Degree > 15"""
        tokens = tokenize("Mars.Degree > 15")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == ">"

    def test_less_than_or_equal(self):
        """Jupiter.House <= 6"""
        tokens = tokenize("Jupiter.House <= 6")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "<="

    def test_greater_than_or_equal(self):
        """Saturn.House >= 7"""
        tokens = tokenize("Saturn.House >= 7")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == ">="

    def test_in_operator(self):
        """Mars.House IN [1, 4, 7, 10]"""
        tokens = tokenize("Mars.House IN [1, 4, 7, 10]")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "IN"
        assert ast.left.property == "House"
        assert ast.right.type == NodeType.LIST
        assert len(ast.right.children) == 4


class TestLists:
    """Тесты списков"""

    def test_empty_list(self):
        """Пустой список []"""
        tokens = tokenize("[]")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.LIST
        assert len(ast.children) == 0

    def test_number_list(self):
        """[1, 4, 7, 10]"""
        tokens = tokenize("[1, 4, 7, 10]")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.LIST
        assert len(ast.children) == 4
        assert all(child.type == NodeType.NUMBER for child in ast.children)
        assert [child.value for child in ast.children] == [1, 4, 7, 10]

    def test_string_list(self):
        """["Aries", "Leo", "Sagittarius"]"""
        tokens = tokenize('["Aries", "Leo", "Sagittarius"]')
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.LIST
        assert len(ast.children) == 3
        assert all(child.type == NodeType.STRING for child in ast.children)

    def test_identifier_list(self):
        """[Aries, Leo, Sagittarius]"""
        tokens = tokenize("[Aries, Leo, Sagittarius]")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.LIST
        assert len(ast.children) == 3
        assert all(child.type == NodeType.IDENTIFIER for child in ast.children)


class TestLogicalOperators:
    """Тесты логических операторов"""

    def test_and_operator(self):
        """Sun.Sign == Aries AND Moon.Sign == Taurus"""
        tokens = tokenize("Sun.Sign == Aries AND Moon.Sign == Taurus")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.COMPARISON
        assert ast.right.type == NodeType.COMPARISON

    def test_or_operator(self):
        """Mars.House == 1 OR Mars.House == 10"""
        tokens = tokenize("Mars.House == 1 OR Mars.House == 10")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "OR"

    def test_not_operator(self):
        """NOT Sun.Retrograde"""
        tokens = tokenize("NOT Sun.Retrograde")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.UNARY_OP
        assert ast.value == "NOT"
        assert ast.operand.type == NodeType.PROPERTY

    def test_complex_logical(self):
        """Sun.Sign == Aries AND (Moon.Sign == Taurus OR Moon.Sign == Scorpio)"""
        tokens = tokenize(
            "Sun.Sign == Aries AND (Moon.Sign == Taurus OR Moon.Sign == Scorpio)"
        )
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.COMPARISON  # Sun.Sign == Aries
        assert ast.right.type == NodeType.BINARY_OP  # OR inside parentheses
        assert ast.right.value == "OR"


class TestOperatorPrecedence:
    """Тесты приоритета операторов"""

    def test_not_before_and(self):
        """NOT A AND B должно быть (NOT A) AND B"""
        tokens = tokenize("NOT Sun.Retrograde AND Moon.Retrograde")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.UNARY_OP  # NOT Sun.Retrograde
        assert ast.left.value == "NOT"
        assert ast.right.type == NodeType.PROPERTY  # Moon.Retrograde

    def test_and_before_or(self):
        """A OR B AND C должно быть A OR (B AND C)"""
        tokens = tokenize(
            "Sun.Sign == Aries OR Moon.Sign == Taurus AND Mars.Sign == Gemini"
        )
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "OR"
        assert ast.left.type == NodeType.COMPARISON  # Sun.Sign == Aries
        assert ast.right.type == NodeType.BINARY_OP  # AND
        assert ast.right.value == "AND"

    def test_parentheses_override_precedence(self):
        """(A OR B) AND C"""
        tokens = tokenize(
            "(Sun.Sign == Aries OR Moon.Sign == Taurus) AND Mars.Sign == Gemini"
        )
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.BINARY_OP  # OR in parentheses
        assert ast.left.value == "OR"
        assert ast.right.type == NodeType.COMPARISON


class TestAggregators:
    """Тесты агрегаторов"""

    def test_planets_aggregator(self):
        """planets.Dignity"""
        tokens = tokenize("planets.Dignity")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.AGGREGATOR
        assert ast.aggregator == "planets"
        assert ast.property == "Dignity"

    def test_aspects_aggregator(self):
        """aspects.Type"""
        tokens = tokenize("aspects.Type")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.AGGREGATOR
        assert ast.aggregator == "aspects"
        assert ast.property == "Type"

    def test_houses_aggregator(self):
        """houses.Ruler"""
        tokens = tokenize("houses.Ruler")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.AGGREGATOR
        assert ast.aggregator == "houses"
        assert ast.property == "Ruler"


class TestParentheses:
    """Тесты скобок"""

    def test_simple_parentheses(self):
        """(Sun.Sign == Aries)"""
        tokens = tokenize("(Sun.Sign == Aries)")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "=="

    def test_nested_parentheses(self):
        """((Sun.Sign == Aries))"""
        tokens = tokenize("((Sun.Sign == Aries))")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.COMPARISON

    def test_complex_parentheses(self):
        """(A OR B) AND (C OR D)"""
        tokens = tokenize(
            "(Sun.Sign == Aries OR Moon.Sign == Taurus) AND "
            "(Mars.Sign == Gemini OR Venus.Sign == Cancer)"
        )
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.BINARY_OP
        assert ast.left.value == "OR"
        assert ast.right.type == NodeType.BINARY_OP
        assert ast.right.value == "OR"


class TestComplexFormulas:
    """Тесты сложных формул"""

    def test_complex_formula_1(self):
        """Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]"""
        tokens = tokenize("Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"
        assert ast.left.type == NodeType.COMPARISON
        assert ast.right.type == NodeType.COMPARISON
        assert ast.right.value == "IN"
        assert ast.right.right.type == NodeType.LIST

    def test_complex_formula_2(self):
        """planets.Dignity == Rulership AND aspects.Type == "Trine" """
        tokens = tokenize('planets.Dignity == Rulership AND aspects.Type == "Trine"')
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.BINARY_OP
        assert ast.left.type == NodeType.COMPARISON
        assert ast.left.left.type == NodeType.AGGREGATOR
        assert ast.right.type == NodeType.COMPARISON
        assert ast.right.right.type == NodeType.STRING

    def test_complex_formula_3(self):
        """NOT (Mars.Retrograde == True OR Venus.Retrograde == True)"""
        tokens = tokenize("NOT (Mars.Retrograde == True OR Venus.Retrograde == True)")
        parser = Parser(tokens)
        ast = parser.parse()

        assert ast.type == NodeType.UNARY_OP
        assert ast.value == "NOT"
        assert ast.operand.type == NodeType.BINARY_OP
        assert ast.operand.value == "OR"


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_empty_formula(self):
        """Пустая формула"""
        with pytest.raises(ParserError, match="Пустая формула"):
            parse("")

    def test_unexpected_token(self):
        """Неожиданный токен"""
        with pytest.raises(ParserError):
            parse("Sun.Sign ==")  # Нет правой части

    def test_missing_closing_paren(self):
        """Пропущена закрывающая скобка"""
        with pytest.raises(ParserError):
            parse("(Sun.Sign == Aries")

    def test_missing_closing_bracket(self):
        """Пропущена закрывающая квадратная скобка"""
        with pytest.raises(ParserError):
            parse("Mars.House IN [1, 4, 7")

    def test_invalid_property_access(self):
        """Некорректный доступ к свойству"""
        with pytest.raises(ParserError):
            parse("Sun.")  # Нет имени свойства


class TestConvenienceFunction:
    """Тесты convenience функции parse()"""

    def test_parse_function(self):
        """Функция parse() работает корректно"""
        ast = parse("Sun.Sign == Aries")

        assert ast.type == NodeType.COMPARISON
        assert ast.value == "=="

    def test_parse_complex(self):
        """parse() обрабатывает сложные формулы"""
        ast = parse("Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]")

        assert ast.type == NodeType.BINARY_OP
        assert ast.value == "AND"


class TestASTRepresentation:
    """Тесты строкового представления AST"""

    def test_node_repr_identifier(self):
        """repr() для IDENTIFIER"""
        node = ASTNode(type=NodeType.IDENTIFIER, value="Sun")
        assert "IDENTIFIER" in repr(node)
        assert "Sun" in repr(node)

    def test_node_repr_comparison(self):
        """repr() для COMPARISON"""
        left = ASTNode(type=NodeType.IDENTIFIER, value="Sun")
        right = ASTNode(type=NodeType.IDENTIFIER, value="Aries")
        node = ASTNode(type=NodeType.COMPARISON, value="==", left=left, right=right)

        assert "Comparison" in repr(node)
        assert "==" in repr(node)

    def test_node_repr_binary_op(self):
        """repr() для BINARY_OP"""
        left = ASTNode(type=NodeType.IDENTIFIER, value="A")
        right = ASTNode(type=NodeType.IDENTIFIER, value="B")
        node = ASTNode(type=NodeType.BINARY_OP, value="AND", left=left, right=right)

        assert "BinaryOp" in repr(node)
        assert "AND" in repr(node)
