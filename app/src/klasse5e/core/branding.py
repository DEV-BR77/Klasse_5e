from django.core.exceptions import ValidationError

from .models import BrandingAsset, PortalConfigurationKey, PortalConfigurationValue


def effective_branding(school_class, kind):
    class_asset = BrandingAsset.objects.filter(
        school_class=school_class, kind=kind, status=BrandingAsset.Status.ACTIVE
    ).first()
    if class_asset:
        return class_asset
    return BrandingAsset.objects.filter(
        school=school_class.school, kind=kind, status=BrandingAsset.Status.ACTIVE
    ).first()


def validate_configuration_value(key, value, *, scope):
    if scope == "school" and not key.school_override_allowed:
        raise ValidationError("Dieser Schlüssel erlaubt keine Schulüberschreibung.")
    if scope == "class" and not key.class_override_allowed:
        raise ValidationError("Dieser Schlüssel erlaubt keine Klassenüberschreibung.")
    if key.value_type == PortalConfigurationKey.ValueType.BOOLEAN and type(value) is not bool:
        raise ValidationError("Der Wert muss Ja/Nein sein.")
    if key.value_type == PortalConfigurationKey.ValueType.STRING:
        if not isinstance(value, str) or len(value) > 160:
            raise ValidationError("Der Textwert ist ungültig oder zu lang.")
        if any(token in value.lower() for token in ("<script", "javascript:", "{%", "{{")):
            raise ValidationError("Aktive Inhalte sind nicht erlaubt.")


def resolve_configuration(key_name, school_class=None):
    key = PortalConfigurationKey.objects.get(key=key_name, active=True)
    if school_class:
        item = PortalConfigurationValue.objects.filter(key=key, school_class=school_class).first()
        if item:
            return item.value
        item = PortalConfigurationValue.objects.filter(key=key, school=school_class.school).first()
        if item:
            return item.value
    item = PortalConfigurationValue.objects.filter(
        key=key, school__isnull=True, school_class__isnull=True
    ).first()
    return item.value if item else key.default_value
