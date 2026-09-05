import base64
import csv
import io
import json
import tempfile

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.db import models
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from .models import (
    AccountDeletionRequest,
    ActivationGrant,
    AuditEvent,
    BrandingAsset,
    ClassDomain,
    ClassMembership,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    DepartureRetentionCase,
    FamilyAccessCode,
    FamilyChildAccount,
    FamilyRegistrationRequest,
    GuardianChildRelationship,
    Household,
    Invitation,
    LogoRequest,
    Person,
    PilotReport,
    PortalConfigurationKey,
    PortalConfigurationValue,
    PortalModule,
    PortalModuleOverride,
    PushSubscription,
    RegistrationApplication,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
)
from .school_import import EXPECTED_FIELDS, detect_encoding, import_schools


@admin.register(RegistrationApplication)
class RegistrationApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "status",
        "school",
        "school_class",
        "created_at",
    )
    list_filter = ("status", "school", "school_class")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = (
        "password_hash",
        "email_token_hash",
        "email_verified_at",
        "created_at",
        "updated_at",
    )
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="Ausgewählte Anträge freigeben")
    def approve_selected(self, request, queryset):
        for item in queryset.select_related("school", "school_class"):
            if (
                item.status != RegistrationApplication.Status.REVIEW_PENDING
                or not item.school_id
                or not item.school_class_id
            ):
                continue
            item.status = RegistrationApplication.Status.APPROVED
            item.reviewed_by = request.user
            item.reviewed_at = timezone.now()
            item.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
            _, token = ActivationGrant.issue(item)
            link = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/aktivieren/{token}/"
            send_mail(
                "Dein KlassID-Zugang wurde freigegeben",
                f"Aktiviere dein Konto einmalig innerhalb von 24 Stunden: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [item.email],
            )
            AuditEvent.objects.create(
                actor=request.user,
                action="registration.approved",
                target_type="registration",
                target_id=str(item.pk),
                metadata={"school_id": item.school_id, "class_id": item.school_class_id},
            )

    @admin.action(description="Ausgewählte Anträge ablehnen")
    def reject_selected(self, request, queryset):
        for item in queryset.filter(status=RegistrationApplication.Status.REVIEW_PENDING):
            item.status = RegistrationApplication.Status.REJECTED
            item.reviewed_by = request.user
            item.reviewed_at = timezone.now()
            item.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
            ActivationGrant.objects.filter(application=item).update(revoked_at=timezone.now())
            AuditEvent.objects.create(
                actor=request.user,
                action="registration.rejected",
                target_type="registration",
                target_id=str(item.pk),
            )


@admin.register(FamilyAccessCode)
class FamilyAccessCodeAdmin(admin.ModelAdmin):
    list_display = (
        "batch_id",
        "serial_number",
        "school_class",
        "intended_family_name",
        "existing_guardian",
        "use_count",
        "max_uses",
        "submitted_at",
        "completed_at",
        "expires_at",
    )
    list_filter = ("school_class", "existing_guardian_relationship_type")
    search_fields = (
        "intended_family_name",
        "existing_guardian__email",
        "existing_guardian__person__first_name",
        "existing_guardian__person__last_name",
    )
    autocomplete_fields = ("existing_guardian",)
    readonly_fields = ("token_hash", "batch_id", "serial_number", "created_at")


admin.site.register([FamilyRegistrationRequest, AccountDeletionRequest, DepartureRetentionCase])


@admin.register(FamilyChildAccount)
class FamilyChildAccountAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "family_request", "activated_user")
    search_fields = ("first_name", "last_name", "email")
    readonly_fields = ("password_hash", "created_at", "activated_user")


@admin.register(UserAccount)
class AccountAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_active", "is_staff", "locked_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Klasse 5e", {"fields": ("email_verified_at", "locked_at", "selected_theme")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    change_list_template = "admin/core/school/change_list.html"
    list_display = (
        "name",
        "postal_code",
        "city",
        "federal_state",
        "school_type",
        "legal_status",
        "provider",
        "slug",
        "source_name",
        "source_imported_at",
    )
    list_filter = ("federal_state", "school_type", "legal_status", "provider", "location_valid")
    search_fields = ("name", "search_name", "postal_code", "city", "slug")
    list_per_page = 50
    readonly_fields = (
        "source_id",
        "source_name",
        "source_imported_at",
        "possible_duplicate_group",
        "created_at",
        "updated_at",
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv_view),
                name="core_school_import_csv",
            )
        ]
        return custom + urls

    def has_import_permission(self, request):
        return (
            request.user.is_superuser
            or RoleAssignment.objects.filter(
                user=request.user, role="primary_admin", active=True
            ).exists()
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_import_permission"] = self.has_import_permission(request)
        return super().changelist_view(request, extra_context=extra_context)

    def import_csv_view(self, request):
        if not self.has_import_permission(request):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Schulen aus CSV importieren",
            "changelist_url": reverse("admin:core_school_changelist"),
            "rows": [],
            "errors": [],
        }
        if request.method == "POST":
            upload = request.FILES.get("csv_file")
            if upload is not None:
                if upload.size > 5 * 1024 * 1024:
                    context["errors"] = ["Die CSV-Datei darf höchstens 5 MB groß sein."]
                else:
                    try:
                        data = upload.read()
                        encoding = detect_encoding(data)
                        reader = csv.DictReader(io.StringIO(data.decode(encoding), newline=""))
                        if not reader.fieldnames or not EXPECTED_FIELDS.issubset(reader.fieldnames):
                            raise ValueError("Die CSV-Spalten entsprechen nicht dem erwarteten Schulformat.")
                        rows = []
                        for row in reader:
                            cleaned = {field: str(row.get(field) or "") for field in EXPECTED_FIELDS}
                            if cleaned["id"] and cleaned["name"]:
                                cleaned["encoded"] = base64.urlsafe_b64encode(
                                    json.dumps(cleaned, ensure_ascii=False).encode("utf-8")
                                ).decode("ascii")
                                rows.append(cleaned)
                        if len(rows) > 1000:
                            raise ValueError(
                                "Bitte höchstens 1.000 Datensätze auf einmal auswählen. "
                                "Nutze dafür vorher einen regionalen CSV-Auszug."
                            )
                        context["rows"] = rows
                        context["uploaded_name"] = upload.name
                    except (UnicodeError, ValueError, csv.Error) as exc:
                        context["errors"] = [str(exc)]
            else:
                encoded_rows = request.POST.getlist("selected_row")
                records = []
                try:
                    for encoded in encoded_rows:
                        decoded = base64.urlsafe_b64decode(encoded.encode()).decode("utf-8")
                        record = json.loads(decoded)
                        records.append({field: record.get(field, "") for field in EXPECTED_FIELDS})
                    if not records:
                        raise ValueError("Bitte mindestens eine Schule auswählen.")
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", newline="") as handle:
                        writer = csv.DictWriter(handle, fieldnames=sorted(EXPECTED_FIELDS))
                        writer.writeheader()
                        writer.writerows(records)
                        handle.flush()
                        _, stats = import_schools(Path(handle.name), source_name="admin-upload.csv")
                    messages.success(
                        request,
                        f"{stats.created + stats.updated} Schule(n) importiert bzw. aktualisiert.",
                    )
                    return HttpResponseRedirect(context["changelist_url"])
                except (ValueError, UnicodeError, json.JSONDecodeError, csv.Error) as exc:
                    context["errors"] = [str(exc)]

        return TemplateResponse(request, "admin/core/school/import_csv.html", context)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if (
            request.user.is_superuser
            or RoleAssignment.objects.filter(
                user=request.user, role="primary_admin", active=True
            ).exists()
        ):
            return query
        school_ids = RoleAssignment.objects.filter(
            user=request.user, role="school_admin", active=True
        ).values("school_id")
        return query.filter(id__in=school_ids)

    def has_add_permission(self, request):
        return (
            request.user.is_superuser
            or RoleAssignment.objects.filter(
                user=request.user, role="primary_admin", active=True
            ).exists()
        )


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "code",
        "school",
        "school_year",
        "status",
        "valid_from",
        "valid_until",
    )
    list_filter = ("status", "school", "school_year")
    search_fields = ("display_name", "name", "code", "school__name", "school__slug")
    list_per_page = 50

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if (
            request.user.is_superuser
            or RoleAssignment.objects.filter(
                user=request.user, role="primary_admin", active=True
            ).exists()
        ):
            return query
        school_ids = RoleAssignment.objects.filter(
            user=request.user, role="school_admin", active=True
        ).values("school_id")
        class_ids = RoleAssignment.objects.filter(
            user=request.user, role="class_admin", active=True
        ).values("school_class_id")
        return query.filter(models.Q(school_id__in=school_ids) | models.Q(id__in=class_ids))


for model in [
    Person,
    BrandingAsset,
    ClassDomain,
    Household,
    SchoolYear,
    StudentProfile,
    ClassMembership,
    RoleAssignment,
    GuardianChildRelationship,
    Invitation,
    ActivationGrant,
    ConsentType,
    ConsentTextVersion,
    ConsentDecision,
    AuditEvent,
    PushSubscription,
    LogoRequest,
    PortalConfigurationKey,
    PortalConfigurationValue,
    PortalModule,
    PortalModuleOverride,
    PilotReport,
]:
    admin.site.register(model)
