import json
import os
from PyQt5.QtCore import QObject, pyqtSignal


class LanguageManager(QObject):
    # Signal emitted when language changes
    language_changed = pyqtSignal(str)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True
        self.current_language = "en"  # Default language is English
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """Load all available translation files"""
        languages = ["en", "vi"]  # Add more languages as needed

        for lang in languages:
            translation_file = os.path.join(
                "resources", "l10n", f"{lang}.json")
            try:
                with open(translation_file, 'r', encoding='utf-8') as file:
                    self.translations[lang] = json.load(file)
            except FileNotFoundError:
                print(f"Translation file for {lang} not found")
                # Create empty dictionary if file doesn't exist
                self.translations[lang] = {}

    def set_language(self, language_code):
        """Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            self.language_changed.emit(language_code)
            return True
        return False

    def get_text(self, key, default=None):
        """Get translated text for a key"""
        if key in self.translations.get(self.current_language, {}):
            return self.translations[self.current_language][key]

        # Fallback to English if key not found in current language
        if key in self.translations.get("en", {}):
            return self.translations["en"][key]

        # Return the key itself or default value if provided
        return default if default is not None else key
