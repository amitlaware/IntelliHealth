import re

class SafetyService:
    EMERGENCY_PATTERNS = [
        r"severe chest pain", r"chest pain.*breath", r"cannot breathe",
        r"can't breathe", r"severe difficulty breathing", r"unconscious",
        r"loss of consciousness", r"severe bleeding", r"heavy bleeding",
        r"seizure", r"stroke symptoms", r"face drooping", r"slurred speech",
        r"suicidal", r"kill myself", r"self harm", r"severe allergic reaction", r"stroke"
    ]

    def is_emergency(self, text):
        text = text.lower()
        return any(re.search(p, text) for p in self.EMERGENCY_PATTERNS)
