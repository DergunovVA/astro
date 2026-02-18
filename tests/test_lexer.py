"""
Tests for DSL Lexer (Tokenizer)

Tests cover:
- Basic tokenization (identifiers, operators, delimiters)
- Numbers (integers, floats)
- Strings (single/double quotes, escaping)
- Keywords (AND, OR, NOT, IN, True, False)
- Aggregators (planets, aspects, houses)
- Two-char operators (==, !=, <=, >=, &&, ||)
- Comments
- Error handling
"""

import pytest
from src.dsl.lexer import Lexer, TokenType, LexerError, tokenize


class TestBasicTokenization:
    """Test basic tokenization of simple formulas"""

    def test_simple_comparison(self):
        """Sun.Sign == Aries"""
        tokens = tokenize("Sun.Sign == Aries")

        assert len(tokens) == 6  # Sun, ., Sign, ==, Aries, EOF
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "Sun"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "Sign"
        assert tokens[3].type == TokenType.EQ
        assert tokens[4].type == TokenType.IDENTIFIER
        assert tokens[4].value == "Aries"
        assert tokens[5].type == TokenType.EOF

    def test_property_access(self):
        """Mars.House"""
        tokens = tokenize("Mars.House")

        assert len(tokens) == 4  # Mars, ., House, EOF
        assert tokens[0].value == "Mars"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].value == "House"

    def test_whitespace_ignored(self):
        """Whitespace should be ignored"""
        tokens1 = tokenize("Sun.Sign==Aries")
        tokens2 = tokenize("Sun . Sign == Aries")
        tokens3 = tokenize("  Sun  .  Sign  ==  Aries  ")

        # All should produce same tokens (except position)
        assert len(tokens1) == len(tokens2) == len(tokens3)
        for t1, t2, t3 in zip(tokens1, tokens2, tokens3):
            assert t1.type == t2.type == t3.type
            assert t1.value == t2.value == t3.value


class TestNumbers:
    """Test numeric literal tokenization"""

    def test_integer(self):
        """123"""
        tokens = tokenize("123")

        assert len(tokens) == 2  # 123, EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"

    def test_float(self):
        """45.6"""
        tokens = tokenize("45.6")

        assert len(tokens) == 2  # 45.6, EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "45.6"

    def test_number_in_comparison(self):
        """Mars.House == 10"""
        tokens = tokenize("Mars.House == 10")

        assert tokens[0].value == "Mars"
        assert tokens[2].value == "House"
        assert tokens[3].type == TokenType.EQ
        assert tokens[4].type == TokenType.NUMBER
        assert tokens[4].value == "10"

    def test_float_in_range(self):
        """Sun.Degree > 15.5"""
        tokens = tokenize("Sun.Degree > 15.5")

        assert tokens[4].type == TokenType.NUMBER
        assert tokens[4].value == "15.5"


class TestStrings:
    """Test string literal tokenization"""

    def test_double_quotes(self):
        '''"hello"'''
        tokens = tokenize('"hello"')

        assert len(tokens) == 2  # "hello", EOF
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_single_quotes(self):
        """'world'"""
        tokens = tokenize("'world'")

        assert len(tokens) == 2
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "world"

    def test_escape_sequences(self):
        r'''"hello\nworld"'''
        tokens = tokenize(r'"hello\nworld"')

        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello\nworld"

    def test_escaped_quote(self):
        r'''"She said \"hi\""'''
        tokens = tokenize(r'"She said \"hi\""')

        assert tokens[0].value == 'She said "hi"'

    def test_unclosed_string_error(self):
        """Unclosed string should raise error"""
        with pytest.raises(LexerError) as exc_info:
            tokenize('"hello')

        assert "Незакрытая строка" in str(exc_info.value)


class TestKeywords:
    """Test keyword recognition"""

    def test_logical_operators(self):
        """AND OR NOT"""
        tokens = tokenize("AND OR NOT")

        assert len(tokens) == 4  # AND, OR, NOT, EOF
        assert tokens[0].type == TokenType.AND
        assert tokens[1].type == TokenType.OR
        assert tokens[2].type == TokenType.NOT

    def test_in_operator(self):
        """Mars.House IN [1, 4, 7, 10]"""
        tokens = tokenize("Mars.House IN [1, 4, 7, 10]")

        # Mars (0), . (1), House (2), IN (3), [ (4)...
        assert tokens[3].type == TokenType.IN
        assert tokens[3].value == "IN"

    def test_boolean_literals(self):
        """True False"""
        tokens = tokenize("True False")

        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == "True"
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == "False"

    def test_case_sensitive(self):
        """Keywords are case-sensitive (AND vs and)"""
        tokens = tokenize("AND and")

        assert tokens[0].type == TokenType.AND  # AND is keyword
        assert tokens[1].type == TokenType.IDENTIFIER  # and is identifier


class TestAggregators:
    """Test aggregator keyword recognition"""

    def test_planets_aggregator(self):
        """planets.Dignity == Rulership"""
        tokens = tokenize("planets.Dignity == Rulership")

        assert tokens[0].type == TokenType.PLANETS
        assert tokens[0].value == "planets"

    def test_aspects_aggregator(self):
        """aspects.Type == Conjunction"""
        tokens = tokenize("aspects.Type == Conjunction")

        assert tokens[0].type == TokenType.ASPECTS

    def test_houses_aggregator(self):
        """houses.Ruler == Mars"""
        tokens = tokenize("houses.Ruler == Mars")

        assert tokens[0].type == TokenType.HOUSES

    def test_aggregator_case_sensitive(self):
        """Aggregators are lowercase only"""
        tokens = tokenize("planets Planets PLANETS")

        assert tokens[0].type == TokenType.PLANETS  # planets (aggregator)
        assert tokens[1].type == TokenType.IDENTIFIER  # Planets (identifier)
        assert tokens[2].type == TokenType.IDENTIFIER  # PLANETS (identifier)


class TestOperators:
    """Test operator tokenization"""

    def test_comparison_operators(self):
        """== != < > <= >="""
        tokens = tokenize("== != < > <= >=")

        assert tokens[0].type == TokenType.EQ
        assert tokens[1].type == TokenType.NEQ
        assert tokens[2].type == TokenType.LT
        assert tokens[3].type == TokenType.GT
        assert tokens[4].type == TokenType.LTE
        assert tokens[5].type == TokenType.GTE

    def test_alternate_logical_operators(self):
        """&& || !"""
        tokens = tokenize("&& || !")

        assert tokens[0].type == TokenType.AND
        assert tokens[0].value == "&&"
        assert tokens[1].type == TokenType.OR
        assert tokens[1].value == "||"
        assert tokens[2].type == TokenType.NOT
        assert tokens[2].value == "!"

    def test_mixed_logical_operators(self):
        """AND && OR || NOT !"""
        tokens = tokenize("AND && OR || NOT !")

        # Both forms should produce same token types
        assert tokens[0].type == tokens[1].type == TokenType.AND
        assert tokens[2].type == tokens[3].type == TokenType.OR
        assert tokens[4].type == tokens[5].type == TokenType.NOT


class TestDelimiters:
    """Test delimiter tokenization"""

    def test_parentheses(self):
        """( )"""
        tokens = tokenize("()")

        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN

    def test_brackets(self):
        """[ ]"""
        tokens = tokenize("[]")

        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET

    def test_list_syntax(self):
        """[1, 2, 3]"""
        tokens = tokenize("[1, 2, 3]")

        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[2].type == TokenType.COMMA
        assert tokens[3].type == TokenType.NUMBER
        assert tokens[4].type == TokenType.COMMA
        assert tokens[5].type == TokenType.NUMBER
        assert tokens[6].type == TokenType.RBRACKET

    def test_nested_parentheses(self):
        """((A AND B) OR C)"""
        tokens = tokenize("((A AND B) OR C)")

        # ( (0), ( (1), A (2), AND (3), B (4), ) (5), OR (6), C (7), ) (8)
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[5].type == TokenType.RPAREN
        assert tokens[8].type == TokenType.RPAREN


class TestComments:
    """Test comment handling"""

    def test_comment_ignored(self):
        """# This is a comment"""
        tokens = tokenize("# This is a comment")

        assert len(tokens) == 1  # Only EOF
        assert tokens[0].type == TokenType.EOF

    def test_comment_at_end(self):
        """Sun.Sign == Aries # comment"""
        tokens = tokenize("Sun.Sign == Aries # comment")

        # Comment should be ignored
        assert len(tokens) == 6  # Sun, ., Sign, ==, Aries, EOF
        assert tokens[4].value == "Aries"
        assert tokens[5].type == TokenType.EOF

    def test_multiline_with_comment(self):
        """
        Sun.Sign == Aries
        # comment line
        Moon.Sign == Taurus
        """
        formula = "Sun.Sign == Aries\n# comment\nMoon.Sign == Taurus"
        tokens = tokenize(formula)

        # Should have tokens from both lines, comment skipped
        assert any(t.value == "Sun" for t in tokens)
        assert any(t.value == "Moon" for t in tokens)
        assert all(t.value != "comment" for t in tokens)


class TestComplexFormulas:
    """Test tokenization of complex formulas"""

    def test_logical_expression(self):
        """Sun.Sign == Aries AND Moon.Sign == Taurus"""
        tokens = tokenize("Sun.Sign == Aries AND Moon.Sign == Taurus")

        assert len(tokens) == 12  # 11 tokens + EOF
        assert tokens[5].type == TokenType.AND

    def test_negation(self):
        """NOT (Venus.Retrograde == True)"""
        tokens = tokenize("NOT (Venus.Retrograde == True)")

        # NOT (0), ( (1), Venus (2), . (3), Retrograde (4), == (5), True (6), ) (7)
        assert tokens[0].type == TokenType.NOT
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[6].type == TokenType.BOOLEAN

    def test_in_list(self):
        """Mars.House IN [1, 4, 7, 10]"""
        tokens = tokenize("Mars.House IN [1, 4, 7, 10]")

        # Mars (0), . (1), House (2), IN (3), [ (4), 1 (5), , (6), 4 (7), , (8), 7 (9), , (10), 10 (11), ] (12)
        assert tokens[3].type == TokenType.IN
        assert tokens[4].type == TokenType.LBRACKET
        assert tokens[12].type == TokenType.RBRACKET

    def test_aggregator_formula(self):
        """planets.Dignity == Rulership"""
        tokens = tokenize("planets.Dignity == Rulership")

        assert tokens[0].type == TokenType.PLANETS
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].value == "Dignity"


class TestPositionTracking:
    """Test line and column position tracking"""

    def test_column_tracking(self):
        """Position tracking for single line"""
        tokens = tokenize("Sun.Sign")

        assert tokens[0].column == 0  # Sun starts at 0
        assert tokens[1].column == 3  # . at position 3
        assert tokens[2].column == 4  # Sign at position 4

    def test_line_tracking(self):
        """Position tracking for multiple lines"""
        formula = "Sun.Sign == Aries\nMoon.Sign == Taurus"
        tokens = tokenize(formula)

        # Find Moon token
        moon_token = next(t for t in tokens if t.value == "Moon")
        assert moon_token.line == 2  # Second line


class TestErrorHandling:
    """Test lexer error handling"""

    def test_unknown_character(self):
        """Unknown character should raise error"""
        with pytest.raises(LexerError) as exc_info:
            tokenize("Sun.Sign @ Aries")  # @ is invalid

        assert "Неизвестный символ" in str(exc_info.value)
        assert "@" in str(exc_info.value)

    def test_unclosed_string(self):
        """Unclosed string should raise error"""
        with pytest.raises(LexerError):
            tokenize('"hello')

    def test_invalid_escape(self):
        r"""Invalid escape sequence"""
        with pytest.raises(LexerError) as exc_info:
            tokenize(r'"hello\x"')  # \x is not valid

        assert "escape" in str(exc_info.value).lower()

    def test_error_has_position(self):
        """Errors should include position info"""
        with pytest.raises(LexerError) as exc_info:
            tokenize("Sun @ Moon")

        error = exc_info.value
        assert error.line >= 1
        assert error.column >= 0


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_string(self):
        """Empty string should return only EOF"""
        tokens = tokenize("")

        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_only_whitespace(self):
        """Only whitespace should return EOF"""
        tokens = tokenize("   \n\t  ")

        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_number_starting_with_dot(self):
        """Dot followed by number (.5) is DOT + NUMBER, not float"""
        tokens = tokenize(".5")

        assert tokens[0].type == TokenType.DOT
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "5"

    def test_consecutive_dots(self):
        """Sun..Sign should be Sun, ., ., Sign"""
        tokens = tokenize("Sun..Sign")

        assert tokens[0].value == "Sun"
        assert tokens[1].type == TokenType.DOT
        assert tokens[2].type == TokenType.DOT
        assert tokens[3].value == "Sign"


class TestConvenienceFunction:
    """Test the convenience tokenize() function"""

    def test_tokenize_function(self):
        """tokenize() should work same as Lexer.tokenize()"""
        formula = "Sun.Sign == Aries"

        # Direct lexer
        lexer = Lexer(formula)
        tokens1 = lexer.tokenize()

        # Convenience function
        tokens2 = tokenize(formula)

        # Should produce same results
        assert len(tokens1) == len(tokens2)
        for t1, t2 in zip(tokens1, tokens2):
            assert t1.type == t2.type
            assert t1.value == t2.value
