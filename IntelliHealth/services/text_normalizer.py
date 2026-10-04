import re

class TextNormalizer:
    @staticmethod
    def normalize(text):
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
