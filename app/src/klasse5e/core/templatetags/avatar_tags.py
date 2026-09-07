import hashlib

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from klasse5e.core.avatar_designer import AVATAR_COMPONENTS, BACKGROUND_COLORS, parse_avatar_seed

register = template.Library()


@register.simple_tag
def avatar_composite(seed, class_name=""):
    """Render a saved SVG avatar from the local, curated Open Peeps atoms."""
    config = parse_avatar_seed(seed)
    if not config:
        return ""
    layers = (
        ("body", 13, 42, 70, 47),
        ("head", 33, 12, 42, 37),
        ("face", 47, 24, 25, 20),
        ("facial-hair", 43, 33, 24, 18),
        ("accessories", 37, 27, 35, 12),
    )
    images = []
    for category, x, y, width, height in layers:
        filename = AVATAR_COMPONENTS[category][config[category]][0]
        if filename:
            url = staticfiles_storage.url(f"vendor/avatar-atoms/{category}/{filename}")
            images.append(format_html(
                '<image href="{}" x="{}%" y="{}%" width="{}%" height="{}%" preserveAspectRatio="xMidYMid meet" />',
                url, x, y, width, height,
            ))
    return format_html(
        '<svg viewBox="0 0 240 324" class="{}" role="img" aria-label="Individuell gestalteter Avatar" xmlns="http://www.w3.org/2000/svg"><rect width="240" height="324" rx="26" fill="{}" />{}</svg>',
        class_name, BACKGROUND_COLORS[config["background"]], mark_safe("".join(images)),
    )


@register.simple_tag
def local_peeps_avatar(seed_name):
    """Generiert einen dynamischen, mathematisch einzigartigen Open-Peeps Avatar.

    Erstellt unterschiedliche Frisuren, Gesichter und Farben basierend auf dem
    Namen.
    """
    name_str = str(seed_name or "Gast")

    # Eindeutiger Zahlencode aus dem Namen (Hash) für feste Zuordnung
    hash_num = int(hashlib.md5(name_str.encode("utf-8")).hexdigest(), 16)

    # 1. Gedeckte Hintergrundfarben zur Auswahl
    colors = [
        "#cbd5e1",
        "#bae6fd",
        "#c7d2fe",
        "#fbcfe8",
        "#fed7aa",
        "#bbf7d0",
        "#fef08a",
    ]
    bg_color = colors[hash_num % len(colors)]

    # 2. Verschiedene Frisuren im Open-Peeps-Stil
    hair_styles = [
        '<path d="M 12 42 Q 50 12 88 42 Q 50 28 12 42" fill="#1e293b"/>',
        '<path d="M 15 45 Q 10 20 35 25 Q 50 10 65 25 Q 90 20 85 45 Q 50 35 15 45" fill="#1e293b"/>',
        '<path d="M 12 42 C 25 20, 75 15, 88 42 C 60 30, 30 35, 12 42" fill="#1e293b"/>',
        '<circle cx="50" cy="20" r="10" fill="#1e293b"/><path d="M 20 42 Q 50 22 80 42 Q 50 32 20 42" fill="#1e293b"/>',
        "",
    ]
    chosen_hair = hair_styles[(hash_num >> 2) % len(hair_styles)]

    # 3. Verschiedene Gesichter (Brille, Augenvarianten)
    face_styles = [
        """<circle cx="35" cy="48" r="11" fill="none" stroke="#0f172a" stroke-width="4.5"/>
           <circle cx="65" cy="48" r="11" fill="none" stroke="#0f172a" stroke-width="4.5"/>
           <line x1="46" y1="48" x2="54" y2="48" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>""",
        """<rect x="23" y="38" width="22" height="18" rx="3" fill="none" stroke="#0f172a" stroke-width="4.5"/>
           <rect x="55" y="38" width="22" height="18" rx="3" fill="none" stroke="#0f172a" stroke-width="4.5"/>
           <line x1="45" y1="47" x2="55" y2="47" stroke="#0f172a" stroke-width="4.5"/>""",
        """<circle cx="35" cy="48" r="3.5" fill="#0f172a"/>
           <circle cx="65" cy="48" r="3.5" fill="#0f172a"/>
           <path d="M 28 38 Q 35 33 42 38" fill="none" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
           <path d="M 58 38 Q 65 33 72 38" fill="none" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>""",
    ]
    chosen_face = face_styles[(hash_num >> 4) % len(face_styles)]

    # 4. Verschiedene Lach-Mäuler
    mouth_styles = [
        '<path d="M 36 68 Q 50 83 64 68" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>',
        '<path d="M 42 70 Q 52 75 60 66" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>',
        '<path d="M 36 66 Q 50 86 64 66 Z" fill="#0f172a" stroke="#0f172a" stroke-width="2" stroke-linejoin="round"/>',
    ]
    chosen_mouth = mouth_styles[(hash_num >> 6) % len(mouth_styles)]

    # Zusammenbau der Vektorgrafik
    svg_html = f"""
    <svg viewBox="0 0 100 100" class="w-full h-full" xmlns="http://w3.org">
        <circle cx="50" cy="50" r="48" fill="{bg_color}" />
        {chosen_hair}
        {chosen_face}
        {chosen_mouth}
    </svg>
    """
    return mark_safe(svg_html)
