from datetime import timedelta

import pytest
from django.utils import timezone

from klasse5e.core.models import ClassMembership, Role, RoleAssignment


URL = "/verwaltung/rollen/personen/"


@pytest.mark.django_db
def test_person_navigation_preserves_filters_and_assignment(client, admin_user, guardian, school_class):
    client.force_login(admin_user)
    suffix = f"?user={guardian.pk}&q=Alex&role=guardian&status=active"
    page = client.get(URL + suffix)
    html = page.content.decode()
    assert "q=Alex&amp;role=guardian&amp;status=active" in html
    response = client.post(URL + suffix, dict(action="assign", user_id=guardian.pk,
        role=Role.EDITOR, school_class_id=school_class.pk, school_id=school_class.school_id))
    assert response.status_code == 302
    assert "role=guardian&status=active" in response.url
    assignment = RoleAssignment.objects.get(user=guardian, role=Role.EDITOR)
    assert assignment.active and assignment.school_class == school_class
    response = client.post(URL + suffix, dict(action="revoke", user_id=guardian.pk, assignment_id=assignment.pk))
    assert response.status_code == 302
    assignment.refresh_from_db()
    assert not assignment.active


@pytest.mark.django_db
def test_expired_membership_does_not_appear_or_match_filters(client, admin_user, guardian, school_class):
    ClassMembership.objects.filter(person=guardian.person).update(valid_until=timezone.localdate() - timedelta(days=1))
    client.force_login(admin_user)
    page = client.get(URL + f"?user={guardian.pk}")
    assert not page.context["selected_memberships"]
    filtered = client.get(URL + f"?class={school_class.pk}")
    assert guardian.pk not in [account.pk for account in filtered.context["users"]]


@pytest.mark.django_db
def test_locked_account_cannot_receive_new_role(client, admin_user, guardian):
    guardian.locked_at = timezone.now()
    guardian.save(update_fields=["locked_at"])
    client.force_login(admin_user)
    response = client.post(URL + f"?user={guardian.pk}", dict(action="assign", user_id=guardian.pk, role=Role.EDITOR))
    assert response.status_code == 200
    assert response.context["assignment_form"].errors
    assert not RoleAssignment.objects.filter(user=guardian, role=Role.EDITOR).exists()


@pytest.mark.django_db
def test_guardian_cannot_open_or_write_people_management(client, guardian):
    client.force_login(guardian)
    assert client.get(URL).status_code == 403
    assert client.post(URL, dict(action="assign", user_id=guardian.pk, role=Role.EDITOR)).status_code == 403


@pytest.mark.django_db
def test_revoke_cannot_target_another_persons_assignment(client, admin_user, guardian):
    client.force_login(admin_user)
    assignment = RoleAssignment.objects.filter(user=admin_user, active=True).first()
    page = client.post(URL + f"?user={guardian.pk}", dict(action="revoke", user_id=guardian.pk, assignment_id=assignment.pk))
    assert page.context["people_errors"]
    assignment.refresh_from_db()
    assert assignment.active
