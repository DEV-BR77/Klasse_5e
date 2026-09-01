from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AuditEvent,
    BrandingAsset,
    ClassDomain,
    ClassMembership,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    Household,
    Invitation,
    LogoRequest,
    Person,
    PushSubscription,
    PortalConfigurationKey,
    PortalConfigurationValue,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
)


@admin.register(UserAccount)
class AccountAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_active", "is_staff", "locked_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Klasse 5e", {"fields": ("email_verified_at", "locked_at")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)


for model in [
    Person,
    BrandingAsset,
    ClassDomain,
    Household,
    School,
    SchoolYear,
    SchoolClass,
    StudentProfile,
    ClassMembership,
    RoleAssignment,
    GuardianChildRelationship,
    Invitation,
    ConsentType,
    ConsentTextVersion,
    ConsentDecision,
    AuditEvent,
    PushSubscription,
    LogoRequest,
    PortalConfigurationKey,
    PortalConfigurationValue,
]:
    admin.site.register(model)
