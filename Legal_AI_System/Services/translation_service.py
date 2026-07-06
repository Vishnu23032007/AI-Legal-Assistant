# services/translation_service.py

from deep_translator import GoogleTranslator


class TranslationService:

    def tamil_to_english(self, text: str) -> str:
        """
        Translate Tamil text to English.
        If translation fails, return original text.
        """
        try:
            return GoogleTranslator(source="ta", target="en").translate(text)
        except Exception as e:
            print("Tamil → English translation error:", e)
            return text

    def english_to_tamil(self, text: str) -> str:
        """
        Translate English text to Tamil.
        If translation fails, return original text.
        """
        try:
            return GoogleTranslator(source="en", target="ta").translate(text)
        except Exception as e:
            print("English → Tamil translation error:", e)
            return text