"""
Tests for i18n (internationalization) module

Tests localization functionality for English and Russian languages.
"""

import pytest
from src.i18n import Localizer, get_localizer, _


class TestLocalizerBasics:
    """Test basic Localizer functionality"""

    def test_create_english_localizer(self):
        """Test creating English localizer"""
        loc = Localizer("en")
        assert loc.lang == "en"
        assert loc.messages is not None

    def test_create_russian_localizer(self):
        """Test creating Russian localizer"""
        loc = Localizer("ru")
        assert loc.lang == "ru"
        assert loc.messages is not None

    def test_fallback_to_english(self):
        """Test fallback to English for unknown language"""
        loc = Localizer("unknown")
        # Should fallback to English
        assert loc.messages is not None

    def test_get_simple_message(self):
        """Test getting simple message without formatting"""
        loc = Localizer("en")
        msg = loc.get("info.validation_passed")
        assert msg == "Formula validation passed"

    def test_get_nested_message(self):
        """Test getting deeply nested message"""
        loc = Localizer("en")
        msg = loc.get("errors.dignity.ruler_explanation")
        assert "planet" in msg.lower()

    def test_get_nonexistent_key_returns_key(self):
        """Test that nonexistent key returns the key itself"""
        loc = Localizer("en")
        msg = loc.get("nonexistent.key.path")
        assert msg == "nonexistent.key.path"


class TestLocalizerFormatting:
    """Test message formatting with parameters"""

    def test_format_single_parameter(self):
        """Test formatting with single parameter"""
        loc = Localizer("en")
        msg = loc.get("errors.retrograde_not_allowed", planet="Sun")
        assert msg == "Sun cannot be retrograde!"

    def test_format_multiple_parameters(self):
        """Test formatting with multiple parameters"""
        loc = Localizer("en")
        msg = loc.get("errors.house_range_error", num=15)
        assert "15" in msg
        assert "1-12" in msg

    def test_format_with_missing_param(self):
        """Test formatting with missing parameter (should not crash)"""
        loc = Localizer("en")
        # Should return unformatted message or handle gracefully
        msg = loc.get("errors.retrograde_not_allowed")
        assert msg is not None

    def test_shorthand_underscore_method(self):
        """Test shorthand _() method"""
        loc = Localizer("en")
        msg1 = loc.get("info.validation_passed")
        msg2 = loc._("info.validation_passed")
        assert msg1 == msg2


class TestEnglishMessages:
    """Test English message catalog"""

    def test_error_retrograde_message(self):
        """Test retrograde error message in English"""
        loc = Localizer("en")
        msg = loc._("errors.retrograde_not_allowed", planet="Sun")
        assert msg == "Sun cannot be retrograde!"

    def test_error_house_range_message(self):
        """Test house range error in English"""
        loc = Localizer("en")
        msg = loc._("errors.house_range_error", num=15)
        assert "15" in msg

    def test_warning_planet_weak(self):
        """Test planet weak warning in English"""
        loc = Localizer("en")
        msg = loc._(
            "warnings.planet_weak", planet="Mars", dignity="fall", sign="Cancer"
        )
        assert "Mars" in msg
        assert "fall" in msg
        assert "Cancer" in msg

    def test_cli_messages(self):
        """Test CLI messages in English"""
        loc = Localizer("en")
        assert loc._("cli.checking_formula") == "Checking formula..."
        assert loc._("cli.parsing") == "Parsing..."
        assert "True" in loc._("cli.result_true")

    def test_success_messages(self):
        """Test success messages in English"""
        loc = Localizer("en")
        msg = loc._("success.formula_valid")
        assert "valid" in msg.lower()


class TestRussianMessages:
    """Test Russian message catalog"""

    def test_error_retrograde_message_ru(self):
        """Test retrograde error message in Russian"""
        loc = Localizer("ru")
        msg = loc._("errors.retrograde_not_allowed", planet="Sun")
        assert "не может быть ретроградным" in msg

    def test_error_house_range_message_ru(self):
        """Test house range error in Russian"""
        loc = Localizer("ru")
        msg = loc._("errors.house_range_error", num=15)
        assert "15" in msg
        assert "1-12" in msg

    def test_warning_planet_weak_ru(self):
        """Test planet weak warning in Russian"""
        loc = Localizer("ru")
        msg = loc._(
            "warnings.planet_weak", planet="Mars", dignity="падение", sign="Cancer"
        )
        assert "Mars" in msg
        assert "падение" in msg

    def test_cli_messages_ru(self):
        """Test CLI messages in Russian"""
        loc = Localizer("ru")
        assert "Проверка" in loc._("cli.checking_formula")
        assert "Парсинг" in loc._("cli.parsing")

    def test_success_messages_ru(self):
        """Test success messages in Russian"""
        loc = Localizer("ru")
        msg = loc._("success.formula_valid")
        assert "корректна" in msg.lower() or "валидации" in msg.lower()


class TestGlobalLocalizer:
    """Test global localizer instance"""

    def test_get_localizer_singleton(self):
        """Test that get_localizer returns singleton"""
        loc1 = get_localizer("en")
        loc2 = get_localizer("en")
        assert loc1 is loc2

    def test_get_localizer_language_change(self):
        """Test changing language creates new instance"""
        loc_en = get_localizer("en")
        loc_ru = get_localizer("ru")
        assert loc_en is not loc_ru
        assert loc_en.lang == "en"
        assert loc_ru.lang == "ru"

    def test_global_underscore_function(self):
        """Test global _() function"""
        msg = _("info.validation_passed")
        assert msg is not None
        assert isinstance(msg, str)


class TestMessageCompleteness:
    """Test that both catalogs have consistent structure"""

    def test_both_have_errors_section(self):
        """Test both catalogs have errors section"""
        loc_en = Localizer("en")
        loc_ru = Localizer("ru")
        assert "errors" in loc_en.messages
        assert "errors" in loc_ru.messages

    def test_both_have_warnings_section(self):
        """Test both catalogs have warnings section"""
        loc_en = Localizer("en")
        loc_ru = Localizer("ru")
        assert "warnings" in loc_en.messages
        assert "warnings" in loc_ru.messages

    def test_both_have_cli_section(self):
        """Test both catalogs have CLI section"""
        loc_en = Localizer("en")
        loc_ru = Localizer("ru")
        assert "cli" in loc_en.messages
        assert "cli" in loc_ru.messages

    def test_both_have_success_section(self):
        """Test both catalogs have success section"""
        loc_en = Localizer("en")
        loc_ru = Localizer("ru")
        assert "success" in loc_en.messages
        assert "success" in loc_ru.messages


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_key(self):
        """Test empty key handling"""
        loc = Localizer("en")
        msg = loc.get("")
        assert msg == ""

    def test_deep_nesting_limit(self):
        """Test very deep key nesting"""
        loc = Localizer("en")
        msg = loc.get("errors.dignity.ruler_explanation")
        assert msg is not None

    def test_unicode_handling(self):
        """Test Unicode characters in Russian"""
        loc = Localizer("ru")
        msg = loc._("errors.retrograde_not_allowed", planet="Солнце")
        assert "Солнце" in msg

    def test_multiline_messages(self):
        """Test multiline message handling"""
        loc = Localizer("en")
        msg = loc._("errors.retrograde_explanation", planet="Sun")
        assert "\n" in msg or len(msg) > 50  # Multiline should be long


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
