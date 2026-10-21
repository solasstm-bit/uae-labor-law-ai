"""Language definitions + robust auto language detection (v2.3)."""
import re

LANGS = {
    "si": {"name": "Sinhala / සිංහල", "stt": "si-LK", "tts": "si",
           "out": "Sinhala (සිංහල script). If the user writes Singlish (romanized Sinhala), still reply in proper Sinhala script", "flag": "🇱🇰"},
    "ta": {"name": "Tamil / தமிழ்", "stt": "ta-IN", "tts": "ta", "out": "Tamil (தமிழ் script)", "flag": "🇱🇰"},
    "hi": {"name": "Hindi / हिन्दी", "stt": "hi-IN", "tts": "hi", "out": "Hindi (हिन्दी script)", "flag": "🇮🇳"},
    "kn": {"name": "Kannada / ಕನ್ನಡ", "stt": "kn-IN", "tts": "kn", "out": "Kannada (ಕನ್ನಡ script)", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam / മലയാളം", "stt": "ml-IN", "tts": "ml", "out": "Malayalam (മലയാളം script)", "flag": "🇮🇳"},
    "ur": {"name": "Urdu / اردو", "stt": "ur-PK", "tts": "ur", "out": "Urdu (اردو script, RTL)", "flag": "🇵🇰"},
    "ar": {"name": "Arabic / العربية", "stt": "ar-AE", "tts": "ar", "out": "Arabic (العربية script, RTL)", "flag": "🇦🇪"},
    "bn": {"name": "Bengali / বাংলা", "stt": "bn-IN", "tts": "bn", "out": "Bengali (বাংলা script)", "flag": "🇧🇩"},
    "ne": {"name": "Nepali / नेपाली", "stt": "ne-NP", "tts": "ne", "out": "Nepali (नेपाली script)", "flag": "🇳🇵"},
    "tl": {"name": "Tagalog / Filipino", "stt": "fil-PH", "tts": "tl", "out": "Tagalog", "flag": "🇵🇭"},
    "en": {"name": "English", "stt": "en-AU", "tts": "en", "out": "English", "flag": "🇬🇧"},
}
LANG_ORDER = ["si", "ta", "hi", "kn", "ml", "ur", "ar", "bn", "ne", "tl", "en"]

# v2.3: much bigger Singlish wordlist (romanized Sinhala markers)
SINGLISH_STRONG = {
    "mama", "mata", "machan", "mchan", "machanla", "oyaa", "oyata", "oyage",
    "numba", "api", "ape", "apage", "kohomada", "koheda", "mokakda", "mokada",
    "puluvan", "puluvanda", "puluvanne", "puluvannam", "epa", "anna", "thamai",
    "thama", "kawda", "kawada", "honda", "hondama", "hari", "harima", "one",
    "onna", "karan", "karanawa", "kala", "karala", "karanna", "karannaone",
    "wenawa", "wenna", "wenne", "thiyenawa", "thibba", "tiyenna", "tiyenne",
    "denna", "danne", "kiyanna", "kiyala", "kiyannako", "ganna", "gannawa",
    "gannakama", "kapanna", "kapannaone", "viyadam", "viyadamuna", "mudala",
    "padiyen", "padiyata", "ekata", "eka", "deka", "una", "nam", "namme",
    "witharai", "witharak", "nathi", "nisa", "nisaone", "eyaa", "eyage",
    "meke", "meeka", "meekata", "meka", "salara", "salarayata", "ayeth",
    "ita", "pasakal", "himan", "labenna", "labba", "labboda", "labbewanam",
    "kalin", "dan", "danpat", "hambakaranna", "hamba", "hambawela",
    "wage", "wagema", "men", "semaye", "samaye",
}

# romanized-Sinhala verb ending patterns (weaker evidence)
SINGLISH_ENDINGS = ("anna", "anawa", "enne", "enawa", "ila", "uwa", "welaa", "wela", "eda", "akuda")


def detect_lang(text: str, fallback: str = "en") -> str:
    """Detect the question's language. Singlish -> Sinhala (robust v2.3)."""
    t = re.sub(r"[^\w\s]", " ", text.lower())
    words = set(t.split())
    strong = words & SINGLISH_STRONG
    weak = sum(1 for w in words if any(w.endswith(e) for e in SINGLISH_ENDINGS))

    if len(strong) >= 2 or (len(strong) >= 1 and weak >= 2):
        return "si"

    try:
        from langdetect import detect_langs, DetectorFactory
        DetectorFactory.seed = 0
        probs = detect_langs(text)
        top = probs[0]
        code = top.lang
        # romanized text often misfires to these languages -> trust Singlish evidence first
        if code in ("tl", "id", "ms", "sw", "so", "vi", "jv", "su") and (strong or weak >= 1):
            return "si"
        if code in LANGS:
            # low confidence + any Singlish hint -> Sinhala
            if top.prob < 0.55 and (strong or weak >= 2):
                return "si"
            return code
        return fallback if not strong else "si"
    except Exception:
        return "si" if strong else fallback