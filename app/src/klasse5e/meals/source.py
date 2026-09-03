import hashlib
import io
import re
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pdfplumber
from django.conf import settings
from django.db import transaction

from .models import MealDay, MealOption, MealPlan

USER_AGENT = "KlassID/0.3 protected-school-meal-reader"
MAX_SOURCE_BYTES = 15 * 1024 * 1024
PARSER_VERSION = "position-v1"

ALLERGENS = {
    "A": "Glutenhaltiges Getreide",
    "B": "Krebstiere",
    "C": "Eier",
    "D": "Fisch",
    "E": "Erdnüsse",
    "F": "Soja",
    "G": "Milch",
    "H": "Schalenfrüchte/Nüsse",
    "I": "Sellerie",
    "J": "Senf",
    "K": "Sesam",
    "L": "Schwefeldioxid/Sulfit",
    "M": "Lupine",
    "N": "Weichtiere",
}
ADDITIVES = {
    "1": "mit Farbstoff",
    "1a": "kann bei übermäßigem Verzehr abführend wirken",
    "2": "mit Konservierungsstoff",
    "3": "mit Antioxidationsmittel",
    "4": "mit Geschmacksverstärker",
    "5": "geschwefelt",
    "6": "geschwärzt",
    "7": "mit Phosphat",
    "8": "gewachst",
    "8a": "mit Süßungsmitteln",
    "8b": "enthält eine Phenylalaninquelle",
    "9": "koffeinhaltig",
    "10": "chininhaltig",
    "11": "unter Schutzatmosphäre verpackt",
}


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.current:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current:
            self.links.append((" ".join(self.text).strip(), self.current))
            self.current = None


def _fetch(url, *, max_bytes=MAX_SOURCE_BYTES):
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if parsed.scheme != "https" or not (
        hostname == "www.wollino.de"
        or hostname == "wollino.de"
        or hostname.endswith(".website-editor.net")
    ):
        raise ValueError("source_host_not_allowed")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf"})
    with urlopen(request, timeout=15) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("source_too_large")
    return data


def discover_plans():
    parser = _Links()
    parser.feed(_fetch(settings.MEAL_PLAN_SOURCE_URL, max_bytes=2 * 1024 * 1024).decode("utf-8", "replace"))
    found = {}
    for label, url in parser.links:
        path = urlparse(url).path
        if not re.search(r"\.pdf$", path, re.IGNORECASE) or "THG" not in path.upper():
            continue
        match = re.search(r"(\d{2})\.(\d{2})\.\s*-\s*(\d{2})\.(\d{2})\.(\d{4})", label)
        if not match:
            continue
        sd, sm, ed, em, year = map(int, match.groups())
        end = date(year, em, ed)
        start = date(year - (sm > em), sm, sd)
        source_id = PurePosixPath(path).name
        found[source_id] = {"source_id": source_id, "url": url, "start": start, "end": end}
    return sorted(found.values(), key=lambda item: item["start"])


_WORD_FIXES = {
    "K�sesp�tzle": "Käsespätzle",
    "R�stzwiebeln": "Röstzwiebeln",
    "Pestorahmso�e": "Pestorahmsoße",
    "Essig-�l": "Essig-Öl",
    "Gem�se-Bagel": "Gemüse-Bagel",
    "Gefl�gelkl��chen": "Geflügelklößchen",
    "Gr�nkernkl��chen": "Grünkernklößchen",
    "Dinkelbr�tchen": "Dinkelbrötchen",
}


def _fixed(text):
    for broken, corrected in _WORD_FIXES.items():
        text = text.replace(broken, corrected)
    return text


def _cell(words, x0, x1, y0, y1):
    selected = [w for w in words if x0 <= (w["x0"] + w["x1"]) / 2 < x1 and y0 <= w["top"] < y1]
    lines = []
    for word in sorted(selected, key=lambda w: (w["top"], w["x0"])):
        if not lines or abs(lines[-1][0] - word["top"]) > 5:
            lines.append([word["top"], [word["text"]]])
        else:
            lines[-1][1].append(word["text"])
    components, additives, allergens = [], [], []
    for _top, tokens in lines:
        codes = [token for token in tokens if re.fullmatch(r"(?:[A-N]|\d{1,2}[ab]?)", token)]
        clean_tokens = [
            token
            for token in tokens
            if token not in codes and not token.startswith("(") and token not in {",", ";"}
        ]
        descriptive = [token for token in clean_tokens if len(token) > 2]
        if descriptive:
            components.append(_fixed(" ".join(clean_tokens)))
        for code in codes:
            target = allergens if code in ALLERGENS else additives
            if code not in target:
                target.append(code)
    return {"components": components, "additives": additives, "allergens": allergens}


def parse_pdf(raw, starts_on):
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        if len(pdf.pages) != 1:
            raise ValueError("unexpected_page_count")
        page = pdf.pages[0]
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
        week_words = [w["text"] for w in words if w["x0"] < 130 and 120 < w["top"] < 190]
        week_match = next((int(value) for value in week_words if value.isdigit()), None)
        if week_match != starts_on.isocalendar().week:
            raise ValueError("calendar_week_mismatch")
        result = []
        columns = ((150, 350), (400, 600), (650, 850), (900, 1110))
        for offset, (x0, x1) in enumerate(columns):
            options = []
            for line, (y0, y1) in enumerate(((175, 400), (440, 650)), 1):
                option = _cell(words, x0, x1, y0, y1)
                if option["components"]:
                    options.append({"line": line, **option})
            if options:
                result.append({"date": starts_on + timedelta(days=offset), "options": options})
        if len(result) < 3 or any(len(day["options"]) != 2 for day in result):
            raise ValueError("layout_not_plausible")
        return result


@transaction.atomic
def import_plan(item):
    raw = _fetch(item["url"])
    checksum = hashlib.sha256(raw).hexdigest()
    existing = MealPlan.objects.filter(source_id=item["source_id"], checksum=checksum, status="ready").first()
    if existing:
        return existing, False
    days = parse_pdf(raw, item["start"])
    iso = item["start"].isocalendar()
    plan, _ = MealPlan.objects.update_or_create(
        source_id=item["source_id"],
        defaults={
            "iso_year": iso.year,
            "iso_week": iso.week,
            "starts_on": item["start"],
            "ends_on": item["end"],
            "source_url": item["url"],
            "checksum": checksum,
            "legend": {"additives": ADDITIVES, "allergens": ALLERGENS},
            "status": MealPlan.Status.READY,
            "parser_version": PARSER_VERSION,
            "error_code": "",
        },
    )
    plan.days.all().delete()
    for day_data in days:
        day = MealDay.objects.create(plan=plan, date=day_data["date"])
        for option in day_data["options"]:
            MealOption.objects.create(
                day=day,
                line=option["line"],
                components=option["components"],
                additive_codes=option["additives"],
                allergen_codes=option["allergens"],
            )
    return plan, True


def sync_plans():
    results = []
    for item in discover_plans():
        if item["end"] < date.today() - timedelta(days=7):
            continue
        try:
            results.append(import_plan(item))
        except Exception as exc:
            iso = item["start"].isocalendar()
            MealPlan.objects.update_or_create(
                source_id=item["source_id"],
                defaults={
                    "iso_year": iso.year,
                    "iso_week": iso.week,
                    "starts_on": item["start"],
                    "ends_on": item["end"],
                    "source_url": item["url"],
                    "checksum": "",
                    "status": MealPlan.Status.REVIEW,
                    "error_code": type(exc).__name__[:80],
                },
            )
    return results
