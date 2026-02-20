"""
DSL (Domain Specific Language) для астрологических формул

Модуль предоставляет язык для формулирования астрологических запросов:
- Логические операторы: AND/OR/NOT (и &&/||/!)
- Проверки свойств: Sun.Sign == Aries
- Сравнения: <, >, <=, >=, ==, !=, IN
- Агрегаторы: planets.Dignity, aspects.Type
- Валидацию астрологической корректности

Пример использования:
    from src.dsl import parse, evaluate

    # Парсинг формулы
    ast = parse("Sun.Sign == Capricorn AND Moon.House IN [1, 4, 7, 10]")

    # Выполнение на карте
    chart_data = {
        'planets': {
            'Sun': {'Sign': 'Capricorn', 'House': 9},
            'Moon': {'Sign': 'Aquarius', 'House': 2}
        }
    }
    result = evaluate("Sun.Sign == Capricorn", chart_data)  # True
"""

from .validator import (
    AstrologicalValidator,
    ValidationError,
    ValidationWarning,
)

from .lexer import (
    Lexer,
    Token,
    TokenType,
    LexerError,
    tokenize,
)

from .parser import (
    Parser,
    ASTNode,
    NodeType,
    ParserError,
    parse,
)

from .evaluator import (
    Evaluator,
    EvaluatorError,
    evaluate,
)

__all__ = [
    # Validator
    "AstrologicalValidator",
    "ValidationError",
    "ValidationWarning",
    # Lexer
    "Lexer",
    "Token",
    "TokenType",
    "LexerError",
    "tokenize",
    # Parser
    "Parser",
    "ASTNode",
    "NodeType",
    "ParserError",
    "parse",
    # Evaluator
    "Evaluator",
    "EvaluatorError",
    "evaluate",
]

__version__ = "1.0.0-beta"
