import re
import unicodedata
import warnings
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

# Deliberately small and reviewable. It masks direct insults, while reports and
# human moderation remain necessary for context-dependent bullying.
_DIRECT_INSULTS = (
    "arschloch",
    "arschlöcher",
    "blöde kuh",
    "bloede kuh",
    "dumme kuh",
    "idiot",
    "idiotin",
    "vollidiot",
    "missgeburt",
    "hurensohn",
    "schlampe",
    "wichser",
    "fick dich",
    "drecksau",
    "scheißkerl",
    "scheisskerl",
    "verpiss dich",
)


_LEET = {
    "a": "aä@4",
    "e": "e3",
    "i": "i1!|",
    "o": "oö0",
    "s": "sß5$",
    "t": "t7+",
    "u": "uü",
}


def _letters(value):
    # Keep sharp-s as one source character. The separate "ss" spelling in the
    # reviewable list still covers that common alternative.
    normalized = unicodedata.normalize("NFKD", value.lower().replace("ß", "s"))
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _pattern(phrase):
    parts = []
    for character in _letters(phrase):
        if character.isspace():
            parts.append(r"[\W_]+")
        else:
            variants = _LEET.get(character, character)
            parts.append(f"[{re.escape(variants)}]")
            parts.append(r"[\W_]*")
    if parts and parts[-1] == r"[\W_]*":
        parts.pop()
    return re.compile(rf"(?<!\w){''.join(parts)}(?!\w)", re.IGNORECASE)


def _mask(value):
    return "".join("•" if character.isalnum() else character for character in value)


def filter_chat_language(body):
    filtered = body
    hits = 0
    for phrase in sorted(_DIRECT_INSULTS, key=len, reverse=True):
        pattern = _pattern(phrase)

        def replace(match):
            nonlocal hits
            hits += 1
            return _mask(match.group(0))

        filtered = pattern.sub(replace, filtered)
    return filtered, hits


class ImagePixelationError(ValueError):
    pass


def pixelate_image(content: bytes) -> bytes:
    image = _decoded_image(content)
    reduced = image.resize(
        (max(1, image.width // 24), max(1, image.height // 24)),
        Image.Resampling.BILINEAR,
    )
    return _jpeg_bytes(reduced.resize(image.size, Image.Resampling.NEAREST), quality=78)


def sanitize_chat_image(content: bytes) -> bytes:
    return _jpeg_bytes(_decoded_image(content), quality=88)


def _decoded_image(content: bytes) -> Image.Image:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as source:
                source.load()
                if source.width * source.height > 25_000_000:
                    raise ImagePixelationError("image_too_large")
                return ImageOps.exif_transpose(source).convert("RGB")
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
    ) as exc:
        raise ImagePixelationError("invalid_image") from exc


def _jpeg_bytes(image: Image.Image, *, quality: int) -> bytes:
    output = BytesIO()
    image.save(output, format="JPEG", quality=quality, optimize=True)
    return output.getvalue()
