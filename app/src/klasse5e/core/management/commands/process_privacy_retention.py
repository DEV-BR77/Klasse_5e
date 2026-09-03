from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from klasse5e.core.models import (
    AccountDeletionRequest,
    ClassMembership,
    DepartureRetentionCase,
    GuardianChildRelationship,
    MembershipStatus,
    Role,
    RoleAssignment,
)
from klasse5e.core.privacy_services import erase_account_data


class Command(BaseCommand):
    help = "Entzieht Zugriffe bei Klassenaustritt und verarbeitet fällige Löschungen."

    def handle(self, *args, **options):
        today = timezone.localdate()
        ended = ClassMembership.objects.filter(
            Q(status=MembershipStatus.ENDED) | Q(valid_until__lt=today),
            person__studentprofile__isnull=False,
        ).select_related("person", "school_class")
        created = revoked = purged = 0
        for membership in ended:
            left_at = membership.valid_until or today
            case, was_created = DepartureRetentionCase.objects.get_or_create(
                student=membership.person,
                school_class=membership.school_class,
                defaults={"left_at": left_at, "purge_after": left_at + timedelta(days=90)},
            )
            created += int(was_created)
            if case.access_revoked_at is None:
                relationships = GuardianChildRelationship.objects.filter(
                    student_person=membership.person, status="verified"
                )
                guardian_ids = list(relationships.values_list("guardian_person_id", flat=True))
                relationships.update(status="revoked", valid_until=today)
                for guardian_id in guardian_ids:
                    has_other_child = GuardianChildRelationship.objects.filter(
                        guardian_person_id=guardian_id, status="verified"
                    ).exclude(student_person=membership.person).exists()
                    if not has_other_child:
                        ClassMembership.objects.filter(
                            person_id=guardian_id, school_class=membership.school_class
                        ).update(status=MembershipStatus.SUSPENDED, valid_until=today)
                        RoleAssignment.objects.filter(
                            user__person_id=guardian_id,
                            school_class=membership.school_class,
                            role=Role.GUARDIAN,
                        ).update(active=False)
                case.access_revoked_at = timezone.now()
                case.save(update_fields=["access_revoked_at"])
                revoked += 1
            if case.purge_after <= today and case.processed_at is None:
                if membership.person.user_id:
                    request_item, _ = AccountDeletionRequest.objects.get_or_create(
                        user=membership.person.user,
                        defaults={"execute_after": timezone.now()},
                    )
                    erase_account_data(request_item)
                case.processed_at = timezone.now()
                case.save(update_fields=["processed_at"])
                purged += 1

        for item in AccountDeletionRequest.objects.filter(
            status=AccountDeletionRequest.Status.PENDING,
            execute_after__lte=timezone.now(),
        ):
            erase_account_data(item)
            purged += 1
        if created or revoked or purged or options.get("verbosity", 1) > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Fälle neu: {created}; Zugriffe entzogen: {revoked}; gelöscht: {purged}"
                )
            )
