"""
Internationalization (i18n) module for PixelPets backend.
Supports EN and RU locales.
"""

from .translations import get_text, get_locale, set_locale, SUPPORTED_LOCALES

__all__ = ['get_text', 'get_locale', 'set_locale', 'SUPPORTED_LOCALES']
