"""
Internationalization (i18n) support for Astro DSL

Provides localization for error messages, warnings, and user-facing text
in multiple languages (English and Russian).

Usage:
    from src.i18n import get_localizer

    loc = get_localizer('ru')
    message = loc._('errors.retrograde_not_allowed', planet='Sun')
"""

import os
import yaml
from typing import Dict, Any, Optional


class Localizer:
    """Internationalization support for multiple languages"""

    def __init__(self, lang: str = "en"):
        """
        Initialize localizer with specified language

        Args:
            lang: Language code ('en' or 'ru')
        """
        self.lang = lang
        self.messages = self._load_messages(lang)

    def _load_messages(self, lang: str) -> Dict[str, Any]:
        """
        Load message catalog for specified language

        Args:
            lang: Language code

        Returns:
            Dictionary with nested message keys

        Raises:
            FileNotFoundError: If locale file doesn't exist
        """
        locale_path = os.path.join(os.path.dirname(__file__), "locales", f"{lang}.yaml")

        if not os.path.exists(locale_path):
            # Fallback to English if locale not found
            if lang != "en":
                return self._load_messages("en")
            raise FileNotFoundError(f"Locale file not found: {locale_path}")

        with open(locale_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, key: str, **kwargs) -> str:
        """
        Get localized message by key with optional formatting

        Args:
            key: Dot-separated message key (e.g., 'errors.retrograde_not_allowed')
            **kwargs: Format parameters for message

        Returns:
            Localized and formatted message

        Examples:
            >>> loc = Localizer('en')
            >>> loc.get('errors.retrograde_not_allowed', planet='Sun')
            'Sun cannot be retrograde!'
        """
        # Navigate nested dictionary by dot-separated key
        keys = key.split(".")
        message = self.messages

        for k in keys:
            if isinstance(message, dict):
                message = message.get(k, key)
            else:
                # If we hit a non-dict value before the last key, return the key itself
                return key

        # If message is still a dict, return the key (we didn't reach a leaf)
        if isinstance(message, dict):
            return key

        # Format message with provided kwargs if any
        if kwargs:
            try:
                return message.format(**kwargs)
            except KeyError:
                # If formatting fails, return unformatted message
                return message

        return message

    def _(self, key: str, **kwargs) -> str:
        """
        Shorthand for get() - shorter syntax for common use

        Args:
            key: Message key
            **kwargs: Format parameters

        Returns:
            Localized message
        """
        return self.get(key, **kwargs)


# Global localizer instance (singleton pattern)
_localizer: Optional[Localizer] = None


def get_localizer(lang: str = "en") -> Localizer:
    """
    Get or create global localizer instance

    Args:
        lang: Language code ('en' or 'ru')

    Returns:
        Localizer instance

    Examples:
        >>> loc = get_localizer('ru')
        >>> loc._('errors.house_range_error', num=15)
    """
    global _localizer
    if _localizer is None or _localizer.lang != lang:
        _localizer = Localizer(lang)
    return _localizer


def _(key: str, **kwargs) -> str:
    """
    Quick access to localization with default language

    Args:
        key: Message key
        **kwargs: Format parameters

    Returns:
        Localized message from default localizer
    """
    return get_localizer()._(key, **kwargs)


__all__ = ["Localizer", "get_localizer", "_"]
