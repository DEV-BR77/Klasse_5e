from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.db import models
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


@admin.register(RegistrationApplication)
class RegistrationApplicationAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "status", "school", "school_class", "created_at")
    list_filter = ("status", "school", "school_class")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("password_hash", "email_token_hash", "email_verified_at", "created_at", "updated_at")
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="Ausgewählte Anträge freigeben")
    def approve_selected(self, request, queryset):
        for item in queryset.select_related("school", "school_class"):
            if item.status != RegistrationApplication.Status.REVIEW_PENDING or not item.school_id or not item.school_class_id:
                continue
            item.status = RegistrationApplication.Status.APPROVED
            item.reviewed_by = request.user
            item.reviewed_at = timezone.now()
            item.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
            _, token = ActivationGrant.issue(item)
            link = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/aktivieren/{token}/"
            send_mail("Dein KlassID-Zugang wurde freigegeben", f"Aktiviere dein Konto einmalig innerhalb von 24 Stunden: {link}", settings.DEFAULT_FROM_EMAIL, [item.email])
            AuditEvent.objects.create(actor=request.user, action="registration.approved", target_type="registration", target_id=str(item.pk), metadata={"school_id": item.school_id, "class_id": item.school_class_id})

    @admin.action(description="Ausgewählte Anträge ablehnen")
    def reject_selected(self, request, queryset):
        for item in queryset.filter(status=RegistrationApplication.Status.REVIEW_PENDING):
            item.status = RegistrationApplication.Status.REJECTED
            item.reviewed_by = request.user
            item.reviewed_at = timezone.now()
            item.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])
            ActivationGrant.objects.filter(application=item).update(revoked_at=timezone.now())
            AuditEvent.objects.create(actor=request.user, action="registration.rejected", target_type="registration", target_id=str(item.pk))


admin.site.register(
    [FamilyAccessCode, FamilyRegistrationRequest, AccountDeletionRequest, DepartureRetentionCase]
)


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
    list_display = ("name", "postal_code", "city", "federal_state", "school_type", "legal_status", "provider", "slug", "source_name", "source_imported_at")
    list_filter = ("federal_state", "school_type", "legal_status", "provider", "location_valid")
    search_fields = ("name", "search_name", "postal_code", "city", "slug")
    list_per_page = 50
    readonly_fields = ("source_id", "source_name", "source_imported_at", "possible_duplicate_group", "created_at", "updated_at")

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if request.user.is_superuser or RoleAssignment.objects.filter(user=request.user, role="primary_admin", active=True).exists():
            return query
        school_ids = RoleAssignment.objects.filter(user=request.user, role="school_admin", active=True).values("school_id")
        return query.filter(id__in=school_ids)

    def has_add_permission(self, request):
        return request.user.is_superuser or RoleAssignment.objects.filter(user=request.user, role="primary_admin", active=True).exists()


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("display_name", "code", "school", "school_year", "status", "valid_from", "valid_until")
    list_filter = ("status", "school", "school_year")
    search_fields = ("display_name", "name", "code", "school__name", "school__slug")
    list_per_page = 50

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if request.user.is_superuser or RoleAssignment.objects.filter(user=request.user, role="primary_admin", active=True).exists():
            return query
        school_ids = RoleAssignment.objects.filter(user=request.user, role="school_admin", active=True).values("school_id")
        class_ids = RoleAssignment.objects.filter(user=request.user, role="class_admin", active=True).values("school_class_id")
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
