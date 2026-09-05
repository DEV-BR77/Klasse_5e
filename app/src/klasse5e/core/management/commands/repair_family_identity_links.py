from django.core.management.base import BaseCommand
from django.db import transaction

from klasse5e.core.models import AuditEvent, FamilyChildAccount, Person


class Command(BaseCommand):
    help = (
        "Prüft aktivierte Kinderzugänge auf ein fehlendes Personenprofil und "
        "stellt eindeutige Familienzuordnungen wieder her. Ohne --apply "
        "werden keine Daten geändert."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="führt ausschließlich eindeutige Reparaturen aus",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        checked = repaired_profiles = repaired_households = ambiguous = 0

        accounts = FamilyChildAccount.objects.select_related(
            "activated_user", "family_request__household", "family_request__access_code__school_class"
        ).order_by("pk")
        for account in accounts:
            if account.activated_user_id is None:
                continue
            checked += 1
            family = account.family_request
            target_class = family.access_code.school_class

            linked_person = Person.objects.filter(user=account.activated_user).first()
            if linked_person is None:
                candidates = (
                    Person.objects.filter(
                        user__isnull=True,
                        first_name__iexact=account.first_name,
                        last_name__iexact=account.last_name,
                        studentprofile__isnull=False,
                        classmembership__school_class=target_class,
                        classmembership__status="active",
                    )
                    .distinct()
                    .order_by("pk")
                )
                if candidates.count() != 1:
                    ambiguous += 1
                    continue
                linked_person = candidates.get()
                if apply_changes:
                    with transaction.atomic():
                        linked_person.user = account.activated_user
                        linked_person.save(update_fields=["user"])
                        AuditEvent.objects.create(
                            actor=None,
                            action="family.child_identity.repaired",
                            target_type="person",
                            target_id=str(linked_person.pk),
                            metadata={
                                "family_request_id": family.pk,
                                "child_account_id": account.pk,
                            },
                        )
                repaired_profiles += 1

            household = family.household
            if household is not None and not household.members.filter(pk=linked_person.pk).exists():
                if apply_changes:
                    household.members.add(linked_person)
                repaired_households += 1

        mode = "ausgeführt" if apply_changes else "nur geprüft"
        self.stdout.write(
            self.style.SUCCESS(
                f"Familienzugänge {mode}: {checked} geprüft; {repaired_profiles} Personenprofile "
                f"und {repaired_households} Haushaltszuordnungen reparierbar; "
                f"{ambiguous} nicht eindeutig."
            )
        )
