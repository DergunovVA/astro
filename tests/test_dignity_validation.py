"""
Unit-тесты для астрологического валидатора

Тестирует:
- Базовую валидацию (ретроградность, диапазоны)
- Валидацию достоинств (Ruler, Exaltation, Detriment, Fall)
- Конфликтующие комбинации
- Качество сообщений об ошибках

Запуск:
    pytest tests/test_dignity_validation.py -v
    pytest tests/test_dignity_validation.py::TestRulerValidation -v
"""

import pytest
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dsl.validator import (
    AstrologicalValidator,
    ValidationLevel,
)


@pytest.fixture
def validator():
    """Фикстура валидатора в modern режиме"""
    return AstrologicalValidator(mode="modern")


@pytest.fixture
def traditional_validator():
    """Фикстура валидатора в traditional режиме"""
    return AstrologicalValidator(mode="traditional")


# ============================================================================
# ТЕСТЫ БАЗОВОЙ ВАЛИДАЦИИ
# ============================================================================


class TestRetrogradeValidation:
    """Тесты проверки ретроградности"""

    def test_sun_cannot_be_retrograde(self, validator):
        """Sun.Retrograde == True должно выдать ошибку"""
        result = validator.check_retrograde("Sun")

        assert result is not None
        assert result.is_valid == False
        assert result.level == ValidationLevel.ERROR
        assert "Sun" in result.message
        assert "не может быть ретроградным" in result.message

    def test_moon_cannot_be_retrograde(self, validator):
        """Moon.Retrograde == True должно выдать ошибку"""
        result = validator.check_retrograde("Moon")

        assert result is not None
        assert result.is_valid == False
        assert "Moon" in result.message

    def test_mercury_can_be_retrograde(self, validator):
        """Mercury может быть ретроградным"""
        result = validator.check_retrograde("Mercury")

        assert result is None  # Нет ошибки

    def test_mars_can_be_retrograde(self, validator):
        """Mars может быть ретроградным"""
        result = validator.check_retrograde("Mars")
        assert result is None

    def test_angles_cannot_be_retrograde(self, validator):
        """Углы карты не могут быть ретроградными"""
        for angle in ["Asc", "MC", "IC", "Dsc"]:
            result = validator.check_retrograde(angle)
            assert result is not None
            assert result.is_valid == False

    def test_error_message_contains_suggestions(self, validator):
        """Сообщение об ошибке содержит предложения"""
        result = validator.check_retrograde("Sun")

        assert result.suggestions is not None
        assert len(result.suggestions) > 0
        assert "Mercury" in str(result.suggestions[0])


class TestSelfAspectValidation:
    """Тесты проверки самоаспектов"""

    def test_planet_cannot_aspect_itself(self, validator):
        """Asp(Mars, Mars, Conj) - ошибка"""
        result = validator.check_self_aspect("Mars", "Mars")

        assert result is not None
        assert result.is_valid == False
        assert result.level == ValidationLevel.ERROR
        assert "сам" in result.message.lower()

    def test_different_planets_ok(self, validator):
        """Asp(Mars, Saturn, Conj) - OK"""
        result = validator.check_self_aspect("Mars", "Saturn")

        assert result is None


class TestRangeValidation:
    """Тесты проверки диапазонов"""

    def test_valid_house_numbers(self, validator):
        """Дома 1-12 валидны"""
        for house in range(1, 13):
            result = validator.check_house_range(house)
            assert result is None

    def test_invalid_house_zero(self, validator):
        """Дом 0 невалиден"""
        result = validator.check_house_range(0)
        assert result is not None
        assert result.is_valid == False

    def test_invalid_house_13(self, validator):
        """Дом 13 невалиден"""
        result = validator.check_house_range(13)
        assert result is not None
        assert result.is_valid == False

    def test_valid_degrees_in_sign(self, validator):
        """Градусы 0-29 валидны"""
        for degree in [0, 15, 29]:
            result = validator.check_degree_range(degree, absolute=False)
            assert result is None

    def test_invalid_degree_30(self, validator):
        """Градус 30 в знаке невалиден"""
        result = validator.check_degree_range(30, absolute=False)
        assert result is not None
        assert result.is_valid == False

    def test_valid_absolute_degrees(self, validator):
        """Абсолютные градусы 0-359 валидны"""
        for degree in [0, 180, 359]:
            result = validator.check_degree_range(degree, absolute=True)
            assert result is None


# ============================================================================
# ТЕСТЫ ВАЛИДАЦИИ ДОСТОИНСТВ
# ============================================================================


class TestRulerValidation:
    """Тесты проверки управителей"""

    def test_invalid_planet_ruler_planet(self, validator):
        """Mars.Ruler == Venus должно выдать ошибку"""
        result = validator.check_ruler_usage("Mars", "Venus")

        assert result is not None
        assert result.is_valid == False
        assert result.level == ValidationLevel.ERROR
        assert "бессмысленна" in result.message
        assert "не управляет другой планетой" in result.details

    def test_ruler_sign_is_ok(self, validator):
        """Mars.Ruler == Aries (знак) - валидно на уровне базовой проверки"""
        result = validator.check_ruler_usage("Mars", "Aries")

        # check_ruler_usage проверяет только planet->planet, не planet->sign
        assert result is None

    def test_error_message_educational(self, validator):
        """Сообщение об ошибке образовательное"""
        result = validator.check_ruler_usage("Sun", "Moon")

        assert result.details is not None
        assert "Объяснение" in result.details
        assert result.suggestions is not None


class TestExaltationValidation:
    """Тесты проверки экзальтаций"""

    def test_sun_exalted_in_aries(self, validator):
        """Sun экзальтировано в Aries"""
        result = validator.check_exaltation("Sun", "Aries")

        assert result is None  # Нет ошибки

    def test_sun_not_exalted_in_taurus(self, validator):
        """Sun НЕ экзальтировано в Taurus"""
        result = validator.check_exaltation("Sun", "Taurus")

        assert result is not None
        assert result.is_valid == False
        assert result.level == ValidationLevel.ERROR
        assert "Aries" in result.message  # Указывает правильный знак
        assert "НЕ в Taurus" in result.message

    def test_moon_exalted_in_taurus(self, validator):
        """Moon экзальтировано в Taurus"""
        result = validator.check_exaltation("Moon", "Taurus")
        assert result is None

    def test_mars_exalted_in_capricorn(self, validator):
        """Mars экзальтирован в Capricorn"""
        result = validator.check_exaltation("Mars", "Capricorn")
        assert result is None

    def test_mars_not_exalted_in_aries(self, validator):
        """Mars НЕ экзальтирован в Aries (управитель, но не экзальтация)"""
        result = validator.check_exaltation("Mars", "Aries")

        assert result is not None
        assert result.is_valid == False
        assert "Capricorn" in result.message

    def test_outer_planet_exaltation_warning(self, validator):
        """Экзальтация внешней планеты - предупреждение (дискуссионно)"""
        # В зависимости от config - может быть warning
        # Пока пропускаем, так как конфиг определяет Uranus экзальтацию
        pass

    def test_all_classical_exaltations(self, validator):
        """Все классические экзальтации корректны"""
        exaltations = [
            ("Sun", "Aries"),
            ("Moon", "Taurus"),
            ("Mercury", "Virgo"),
            ("Venus", "Pisces"),
            ("Mars", "Capricorn"),
            ("Jupiter", "Cancer"),
            ("Saturn", "Libra"),
        ]

        for planet, sign in exaltations:
            result = validator.check_exaltation(planet, sign)
            assert result is None, f"{planet} должен быть экзальтирован в {sign}"


class TestConflictingDignities:
    """Тесты конфликтующих достоинств"""

    def test_rulership_and_fall_conflict(self, validator):
        """Планета не может быть одновременно в Rulership и Fall"""
        result = validator.check_conflicting_dignities("Mars", "Rulership", "Fall")

        assert result is not None
        assert result.is_valid == False
        assert result.level == ValidationLevel.ERROR
        assert "одновременно" in result.message.lower()

    def test_exaltation_and_detriment_conflict(self, validator):
        """Exaltation и Detriment конфликтуют"""
        result = validator.check_conflicting_dignities("Sun", "Exaltation", "Detriment")

        assert result is not None
        assert result.is_valid == False

    def test_same_dignity_ok(self, validator):
        """Одно и то же достоинство - не конфликт"""
        result = validator.check_conflicting_dignities("Mars", "Rulership", "Rulership")

        assert result is None

    def test_error_suggests_or_operator(self, validator):
        """Ошибка предлагает использовать OR"""
        result = validator.check_conflicting_dignities("Venus", "Rulership", "Fall")

        assert result.suggestions is not None
        assert "OR" in result.suggestions[0]


class TestDignitySignMatch:
    """Тесты соответствия планета-знак-достоинство"""

    def test_mars_rulership_in_aries_ok(self, validator):
        """Mars в Aries + Rulership = OK"""
        result = validator.check_dignity_sign_match("Mars", "Aries", "Rulership")

        assert result is None

    def test_mars_rulership_in_taurus_error(self, validator):
        """Mars в Taurus + Rulership = ERROR (Venus управляет Taurus)"""
        result = validator.check_dignity_sign_match("Mars", "Taurus", "Rulership")

        assert result is not None
        assert result.is_valid == False
        assert "Venus" in result.message  # Указывает правильного управителя

    def test_sun_exaltation_in_aries_ok(self, validator):
        """Sun в Aries + Exaltation = OK"""
        result = validator.check_dignity_sign_match("Sun", "Aries", "Exaltation")

        assert result is None

    def test_sun_exaltation_in_libra_error(self, validator):
        """Sun в Libra + Exaltation = ERROR"""
        result = validator.check_dignity_sign_match("Sun", "Libra", "Exaltation")

        assert result is not None
        assert result.is_valid == False

    def test_saturn_fall_in_aries_ok(self, validator):
        """Saturn в Aries + Fall = OK"""
        result = validator.check_dignity_sign_match("Saturn", "Aries", "Fall")

        assert result is None

    def test_saturn_fall_in_leo_error(self, validator):
        """Saturn в Leo + Fall = ERROR"""
        result = validator.check_dignity_sign_match("Saturn", "Leo", "Fall")

        assert result is not None
        assert result.is_valid == False


class TestLookupTables:
    """Тесты оптимизированных lookup таблиц"""

    def test_planet_rules_signs_built(self, validator):
        """Таблица planet_rules_signs построена"""
        assert hasattr(validator, "planet_rules_signs")
        assert "Mars" in validator.planet_rules_signs
        assert "Aries" in validator.planet_rules_signs["Mars"]

    def test_exaltation_lookup_built(self, validator):
        """Таблица exaltation_lookup построена"""
        assert hasattr(validator, "exaltation_lookup")
        assert ("Sun", "Aries") in validator.exaltation_lookup
        assert validator.exaltation_lookup[("Sun", "Aries")] == True

    def test_fall_lookup_built(self, validator):
        """Таблица fall_lookup построена"""
        assert hasattr(validator, "fall_lookup")
        assert ("Sun", "Libra") in validator.fall_lookup

    def test_detriment_lookup_built(self, validator):
        """Таблица detriment_lookup построена"""
        assert hasattr(validator, "detriment_lookup")
        assert ("Sun", "Aquarius") in validator.detriment_lookup


# ============================================================================
# ТЕСТЫ РЕЖИМОВ (TRADITIONAL VS MODERN)
# ============================================================================


class TestTraditionalVsModern:
    """Тесты различий traditional и modern режимов"""

    def test_scorpio_rulers_modern(self, validator):
        """В modern режиме у Scorpio два управителя: Mars и Pluto"""
        rulers = validator.get_ruler("Scorpio")

        assert "Mars" in rulers
        assert "Pluto" in rulers

    def test_scorpio_rulers_traditional(self, traditional_validator):
        """В traditional режиме у Scorpio один управитель: Mars"""
        rulers = traditional_validator.get_ruler("Scorpio")

        assert "Mars" in rulers
        assert "Pluto" not in rulers  # В traditional Pluto не используется

    def test_aquarius_modern(self, validator):
        """Aquarius modern: Saturn и Uranus"""
        rulers = validator.get_ruler("Aquarius")
        assert "Saturn" in rulers
        assert "Uranus" in rulers

    def test_aquarius_traditional(self, traditional_validator):
        """Aquarius traditional: только Saturn"""
        rulers = traditional_validator.get_ruler("Aquarius")
        assert "Saturn" in rulers
        assert "Uranus" not in rulers


# ============================================================================
# ТЕСТЫ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ
# ============================================================================


class TestHelperMethods:
    """Тесты вспомогательных методов валидатора"""

    def test_is_in_rulership(self, validator):
        """Проверка управления"""
        assert validator.is_in_rulership("Mars", "Aries") == True
        assert validator.is_in_rulership("Mars", "Taurus") == False
        assert validator.is_in_rulership("Venus", "Taurus") == True

    def test_is_in_exaltation(self, validator):
        """Проверка экзальтации"""
        assert validator.is_in_exaltation("Sun", "Aries") == True
        assert validator.is_in_exaltation("Sun", "Taurus") == False
        assert validator.is_in_exaltation("Moon", "Taurus") == True

    def test_is_in_fall(self, validator):
        """Проверка падения"""
        assert validator.is_in_fall("Sun", "Libra") == True
        assert validator.is_in_fall("Sun", "Aries") == False
        assert validator.is_in_fall("Saturn", "Aries") == True

    def test_is_in_detriment(self, validator):
        """Проверка изгнания"""
        assert validator.is_in_detriment("Sun", "Aquarius") == True
        assert validator.is_in_detriment("Sun", "Leo") == False
        assert validator.is_in_detriment("Mars", "Libra") == True

    def test_get_dignity_status_rulership(self, validator):
        """Определение статуса: Rulership"""
        assert validator.get_dignity_status("Mars", "Aries") == "Rulership"
        assert validator.get_dignity_status("Sun", "Leo") == "Rulership"

    def test_get_dignity_status_exaltation(self, validator):
        """Определение статуса: Exaltation"""
        assert validator.get_dignity_status("Sun", "Aries") == "Exaltation"
        assert validator.get_dignity_status("Moon", "Taurus") == "Exaltation"

    def test_get_dignity_status_fall(self, validator):
        """Определение статуса: Fall"""
        assert validator.get_dignity_status("Sun", "Libra") == "Fall"
        assert validator.get_dignity_status("Saturn", "Aries") == "Fall"

    def test_get_dignity_status_detriment(self, validator):
        """Определение статуса: Detriment"""
        assert validator.get_dignity_status("Sun", "Aquarius") == "Detriment"
        assert validator.get_dignity_status("Mars", "Libra") == "Detriment"

    def test_get_dignity_status_peregrine(self, validator):
        """Определение статуса: Peregrine (нейтральное)"""
        # Sun в Gemini - нет особых достоинств
        assert validator.get_dignity_status("Sun", "Gemini") == "Peregrine"


# ============================================================================
# ТЕСТЫ КАЧЕСТВА СООБЩЕНИЙ
# ============================================================================


class TestErrorMessages:
    """Тесты качества сообщений об ошибках"""

    def test_error_has_emoji(self, validator):
        """Сообщения об ошибках содержат emoji для визуальности"""
        result = validator.check_retrograde("Sun")
        assert "❌" in result.message

    def test_error_has_details(self, validator):
        """Сообщения содержат детальное объяснение"""
        result = validator.check_retrograde("Sun")
        assert result.details is not None
        assert "Объяснение" in result.details or "почему" in result.details.lower()

    def test_error_has_suggestions(self, validator):
        """Сообщения содержат предложения по исправлению"""
        result = validator.check_retrograde("Sun")
        assert result.suggestions is not None
        assert len(result.suggestions) > 0

    def test_all_errors_educational(self, validator):
        """Все критические ошибки образовательные"""
        test_cases = [
            validator.check_retrograde("Sun"),
            validator.check_self_aspect("Mars", "Mars"),
            validator.check_house_range(13),
            validator.check_ruler_usage("Mars", "Venus"),
            validator.check_exaltation("Sun", "Taurus"),
        ]

        for result in test_cases:
            if result and result.level == ValidationLevel.ERROR:
                # Сообщение должно быть информативным
                assert len(result.message) > 20
                # Должно быть объяснение или предложения
                assert result.details or result.suggestions


# ============================================================================
# STRESS TESTS
# ============================================================================


class TestPerformance:
    """Тесты производительности (требования: < 1ms для простой проверки)"""

    def test_lookup_performance(self, validator, benchmark):
        """O(1) lookup должен быть быстрым"""
        # pytest-benchmark автоматически измеряет время
        result = benchmark(validator.is_in_rulership, "Mars", "Aries")
        assert result == True

    def test_multiple_checks_fast(self, validator):
        """100 проверок должны выполниться быстро"""
        import time

        start = time.time()
        for _ in range(100):
            validator.check_retrograde("Mercury")
            validator.is_in_rulership("Mars", "Aries")
            validator.is_in_exaltation("Sun", "Aries")
        elapsed = time.time() - start

        # < 10ms для 100 проверок
        assert elapsed < 0.01


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_chiron_handling(self, validator):
        """Обработка Chiron (не в классических достоинствах)"""
        # Должно работать без ошибок, даже если Chiron не в конфиге
        result = validator.get_dignity_status("Chiron", "Aries")
        # Peregrine, так как нет определений
        assert result == "Peregrine"

    def test_case_sensitivity(self, validator):
        """Регистр имен (если будет поддержка)"""
        # Пока требуем точный case
        pass

    def test_empty_sign(self, validator):
        """Пустой знак"""
        result = validator.get_ruler("")
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
