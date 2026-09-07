"""The curated, local SVG choices used by the profile avatar designer."""

from django.core.exceptions import ValidationError

AVATAR_COMPONENTS = {
    "body": (
        ("Hoodie.svg", "Hoodie"), ("Dress.svg", "Kleid"),
        ("Sweater.svg", "Pullover"), ("Striped Tee.svg", "Gestreiftes Shirt"),
        ("Turtleneck.svg", "Rollkragen"), ("Blazer Black Tee.svg", "Blazer"),
        ("Sporty Tee.svg", "Sportliches Shirt"), ("Tee Selena.svg", "T-Shirt"),
    ),
    "head": (
        ("Bangs.svg", "Pony"), ("Afro.svg", "Afro"), ("Bun.svg", "Dutt"),
        ("Cornrows.svg", "Cornrows"), ("Long Curly.svg", "Lange Locken"),
        ("Medium Straight.svg", "Mittellang"), ("Mohawk.svg", "Irokese"),
        ("Short 2.svg", "Kurz"), ("Twists.svg", "Twists"), ("Hijab.svg", "Hijab"),
        ("No Hair 1.svg", "Ohne Haare"),
    ),
    "face": (
        ("Smile.svg", "Lächeln"), ("Smile Big.svg", "Großes Lächeln"),
        ("Angry with Fang.svg", "Vampirzähne"),
        ("Calm.svg", "Ruhig"), ("Cheeky.svg", "Frech"), ("Cute.svg", "Niedlich"),
        ("Driven.svg", "Entschlossen"), ("Eyes Closed.svg", "Augen zu"),
        ("Serious.svg", "Ernst"), ("Suspicious.svg", "Neugierig"),
        ("Loving Grin 1.svg", "Grinsen"),
    ),
    "facial-hair": (
        ("", "Ohne Bart"), ("Chin.svg", "Kinnbart"), ("Full.svg", "Vollbart"),
        ("Goatee 1.svg", "Ziegenbart"), ("Moustache 1.svg", "Schnurrbart"),
        ("Moustache 5.svg", "Schnurrbart geschwungen"),
    ),
    "accessories": (
        ("", "Ohne Accessoire"), ("Glasses.svg", "Brille"),
        ("Glasses 3.svg", "Runde Brille"), ("Glasses 5.svg", "Eckige Brille"),
        ("Sunglasses.svg", "Sonnenbrille"), ("Eyepatch.svg", "Augenklappe"),
    ),
}

BACKGROUND_COLORS = ("#bae6fd", "#bbf7d0", "#fef08a", "#fbcfe8", "#fed7aa", "#ddd6fe", "#cbd5e1")
CONFIG_KEYS = ("background", "body", "head", "face", "facial-hair", "accessories")


def parse_avatar_seed(seed):
    """Return a safe avatar configuration or ``None`` for the old avatar choices."""
    values = str(seed or "").split(":")
    if len(values) != 7 or values[0] != "v2":
        return None
    try:
        indexes = [int(value) for value in values[1:]]
    except ValueError:
        return None
    limits = (len(BACKGROUND_COLORS), *(len(AVATAR_COMPONENTS[key]) for key in CONFIG_KEYS[1:]))
    if any(index < 0 or index >= limit for index, limit in zip(indexes, limits, strict=True)):
        return None
    return dict(zip(CONFIG_KEYS, indexes, strict=True))


def validate_avatar_seed(seed):
    if seed and parse_avatar_seed(seed) is None:
        raise ValidationError("Bitte wähle einen gültigen Avatar.")
    return seed


def avatar_designer_context():
    return {"components": AVATAR_COMPONENTS, "backgrounds": BACKGROUND_COLORS}
