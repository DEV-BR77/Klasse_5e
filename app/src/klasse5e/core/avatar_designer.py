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
V3_KEYS = ("background", "pose", "body", "head", "face", "facial-hair", "accessories")
# Coordinates from the upstream complete-person templates. Standing and
# sitting are distinct full-body assets, never stretched bust illustrations.
POSES = (
    {"label": "Stehend", "category": "pose/standing", "viewBox": "-180 0 1900 3300",
     "body": (-121, 634, 1645, 2500), "head": (404, 180),
     "clothes": (("crossed_arms-1.svg", "Arme verschränkt"), ("blazer-1.svg", "Blazer"))},
    {"label": "Sitzend", "category": "pose/sitting", "viewBox": "-140 0 1800 2600",
     "body": (-81, 637, 1534, 1856), "head": (345, 180),
     "clothes": (("crossed_legs.svg", "Beine gekreuzt"), ("hands_back-1.svg", "Entspannt"))},
)
HEAD_LAYERS = {
    "head": (0, 0, 473, 567), "face": (159, 186, 289, 293),
    "facial-hair": (123, 338, 280, 230), "accessories": (47, 241, 392, 138),
}


def parse_avatar_seed(seed):
    """Return a safe avatar configuration or ``None`` for the old avatar choices."""
    values = str(seed or "").split(":")
    if len(values) == 8 and values[0] == "v3":
        try:
            indexes = [int(value) for value in values[1:]]
        except ValueError:
            return None
        limits = (len(BACKGROUND_COLORS), len(POSES), 2, *(len(AVATAR_COMPONENTS[key]) for key in V3_KEYS[3:]))
        if any(index < 0 or index >= limit for index, limit in zip(indexes, limits, strict=True)):
            return None
        return dict(zip(V3_KEYS, indexes, strict=True))
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
    return {"components": AVATAR_COMPONENTS, "backgrounds": BACKGROUND_COLORS,
            "poses": POSES, "headLayers": HEAD_LAYERS}
