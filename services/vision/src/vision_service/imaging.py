from __future__ import annotations

import hashlib
import warnings
from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


class ImageValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ValidatedImage:
    bgr: np.ndarray
    jpeg_bytes: bytes
    sha256: str
    width: int
    height: int


def validate_image(content: bytes, *, max_bytes: int, max_pixels: int) -> ValidatedImage:
    if not content or len(content) > max_bytes:
        raise ImageValidationError("invalid_image_size")
    try:
        Image.MAX_IMAGE_PIXELS = max_pixels
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as source:
                if source.format not in {"JPEG", "PNG"}:
                    raise ImageValidationError("unsupported_image_format")
                width, height = source.size
                if width <= 0 or height <= 0 or width * height > max_pixels:
                    raise ImageValidationError("image_pixel_limit_exceeded")
                normalized = ImageOps.exif_transpose(source).convert("RGB")
                output = BytesIO()
                normalized.save(output, format="JPEG", quality=90, optimize=True)
                rgb = np.asarray(normalized)
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Image.DecompressionBombError as exc:
        raise ImageValidationError("image_pixel_limit_exceeded") from exc
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageValidationError("invalid_image_content") from exc
    payload = output.getvalue()
    return ValidatedImage(
        bgr=bgr,
        jpeg_bytes=payload,
        sha256=hashlib.sha256(payload).hexdigest(),
        width=normalized.width,
        height=normalized.height,
    )
