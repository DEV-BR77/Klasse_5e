from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from klasse5e.core.models import ClassDomain, School, SchoolClass, SchoolYear


class Command(BaseCommand):
    help = "Legt die Beta-Stammdaten fuer THG / Klasse 5e idempotent an."

    @transaction.atomic
    def handle(self, *args, **options):
        year, _ = SchoolYear.objects.get_or_create(
            label="2026/27",
            defaults={"starts_on": date(2026, 8, 1), "ends_on": date(2027, 7, 31), "is_active": True},
        )
        SchoolYear.objects.filter(pk=year.pk).update(is_active=True)
        SchoolYear.objects.exclude(pk=year.pk).filter(is_active=True).update(is_active=False)

        school, _ = School.objects.get_or_create(
            slug="thg-wolfsburg",
            defaults={
                "name": "Theodor-Heuss-Gymnasium Wolfsburg",
                "short_name": "THG",
                "address": "Martin-Luther-Straße 23",
                "postal_code": "38440",
                "city": "Wolfsburg",
                "federal_state": "Niedersachsen",
                "latitude": "52.419130",
                "longitude": "10.768277",
                "location_valid": True,
                "is_active": True,
            },
        )
        school.name = "Theodor-Heuss-Gymnasium Wolfsburg"
        school.short_name = "THG"
        school.address = "Martin-Luther-Straße 23"
        school.postal_code = "38440"
        school.city = "Wolfsburg"
        school.federal_state = "Niedersachsen"
        school.latitude = "52.419130"
        school.longitude = "10.768277"
        school.location_valid = True
        school.is_active = True
        school.save(
            update_fields=[
                "name",
                "short_name",
                "address",
                "postal_code",
                "city",
                "federal_state",
                "latitude",
                "longitude",
                "location_valid",
                "is_active",
                "updated_at",
            ]
        )

        school_class, _ = SchoolClass.objects.get_or_create(
            school=school,
            code="5e",
            school_year=year,
            defaults={
                "name": "5e",
                "display_name": "THG · 5e",
                "grade_level": "5",
                "status": "active",
                "valid_from": year.starts_on,
                "valid_until": year.ends_on,
            },
        )
        school_class.name = "5e"
        school_class.display_name = "THG · 5e"
        school_class.grade_level = "5"
        school_class.status = "active"
        school_class.save(update_fields=["name", "display_name", "grade_level", "status"])

        domain = ClassDomain.objects.filter(school_class=school_class).first()
        if domain is None:
            domain = ClassDomain.objects.filter(hostname="5e.klassid.de").first()
        if domain is None:
            domain = ClassDomain.objects.create(
                school_class=school_class,
                hostname="5e.klassid.de",
                is_reserved_exception=True,
                is_active=True,
            )
        else:
            domain.school_class = school_class
            domain.hostname = "5e.klassid.de"
            domain.is_reserved_exception = True
            domain.is_active = True
            domain.save(update_fields=["school_class", "hostname", "is_reserved_exception", "is_active"])

        self.stdout.write(self.style.SUCCESS("THG / Klasse 5e / 5e.klassid.de ist bereit."))
