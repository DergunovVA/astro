"""
Тесты для DSL Evaluator

Проверяет выполнение AST на данных натальной карты.
"""

import pytest
from src.dsl.parser import parse
from src.dsl.evaluator import Evaluator, EvaluatorError, evaluate


# Фикстура с тестовыми данными карты
@pytest.fixture
def sample_chart():
    """Простая тестовая карта"""
    return {
        "planets": {
            "Sun": {
                "Sign": "Capricorn",
                "House": 9,
                "Dignity": "Neutral",
                "Retrograde": False,
                "Degree": 17.5,
            },
            "Moon": {
                "Sign": "Aquarius",
                "House": 2,
                "Dignity": "Neutral",
                "Retrograde": False,
                "Degree": 25.3,
            },
            "Mars": {
                "Sign": "Libra",
                "House": 6,
                "Dignity": "Detriment",
                "Retrograde": False,
                "Degree": 1.2,
            },
            "Mercury": {
                "Sign": "Capricorn",
                "House": 10,
                "Dignity": "Neutral",
                "Retrograde": True,
                "Degree": 12.8,
            },
            "Venus": {
                "Sign": "Capricorn",
                "House": 10,
                "Dignity": "Neutral",
                "Retrograde": False,
                "Degree": 8.4,
            },
        },
        "houses": {
            1: {"Sign": "Taurus", "Ruler": "Venus"},
            2: {"Sign": "Gemini", "Ruler": "Mercury"},
            3: {"Sign": "Cancer", "Ruler": "Moon"},
        },
        "aspects": [
            {"Planet1": "Sun", "Planet2": "Moon", "Type": "Sextile", "Orb": 1.2},
            {"Planet1": "Mars", "Planet2": "Venus", "Type": "Square", "Orb": 2.5},
        ],
    }


class TestBasicEvaluation:
    """Базовые тесты выполнения"""

    def test_simple_equality(self, sample_chart):
        """Простое сравнение: Sun.Sign == Capricorn"""
        ast = parse("Sun.Sign == Capricorn")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_simple_inequality(self, sample_chart):
        """Простое неравенство: Moon.Sign != Capricorn"""
        ast = parse("Moon.Sign != Capricorn")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_equality_false(self, sample_chart):
        """Сравнение возвращает False"""
        ast = parse("Sun.Sign == Aries")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False


class TestPropertyAccess:
    """Тесты доступа к свойствам"""

    def test_planet_sign(self, sample_chart):
        """Доступ к знаку планеты"""
        ast = parse("Mars.Sign")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result == "Libra"

    def test_planet_house(self, sample_chart):
        """Доступ к дому планеты"""
        ast = parse("Sun.House")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result == 9

    def test_planet_dignity(self, sample_chart):
        """Доступ к достоинству планеты"""
        ast = parse("Mars.Dignity")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result == "Detriment"

    def test_planet_retrograde(self, sample_chart):
        """Доступ к ретроградности"""
        ast = parse("Mercury.Retrograde")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_planet_degree(self, sample_chart):
        """Доступ к градусу планеты"""
        ast = parse("Moon.Degree")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result == 25.3

    def test_nonexistent_planet(self, sample_chart):
        """Ошибка при обращении к несуществующей планете"""
        ast = parse("Jupiter.Sign")
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="не найден"):
            evaluator.evaluate(ast)

    def test_nonexistent_property(self, sample_chart):
        """Ошибка при обращении к несуществующему свойству"""
        ast = parse("Sun.NonexistentProperty")
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="не найдено"):
            evaluator.evaluate(ast)


class TestComparisons:
    """Тесты операторов сравнения"""

    def test_numeric_greater_than(self, sample_chart):
        """Числовое сравнение >"""
        ast = parse("Sun.House > 5")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_numeric_less_than(self, sample_chart):
        """Числовое сравнение <"""
        ast = parse("Mars.House < 10")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_numeric_greater_equal(self, sample_chart):
        """Числовое сравнение >="""
        ast = parse("Sun.House >= 9")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_numeric_less_equal(self, sample_chart):
        """Числовое сравнение <="""
        ast = parse("Moon.House <= 2")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_float_comparison(self, sample_chart):
        """Сравнение дробных чисел"""
        ast = parse("Mars.Degree < 5.0")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestInOperator:
    """Тесты оператора IN"""

    def test_in_number_list(self, sample_chart):
        """IN с числовым списком"""
        ast = parse("Sun.House IN [1, 4, 7, 10]")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False  # Sun.House = 9

    def test_in_number_list_true(self, sample_chart):
        """IN с числовым списком (True)"""
        ast = parse("Moon.House IN [1, 2, 3]")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True  # Moon.House = 2

    def test_in_string_list(self, sample_chart):
        """IN со строковым списком"""
        ast = parse("Sun.Sign IN [Aries, Leo, Sagittarius]")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False  # Sun.Sign = Capricorn

    def test_in_string_list_true(self, sample_chart):
        """IN со строковым списком (True)"""
        ast = parse("Mars.Sign IN [Aries, Libra, Scorpio]")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True  # Mars.Sign = Libra

    def test_not_in_list(self, sample_chart):
        """Отрицание IN (через !=)"""
        ast = parse("NOT (Sun.Sign IN [Aries, Leo])")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestLogicalOperators:
    """Тесты логических операторов"""

    def test_and_operator_true(self, sample_chart):
        """AND оператор (True AND True = True)"""
        ast = parse("Sun.Sign == Capricorn AND Moon.Sign == Aquarius")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_and_operator_false(self, sample_chart):
        """AND оператор (True AND False = False)"""
        ast = parse("Sun.Sign == Capricorn AND Moon.Sign == Aries")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False

    def test_or_operator_true(self, sample_chart):
        """OR оператор (False OR True = True)"""
        ast = parse("Sun.Sign == Aries OR Moon.Sign == Aquarius")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_or_operator_false(self, sample_chart):
        """OR оператор (False OR False = False)"""
        ast = parse("Sun.Sign == Aries OR Moon.Sign == Taurus")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False

    def test_not_operator_true(self, sample_chart):
        """NOT оператор (NOT False = True)"""
        ast = parse("NOT (Sun.Sign == Aries)")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_not_operator_false(self, sample_chart):
        """NOT оператор (NOT True = False)"""
        ast = parse("NOT (Sun.Sign == Capricorn)")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False

    def test_complex_logical(self, sample_chart):
        """Сложная логическая формула"""
        ast = parse(
            "(Sun.Sign == Capricorn OR Moon.Sign == Aries) AND NOT Mars.Retrograde"
        )
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestAggregators:
    """Тесты агрегаторов"""

    def test_planets_aggregator(self, sample_chart):
        """Агрегатор planets.Dignity"""
        ast = parse("planets.Dignity")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert isinstance(result, list)
        assert len(result) == 5  # 5 планет в тестовой карте
        assert "Neutral" in result
        assert "Detriment" in result

    def test_planets_aggregator_with_comparison(self, sample_chart):
        """Агрегатор в сравнении (planets.Dignity содержит Detriment)"""
        # planets.Dignity == Detriment вернет список ['Neutral', 'Neutral', 'Detriment', ...]
        # Сравнение списка с одним значением даст False (список != строка)
        # Правильный способ - использовать IN
        ast = parse("Detriment IN planets.Dignity")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_houses_aggregator(self, sample_chart):
        """Агрегатор houses.Sign"""
        ast = parse("houses.Sign")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert isinstance(result, list)
        assert len(result) == 3  # 3 дома в тестовой карте
        assert "Taurus" in result
        assert "Gemini" in result
        assert "Cancer" in result

    def test_aspects_aggregator(self, sample_chart):
        """Агрегатор aspects.Type"""
        ast = parse("aspects.Type")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert isinstance(result, list)
        assert len(result) == 2  # 2 аспекта в тестовой карте
        assert "Sextile" in result
        assert "Square" in result

    def test_aggregator_in_list(self, sample_chart):
        """Проверка вхождения в агрегатор"""
        ast = parse("Capricorn IN planets.Sign")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestBooleanValues:
    """Тесты с булевыми значениями"""

    def test_retrograde_true(self, sample_chart):
        """Проверка ретроградности (True)"""
        ast = parse("Mercury.Retrograde == True")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_retrograde_false(self, sample_chart):
        """Проверка ретроградности (False)"""
        ast = parse("Mars.Retrograde == False")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_direct_boolean_access(self, sample_chart):
        """Прямой доступ к булевому значению"""
        ast = parse("Mercury.Retrograde")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestComplexFormulas:
    """Тесты сложных формул"""

    def test_multiple_conditions(self, sample_chart):
        """Множественные условия с AND"""
        ast = parse(
            "Sun.Sign == Capricorn AND Moon.House == 2 AND Mars.Dignity == Detriment"
        )
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_mixed_operators(self, sample_chart):
        """Смешанные операторы (AND, OR, NOT)"""
        ast = parse("(Sun.House > 8 AND Moon.House < 5) OR NOT Mars.Retrograde")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_nested_parentheses(self, sample_chart):
        """Вложенные скобки"""
        ast = parse(
            "((Sun.Sign == Capricorn OR Moon.Sign == Aries) AND Mars.House < 10)"
        )
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_aggregator_with_logic(self, sample_chart):
        """Агрегатор с логическими операторами"""
        ast = parse("Detriment IN planets.Dignity AND Sun.House IN [9, 10]")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_missing_planet(self, sample_chart):
        """Ошибка при отсутствии планеты"""
        ast = parse("Saturn.Sign == Capricorn")
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="не найден"):
            evaluator.evaluate(ast)

    def test_missing_property(self, sample_chart):
        """Ошибка при отсутствии свойства"""
        ast = parse("Sun.InvalidProperty")
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="не найдено"):
            evaluator.evaluate(ast)

    def test_in_with_non_list(self, sample_chart):
        """Ошибка при использовании IN с не-списком"""
        ast = parse("Sun.Sign IN Capricorn")  # Capricorn - не список
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="требует список"):
            evaluator.evaluate(ast)

    def test_aggregator_missing_property(self, sample_chart):
        """Ошибка при отсутствии свойства в агрегаторе"""
        ast = parse("planets.NonexistentProperty")
        evaluator = Evaluator(sample_chart)
        with pytest.raises(EvaluatorError, match="не найдено"):
            evaluator.evaluate(ast)

    def test_empty_chart_data(self):
        """Ошибка при пустых данных карты"""
        empty_chart = {"planets": {}}
        ast = parse("Sun.Sign == Aries")
        evaluator = Evaluator(empty_chart)
        with pytest.raises(EvaluatorError, match="не найден"):
            evaluator.evaluate(ast)


class TestConvenienceFunction:
    """Тесты convenience функции evaluate()"""

    def test_evaluate_simple(self, sample_chart):
        """Простое использование evaluate()"""
        result = evaluate("Sun.Sign == Capricorn", sample_chart)
        assert result is True

    def test_evaluate_complex(self, sample_chart):
        """Сложная формула через evaluate()"""
        result = evaluate(
            "Sun.Sign == Capricorn AND Moon.House IN [1, 2, 3]", sample_chart
        )
        assert result is True


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_empty_list(self, sample_chart):
        """Проверка вхождения в пустой список"""
        ast = parse("Sun.Sign IN []")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False

    def test_comparison_with_zero(self, sample_chart):
        """Сравнение с нулем"""
        # Добавим планету с градусом 0
        chart = sample_chart.copy()
        chart["planets"]["TestPlanet"] = {"Degree": 0}
        ast = parse("TestPlanet.Degree == 0")
        evaluator = Evaluator(chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_string_comparison_case_sensitive(self, sample_chart):
        """Сравнение строк чувствительно к регистру"""
        ast = parse("Sun.Sign == capricorn")  # lowercase
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False  # Должен быть Capricorn с большой буквы

    def test_numeric_string_comparison(self, sample_chart):
        """Сравнение числа со строкой"""
        ast = parse('Sun.House == "9"')
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is False  # 9 != "9"


class TestOperatorPrecedence:
    """Тесты приоритета операторов в выполнении"""

    def test_not_before_and(self, sample_chart):
        """NOT выполняется перед AND"""
        # NOT False AND True = True AND True = True
        ast = parse("NOT (Sun.Sign == Aries) AND Moon.Sign == Aquarius")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_and_before_or(self, sample_chart):
        """AND выполняется перед OR"""
        # False OR True AND True = False OR True = True
        ast = parse("Sun.Sign == Aries OR Moon.Sign == Aquarius AND Mars.House < 10")
        evaluator = Evaluator(sample_chart)
        result = evaluator.evaluate(ast)
        assert result is True

    def test_parentheses_override(self, sample_chart):
        """Скобки переопределяют приоритет"""
        # (False OR True) AND False = True AND False = False
        chart = sample_chart.copy()
        chart["planets"]["Mars"]["House"] = 15  # Меняем для теста
        ast = parse("(Sun.Sign == Aries OR Moon.Sign == Aquarius) AND Mars.House < 10")
        evaluator = Evaluator(chart)
        result = evaluator.evaluate(ast)
        assert result is False
