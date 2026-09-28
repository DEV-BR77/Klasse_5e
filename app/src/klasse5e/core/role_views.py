from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from klasse5e.chat.models import ChatRoom

from .models import (
    AuditEvent,
    PortalModule,
    Role,
    RoleAssignment,
    RoleModulePermission,
    School,
    SchoolClass,
    ClassMembership,
    UserAccount,
)
from .role_management import require_role_manager, set_user_role
from .module_permissions import MODULE_ACTIONS, MODULE_DESCRIPTIONS
from .ui_views import _shared


PHASE1_ROLES = {
    Role.PRIMARY_ADMIN,
    Role.CONTENT_MANAGER,
    Role.EDITOR,
    Role.MODERATOR,
}
MANAGED_ROLES = tuple((value, label) for value, label in Role.choices if value in PHASE1_ROLES)
ASSIGNABLE_ROLES = tuple(
    (value, label)
    for value, label in Role.choices
    if value in PHASE1_ROLES - {Role.PRIMARY_ADMIN}
)


def _role_label(value):
    return dict(Role.choices).get(value, value)


@login_required
@require_http_methods(["GET", "POST"])
def role_permissions(request):
    require_role_manager(request.user)
    selected_role = request.POST.get("role") or request.GET.get("role") or Role.CONTENT_MANAGER
    if selected_role not in dict(MANAGED_ROLES):
        if request.method == "POST":
            context = _shared(request, "Rollenberechtigungen", "management")
            context.update(
                role_choices=MANAGED_ROLES,
                selected_role="",
                selected_role_label="Ungültige Rolle",
                module_rows=[],
                permission_error="Die ausgewählte Rolle ist ungültig. Es wurden keine Rechte geändert.",
            )
            return render(request, "ui/role_permissions.html", context, status=400)
        selected_role = Role.CONTENT_MANAGER
    modules = list(PortalModule.objects.order_by("label", "key"))
    actions = list(RoleModulePermission.Action.choices)
    permission_error = ""
    if request.method == "POST":
        full_matrix = request.POST.get("permission_matrix") == "1"
        changes = []
        for module in modules:
            for action, _label in actions:
                permission_key = f"permission-{module.pk}-{action}"
                scope_key = f"scope-{module.pk}-{action}"
                if action not in MODULE_ACTIONS.get(module.key, set()):
                    if request.POST.get(permission_key) == "on":
                        permission_error = "Diese Aktion ist für das Modul nicht verfügbar. Es wurden keine Rechte geändert."
                        break
                    continue
                if not full_matrix and permission_key not in request.POST:
                    continue
                scope = request.POST.get(scope_key)
                enabled_value = request.POST.get(permission_key)
                if (full_matrix and scope is None) or (scope is not None and scope not in dict(RoleModulePermission.Scope.choices)):
                    permission_error = "Das Formular ist unvollständig oder enthält einen ungültigen Geltungsbereich. Es wurden keine Rechte geändert."
                    break
                if enabled_value not in (None, "on", "off"):
                    permission_error = "Eine Berechtigung enthält einen ungültigen Wert. Es wurden keine Rechte geändert."
                    break
                changes.append((module, action, enabled_value == "on", scope or RoleModulePermission.Scope.CLASS))
            if permission_error:
                break
        if not changes and not permission_error:
            permission_error = "Es wurden keine Berechtigungen übermittelt."
        if not permission_error:
            with transaction.atomic():
                for module, action, enabled, scope in changes:
                    permission, _ = RoleModulePermission.objects.get_or_create(
                        role=selected_role, module=module, action=action,
                        defaults={"updated_by": request.user, "scope": scope, "active": enabled},
                    )
                    if permission.active != enabled or permission.scope != scope or permission.updated_by_id != request.user.pk:
                        permission.active = enabled
                        permission.scope = scope
                        permission.updated_by = request.user
                        permission.save(update_fields=["active", "scope", "updated_by", "updated_at"])
                AuditEvent.objects.create(
                    actor=request.user,
                    action="role.permissions.updated",
                    target_type="role",
                    target_id=selected_role,
                    metadata={"role": selected_role},
                )
            messages.success(request, f"Berechtigungen für {_role_label(selected_role)} gespeichert.")
            return redirect(f"{reverse('role-permissions')}?role={selected_role}")
    existing = {
        (item.module_id, item.action): item
        for item in RoleModulePermission.objects.filter(role=selected_role)
    }
    module_rows = []
    for module in modules:
        permission_items = []
        for action, label in actions:
            if action not in MODULE_ACTIONS.get(module.key, set()):
                continue
            permission = existing.get((module.pk, action))
            enabled = bool(permission and permission.active)
            scope = permission.scope if permission else RoleModulePermission.Scope.CLASS
            if permission_error:
                enabled = request.POST.get(f"permission-{module.pk}-{action}") == "on"
                scope = request.POST.get(f"scope-{module.pk}-{action}") or scope
            permission_items.append({
                "value": action, "label": label, "enabled": enabled, "scope": scope,
            })
        module_rows.append({
            "module": module,
            "permissions": permission_items,
            "description": MODULE_DESCRIPTIONS.get(module.key, ""),
        })
    context = _shared(request, "Rollenberechtigungen", "management")
    context.update(
        role_choices=MANAGED_ROLES,
        selected_role=selected_role,
        selected_role_label=_role_label(selected_role),
        module_rows=module_rows,
        scopes=RoleModulePermission.Scope.choices,
        permission_error=permission_error,
    )
    return render(request, "ui/role_permissions.html", context, status=400 if permission_error else 200)


class PersonRoleForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=UserAccount.objects.filter(is_active=True, locked_at__isnull=True), label="Person")
    role = forms.ChoiceField(choices=ASSIGNABLE_ROLES, label="Rolle")
    school_id = forms.ModelChoiceField(queryset=School.objects.filter(is_active=True), required=False, label="Schule")
    school_class_id = forms.ModelChoiceField(queryset=SchoolClass.objects.filter(status="active"), required=False, label="Klasse")

    def clean(self):
        data = super().clean()
        if data.get("school_id") and data.get("school_class_id"):
            if data["school_class_id"].school_id != data["school_id"].pk:
                raise ValidationError("Die Klasse gehört nicht zur gewählten Schule.")
        return data


@login_required
@require_http_methods(["GET", "POST"])
def role_people(request):
    from django.db.models import Q
    from django.http import Http404
    from urllib.parse import urlencode

    require_role_manager(request.user)
    errors = []
    filter_values = {key: request.GET[key] for key in ("q", "school", "class", "role", "status") if request.GET.get(key)}
    filter_suffix = "&" + urlencode(filter_values) if filter_values else ""
    selected_id = request.POST.get("user_id") if request.method == "POST" else request.GET.get("user")
    try:
        selected_user = forms.ModelChoiceField(queryset=UserAccount.objects.select_related("person"), required=False).clean(selected_id)
    except ValidationError:
        raise Http404("Person nicht gefunden.") from None
    assignment_form = PersonRoleForm(
        request.POST if request.method == "POST" and request.POST.get("action") == "assign" else None,
        initial={"user_id": selected_user.pk if selected_user else None},
    )
    assignment_form.fields["user_id"].widget = forms.HiddenInput()
    if request.method == "POST":
        try:
            with transaction.atomic():
                action = request.POST.get("action")
                if action == "assign":
                    form = assignment_form
                    if not form.is_valid():
                        raise ValidationError([error for values in form.errors.values() for error in values])
                    data = form.cleaned_data
                    school_class = data["school_class_id"]
                    assignment, created = RoleAssignment.objects.get_or_create(
                        user=data["user_id"], role=data["role"],
                        school=None if school_class else data["school_id"], school_class=school_class,
                        defaults={"assigned_by": request.user, "active": True},
                    )
                    if not created and not assignment.active:
                        assignment.active = True
                        assignment.assigned_by = request.user
                        assignment.save(update_fields=["active", "assigned_by"])
                    AuditEvent.objects.create(actor=request.user, action="role.granted",
                        target_type="role_assignment", target_id=str(assignment.pk),
                        metadata={"role": data["role"], "user_id": data["user_id"].pk})
                elif action == "revoke":
                    assignment = forms.ModelChoiceField(queryset=RoleAssignment.objects.filter(
                        user=selected_user, active=True)).clean(request.POST.get("assignment_id"))
                    if assignment.role in {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN,
                                           Role.PARENT_REPRESENTATIVE, Role.DEPUTY_PARENT_REPRESENTATIVE}:
                        set_user_role(request.user, assignment.user, assignment.role,
                                      school_class=assignment.school_class, active=False)
                    else:
                        assignment.active = False
                        assignment.assigned_by = request.user
                        assignment.save(update_fields=["active", "assigned_by"])
                        AuditEvent.objects.create(actor=request.user, action="role.revoked",
                            target_type="role_assignment", target_id=str(assignment.pk),
                            metadata={"role": assignment.role, "user_id": assignment.user_id})
                else:
                    raise ValidationError("Unbekannte Aktion.")
            messages.success(request, "Rollenzuweisung gespeichert.")
            return redirect(f"{reverse('role-people')}?{urlencode({'user': selected_user.pk})}{filter_suffix}")
        except ValidationError as exc:
            errors = exc.messages
    query = request.GET.get("q", "").strip()
    school_id = request.GET.get("school", "").strip()
    class_id = request.GET.get("class", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")
    today = timezone.localdate()
    current_memberships = ClassMembership.objects.filter(status="active", valid_from__lte=today).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )
    users = UserAccount.objects.select_related("person").prefetch_related("roleassignment_set").order_by("person__last_name", "person__first_name", "email")
    if query:
        users = users.filter(Q(email__icontains=query) | Q(person__first_name__icontains=query) | Q(person__last_name__icontains=query))
    for value, model, lookup in (
        (school_id, School, "person__classmembership__school_class__school"),
        (class_id, SchoolClass, "person__classmembership__school_class"),
    ):
        if value:
            try:
                choice = forms.ModelChoiceField(queryset=model.objects.all()).clean(value)
                membership_field = "school_class__school" if model is School else "school_class"
                current_memberships = current_memberships.filter(**{membership_field: choice})
            except ValidationError:
                users = users.none()
                errors.append("Der gewählte Schul- oder Klassenfilter ist ungültig.")
    if school_id or class_id:
        users = users.filter(person__pk__in=current_memberships.values("person_id"))
    if role in Role.values:
        users = users.filter(roleassignment__role=role, roleassignment__active=True)
    if status == "active":
        users = users.filter(is_active=True, locked_at__isnull=True)
    elif status == "inactive":
        users = users.filter(Q(is_active=False) | Q(locked_at__isnull=False))
    users = list(users.distinct())
    people = [getattr(account, "person", None) for account in users]
    person_ids = [person.pk for person in people if person]
    if selected_user and getattr(selected_user, "person", None):
        person_ids.append(selected_user.person.pk)
    membership_rows = ClassMembership.objects.filter(
        person_id__in=person_ids, status="active", valid_from__lte=today
    ).filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today)).select_related("school_class", "school_class__school", "school_class__school_year").order_by("school_class__school__name", "school_class__name")
    memberships_by_person = {}
    for membership in membership_rows:
        memberships_by_person.setdefault(membership.person_id, []).append(membership)
    for account, person in zip(users, people):
        account.active_memberships = memberships_by_person.get(person.pk, []) if person else []
        account.active_roles = [assignment for assignment in account.roleassignment_set.all() if assignment.active]
    context = _shared(request, "Personenverwaltung", "management")
    context.update(
        users=users, selected_user=selected_user, people_errors=errors,
        assignment_form=assignment_form,
        selected_memberships=memberships_by_person.get(selected_user.person.pk, []) if selected_user and getattr(selected_user, "person", None) else [],
        filter_suffix=filter_suffix,
        selected_assignments=RoleAssignment.objects.filter(user=selected_user, active=True).select_related("school", "school_class") if selected_user else [],
        assignable_roles=ASSIGNABLE_ROLES,
        schools=School.objects.filter(is_active=True).order_by("name"),
        school_classes=SchoolClass.objects.filter(status="active").select_related("school").order_by("school__name", "name"),
        query=query, selected_school=school_id, selected_class=class_id,
        filter_roles=Role.choices, selected_role=role, selected_status=status,
    )
    return render(request, "ui/role_people.html", context)

class UserRoleForm(forms.Form):
    user = forms.ModelChoiceField(label="Benutzerkonto", queryset=UserAccount.objects.all())
    role = forms.ChoiceField(label="Rolle", choices=[
        (Role.DEPUTY_ADMIN, "Stellvertretender Administrator"),
        (Role.PARENT_REPRESENTATIVE, "Elternvertretung"),
        (Role.DEPUTY_PARENT_REPRESENTATIVE, "Stellvertretende Elternvertretung"),
    ])
    school_class = forms.ModelChoiceField(
        label="Klasse (nur für Elternvertretung)", queryset=SchoolClass.objects.all(), required=False,
    )
    action = forms.ChoiceField(label="Aktion", choices=[("grant", "Vergeben"), ("revoke", "Entziehen")])


class RepresentativeRoomForm(forms.Form):
    room = forms.ModelChoiceField(label="Chatraum", queryset=ChatRoom.objects.filter(event=None))
    enabled = forms.BooleanField(label="Als Elternvertreter-Chat verwenden", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].label_from_instance = lambda room: f"{room.school_class} · {room.title}"


@login_required
@require_http_methods(["GET", "POST"])
def role_management(request):
    require_role_manager(request.user)
    if request.method == "POST" and not request.POST.get("form"):
        action = request.POST.get("action")
        if action == "revoke":
            assignment_id = request.POST.get("assignment_id", "")
            assignment = RoleAssignment.objects.filter(
                pk=assignment_id if assignment_id.isdigit() else None,
                active=True,
                role__in=[
                    Role.PRIMARY_ADMIN,
                    Role.DEPUTY_ADMIN,
                    Role.PARENT_REPRESENTATIVE,
                    Role.DEPUTY_PARENT_REPRESENTATIVE,
                ],
            ).first()
            if assignment is None:
                messages.error(request, "Die Rollenzuweisung wurde nicht gefunden.")
                return redirect("role-management")
            try:
                set_user_role(
                    request.user,
                    assignment.user,
                    assignment.role,
                    school_class=assignment.school_class,
                    active=False,
                )
            except ValidationError as exc:
                messages.error(request, "; ".join(exc.messages))
                return redirect("role-management")
            messages.success(request, "Die Rolle wurde entzogen.")
            return redirect("role-management")
        if action == "assign":
            user_id = request.POST.get("user_id", "")
            class_id = request.POST.get("school_class_id", "")
            user = UserAccount.objects.filter(pk=user_id if user_id.isdigit() else None).first()
            role = request.POST.get("role")
            school_class = SchoolClass.objects.filter(
                pk=class_id if class_id.isdigit() else None
            ).first()
            if user is None:
                messages.error(request, "Das Benutzerkonto wurde nicht gefunden.")
                return redirect("role-management")
            try:
                set_user_role(request.user, user, role, school_class=school_class)
            except ValidationError as exc:
                messages.error(request, "; ".join(exc.messages))
                return redirect("role-management")
            messages.success(request, "Die Rolle wurde zugewiesen.")
            return redirect("role-management")
        messages.error(request, "Die Aktion ist unbekannt.")
        return redirect("role-management")
    role_form = UserRoleForm(request.POST if request.POST.get("form") == "role" else None)
    room_form = RepresentativeRoomForm(request.POST if request.POST.get("form") == "room" else None)
    if request.method == "POST":
        if request.POST.get("form") == "role" and role_form.is_valid():
            try:
                data = role_form.cleaned_data
                set_user_role(request.user, data["user"], data["role"],
                              school_class=data["school_class"], active=data["action"] == "grant")
            except ValidationError as exc:
                role_form.add_error(None, exc)
            else:
                messages.success(request, "Rollenzuweisung gespeichert.")
                return redirect("role-management")
        elif request.POST.get("form") == "room" and room_form.is_valid():
            room = room_form.cleaned_data["room"]
            with transaction.atomic():
                SchoolClass.objects.select_for_update().get(pk=room.school_class_id)
                if room_form.cleaned_data["enabled"]:
                    ChatRoom.objects.filter(school_class_id=room.school_class_id).update(parent_representative_chat=False)
                room.parent_representative_chat = room_form.cleaned_data["enabled"]
                room.save(update_fields=["parent_representative_chat"])
                AuditEvent.objects.create(
                    actor=request.user, action="chat.representative_room.changed",
                    target_type="chat_room", target_id=str(room.public_id),
                    metadata={"enabled": room.parent_representative_chat},
                )
            messages.success(request, "Elternvertreter-Chat gespeichert.")
            return redirect("role-management")
    context = _shared(request, "Rollenverwaltung", "management")
    context.update(role_form=role_form, room_form=room_form,
                   users=UserAccount.objects.order_by("email"),
                   assignments=RoleAssignment.objects.filter(active=True, role__in=[
                       Role.PRIMARY_ADMIN,
                       Role.DEPUTY_ADMIN,
                       Role.PARENT_REPRESENTATIVE,
                       Role.DEPUTY_PARENT_REPRESENTATIVE,
                   ]).select_related("user", "school_class"),
                   representative_rooms=ChatRoom.objects.filter(parent_representative_chat=True).select_related("school_class"))
    return render(request, "ui/role_management.html", context)
