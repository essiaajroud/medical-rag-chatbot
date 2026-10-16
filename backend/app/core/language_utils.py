import re
import unicodedata

from langdetect import LangDetectException, detect


LANGUAGE_NAMES = {"fr": "French", "en": "English", "ar": "Arabic"}

GREETINGS = {
    "fr": "Bonjour 👋 Je suis MediBot. Comment puis-je vous aider aujourd'hui ?",
    "en": "Hello 👋 I'm MediBot. How can I help you today?",
    "ar": "مرحبًا 👋 أنا MediBot. كيف يمكنني مساعدتك اليوم؟",
}


def detect_language(text: str) -> str:
    """Detect French, English, or Arabic from the current message.

    Arabic is identified by its script. Very short Latin messages use an
    explicit greeting map; other ambiguous short messages default to English.
    Arabizi is not reliably distinguishable and is intentionally unsupported.
    """
    text = text.strip()
    if any("\u0600" <= char <= "\u06ff" for char in text):
        return "ar"
    normalized = re.sub(r"[^\w']+", " ", text.casefold()).strip()
    short_languages = {
        "bonjour": "fr", "salut": "fr", "bonsoir": "fr",
        "hello": "en", "hi": "en", "hey": "en",
    }
    if normalized in short_languages:
        return short_languages[normalized]
    if len(normalized.split()) < 3:
        # Accented French words are a useful signal in otherwise short text.
        if any(char in text.lower() for char in "àâçéèêëîïôùûüÿœ"):
            return "fr"
        return "en"
    try:
        detected = detect(text)
        return detected if detected in LANGUAGE_NAMES else "en"
    except LangDetectException:
        return "en"


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")


_GREETING_ALIASES = {
    "bonjour": "fr", "salut": "fr", "bonsoir": "fr",
    "hello": "en", "hi": "en", "hey": "en",
    "مرحبا": "ar", "السلام عليكم": "ar", "أهلا": "ar", "اهلا": "ar",
}


def get_greeting(text: str) -> str | None:
    normalized = unicodedata.normalize("NFKC", text).casefold().strip()
    normalized = re.sub(r"[\s!?.،,؛:]+", " ", normalized).strip()
    language = _GREETING_ALIASES.get(normalized)
    return GREETINGS[language] if language else None

