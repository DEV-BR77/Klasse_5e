import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from klasse5e.core.models import Invitation, Person, Role, RoleAssignment, UserAccount


class Command(BaseCommand):
    help = "Creates an inactive primary administrator and writes a one-time invitation token."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--token-output", required=True)

    def handle(self, *args, **options):
        path = Path(options["token_output"])
        if path.exists():
            raise CommandError("token output already exists")
        user = UserAccount.objects.create_user(email=options["email"], is_active=False)
        person = Person.objects.create(user=user, first_name="Bootstrap", last_name="Administrator")
        invitation, token = Invitation.issue(options["email"], user)
        RoleAssignment.objects.create(user=user, role=Role.PRIMARY_ADMIN, assigned_by=user)
        path.write_text(token, encoding="utf-8")
        os.chmod(path, 0o600)
        self.stdout.write(
            f"Bootstrap prepared for account {user.pk}, person {person.pk}, invitation {invitation.pk}."
        )
