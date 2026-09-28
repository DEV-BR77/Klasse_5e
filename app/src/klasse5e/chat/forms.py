from io import BytesIO
from uuid import uuid4

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import ChatAsset


class ChatAssetForm(forms.ModelForm):
    class Meta:
        model = ChatAsset
        fields = ("kind", "label", "value", "image", "sort_order", "is_active")
        labels = {
            "kind": "Typ",
            "label": "Bezeichnung",
            "value": "Emoji oder Text-Sticker (bei Grafik optional)",
            "image": "Sticker-Grafik (PNG, JPEG oder WebP)",
            "sort_order": "Position",
            "is_active": "Aktiv im Chat anbieten",
        }
        # Private sticker storage has no public URL; ClearableFileInput would
        # try to render the current file's inaccessible storage URL on errors.
        widgets = {"image": forms.FileInput(attrs={"accept": "image/png,image/jpeg,image/webp"})}

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not isinstance(image, UploadedFile):
            return image
        if image.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Die Grafik darf höchstens 2 MB groß sein.")
        if image.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise forms.ValidationError("Nur PNG, JPEG und WebP sind erlaubt.")
        try:
            with Image.open(image) as source:
                if source.width * source.height > 4_000_000 or getattr(source, "n_frames", 1) != 1:
                    raise forms.ValidationError("Die Grafik ist zu groß oder animiert.")
                cleaned = ImageOps.exif_transpose(source).convert("RGBA")
                cleaned.thumbnail((512, 512), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", cleaned.size)
                canvas.paste(cleaned)
                output = BytesIO()
                canvas.save(output, format="PNG", optimize=True)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise forms.ValidationError("Die Grafik konnte nicht sicher verarbeitet werden.") from exc
        if output.tell() > 2 * 1024 * 1024:
            raise forms.ValidationError("Die bereinigte Grafik ist zu groß.")
        return SimpleUploadedFile(
            f"{uuid4().hex}.png", output.getvalue(), content_type="image/png"
        )

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("kind")
        if kind == ChatAsset.Kind.EMOJI and not cleaned.get("value"):
            self.add_error("value", "Für ein Emoji ist ein Zeichen erforderlich.")
        if kind == ChatAsset.Kind.EMOJI and cleaned.get("image"):
            self.add_error("image", "Grafiken sind nur für Sticker möglich.")
        if kind == ChatAsset.Kind.STICKER and not (cleaned.get("value") or cleaned.get("image")):
            self.add_error("image", "Bitte eine Grafik hochladen oder einen Text-Sticker angeben.")
        return cleaned
