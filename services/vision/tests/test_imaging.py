from io import BytesIO

import pytest
from PIL import Image

from vision_service.imaging import ImageValidationError, validate_image
from vision_service.storage import Storage


def test_valid_jpeg_is_normalized_without_metadata(jpeg_bytes) -> None:
    result = validate_image(jpeg_bytes, max_bytes=1_000_000, max_pixels=1_000_000)
    assert result.width == 120
    assert result.height == 100
    with Image.open(BytesIO(result.jpeg_bytes)) as image:
        assert not image.getexif()


def test_invalid_content_is_rejected() -> None:
    with pytest.raises(ImageValidationError, match="invalid_image_content"):
        validate_image(b"not an image", max_bytes=100, max_pixels=100)


def test_upload_size_is_bounded() -> None:
    with pytest.raises(ImageValidationError, match="invalid_image_size"):
        validate_image(b"x" * 101, max_bytes=100, max_pixels=100)


def test_pixel_count_is_bounded() -> None:
    output = BytesIO()
    Image.new("RGB", (20, 20)).save(output, "PNG")
    with pytest.raises(ImageValidationError, match="image_pixel_limit_exceeded"):
        validate_image(output.getvalue(), max_bytes=10000, max_pixels=100)


def test_storage_rejects_path_traversal(tmp_path) -> None:
    storage = Storage(tmp_path)
    with pytest.raises(ValueError, match="unsafe_identifier"):
        storage.image_path("../outside", "image")
