from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from klasse5e.core.models import AuditEvent, RoleAssignment, School, SchoolClass


class Command(BaseCommand):
    help = (
        "Führt den historischen THG-Übergangsdatensatz mit dem kanonischen "
        "THG-Wolfsburg-Datensatz zusammen. Ohne --apply werden nur die "
        "geplanten Änderungen angezeigt."
    )

    source_slug = "standard-schule"
    target_slug = "thg-wolfsburg"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="führt die bereinigende, transaktionale Datenänderung aus",
        )

    def handle(self, *args, **options):
        source = School.objects.filter(slug=self.source_slug).first()
        target = School.objects.filter(slug=self.target_slug).first()
        if source is None:
            self.stdout.write(self.style.SUCCESS("THG-Schuldatensatz ist bereits bereinigt."))
            return
        if target is None:
            raise CommandError("Der kanonische THG-Datensatz fehlt (Slug thg-wolfsburg).")

        legacy_class = SchoolClass.objects.filter(
            school=source, code="5e", school_year__label="2026/27"
        ).first()
        target_class = SchoolClass.objects.filter(
            school=target, code="5e", school_year__label="2026/27"
        ).first()
        if legacy_class is None or target_class is None:
            raise CommandError("Die beiden erwarteten THG-Klassen 5e für 2026/27 fehlen.")

        remaining = source.classes.exclude(pk__in=[legacy_class.pk]).values_list(
            "id", "code", "name"
        )
        unexpected = [item for item in remaining if item[1] != "synthetic-phase5"]
        if unexpected:
            raise CommandError(
                "Der Übergangsdatensatz enthält weitere Klassen; automatische Bereinigung "
                f"abgebrochen: {unexpected}"
            )

        plan = (
            f"{source.name} ({source.slug}) wird mit {target.name} ({target.slug}) "
            "zusammengeführt; die historische Klasse 5e wird in die aktive Klasse 5e "
            "überführt. Die interne Testklasse bleibt als archivierte Testklasse erhalten."
        )
        if not options["apply"]:
            self.stdout.write(plan)
            self.stdout.write("Keine Daten geändert. Mit --apply ausführen.")
            return

        with transaction.atomic():
            self._merge_class(legacy_class, target_class)
            self._archive_test_classes(source, target)
            source.delete()

            target.name = "Theodor-Heuss-Gymnasium Wolfsburg"
            target.short_name = "THG"
            target.address = "Martin-Luther-Straße 23"
            target.postal_code = "38440"
            target.city = "Wolfsburg"
            target.federal_state = "Niedersachsen"
            target.latitude = "52.419130"
            target.longitude = "10.768277"
            target.location_valid = True
            target.is_active = True
            target.save()
            AuditEvent.objects.create(
                actor=None,
                action="school.consolidated",
                target_type="school",
                target_id=str(target.pk),
                metadata={"source_slug": self.source_slug, "target_slug": self.target_slug},
            )

        self.stdout.write(self.style.SUCCESS("THG-Stammdaten wurden sauber zusammengeführt."))

    def _merge_class(self, source, target):
        """Moves every direct class relation while handling the role uniqueness rule."""
        for assignment in RoleAssignment.objects.filter(school_class=source):
            duplicate = RoleAssignment.objects.filter(
                user=assignment.user, school_class=target, role=assignment.role
            ).first()
            if duplicate:
                if assignment.active and not duplicate.active:
                    duplicate.active = True
                    duplicate.save(update_fields=["active"])
                assignment.delete()
                continue
            assignment.school_class = target
            assignment.school = target.school
            assignment.save(update_fields=["school_class", "school"])

        for relation in source._meta.related_objects:
            model = relation.related_model
            field_name = relation.field.name
            if model is RoleAssignment:
                continue
            records = model.objects.filter(**{field_name: source})
            if relation.one_to_one and records.exists() and model.objects.filter(
                **{field_name: target}
            ).exists():
                raise CommandError(
                    f"Doppelte Einzelzuordnung in {model._meta.label}; manuelle Prüfung nötig."
                )
            records.update(**{field_name: target})
        source.delete()

    @staticmethod
    def _archive_test_classes(source_school, target_school):
        for school_class in source_school.classes.all():
            school_class.school = target_school
            school_class.name = "Interne Testklasse (nicht produktiv)"
            school_class.display_name = "Interne Testklasse (nicht produktiv)"
            school_class.code = "test-phase5"
            school_class.status = "archived"
            school_class.save(
                update_fields=["school", "name", "display_name", "code", "status"]
            )
