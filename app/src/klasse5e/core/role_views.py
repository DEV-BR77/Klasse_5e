from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from klasse5e.chat.models import ChatRoom

from .models import AuditEvent, Role, RoleAssignment, SchoolClass, UserAccount
from .role_management import require_role_manager, set_user_role
from .ui_views import _shared


class UserRoleForm(forms.Form):
    user = forms.ModelChoiceField(label="Benutzerkonto", queryset=UserAccount.objects.all())
    role = forms.ChoiceField(label="Rolle", choices=[
        (Role.PRIMARY_ADMIN, "Portal-Admin"),
        (Role.PARENT_REPRESENTATIVE, "Elternvertretung"),
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
            assignment = RoleAssignment.objects.filter(
                pk=request.POST.get("assignment_id"),
                active=True,
                role__in=[
                    Role.PRIMARY_ADMIN,
                    Role.DEPUTY_ADMIN,
                    Role.PARENT_REPRESENTATIVE,
                ],
            ).first()
            if assignment is None:
                raise ValidationError("Die Rollenzuweisung wurde nicht gefunden.")
            set_user_role(
                request.user,
                assignment.user,
                assignment.role,
                school_class=assignment.school_class,
                active=False,
            )
            messages.success(request, "Die Rolle wurde entzogen.")
            return redirect("role-management")
        if action == "assign":
            user = UserAccount.objects.filter(pk=request.POST.get("user_id")).first()
            role = request.POST.get("role")
            school_class = SchoolClass.objects.filter(
                pk=request.POST.get("school_class_id")
            ).first()
            if user is None:
                raise ValidationError("Das Benutzerkonto wurde nicht gefunden.")
            set_user_role(request.user, user, role, school_class=school_class)
            messages.success(request, "Die Rolle wurde zugewiesen.")
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
                       Role.PRIMARY_ADMIN, Role.PARENT_REPRESENTATIVE,
                   ]).select_related("user", "school_class"),
                   representative_rooms=ChatRoom.objects.filter(parent_representative_chat=True).select_related("school_class"))
    return render(request, "ui/role_management.html", context)
