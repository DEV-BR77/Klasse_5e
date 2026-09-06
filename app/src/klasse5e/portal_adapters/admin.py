from django.contrib import admin

from .models import ChildModuleConnection, PortalAdapter, PortalAdapterModule


class PortalAdapterModuleInline(admin.TabularInline):
    model = PortalAdapterModule
    extra = 0
    fields = ("label", "key", "is_enabled", "requires_child_credentials", "status")


@admin.register(PortalAdapter)
class PortalAdapterAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "school", "is_enabled", "last_check_status", "updated_at")
    list_filter = ("provider", "is_enabled", "school")
    search_fields = ("name", "school__name", "project_identifier", "institution_identifier")
    inlines = (PortalAdapterModuleInline,)


@admin.register(PortalAdapterModule)
class PortalAdapterModuleAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "adapter",
        "is_enabled",
        "requires_child_credentials",
        "status",
        "last_synced_at",
    )
    list_filter = ("is_enabled", "status", "adapter__provider")
    search_fields = ("label", "adapter__name", "adapter__school__name")
    filter_horizontal = ("available_to_classes",)


@admin.register(ChildModuleConnection)
class ChildModuleConnectionAdmin(admin.ModelAdmin):
    list_display = ("student", "module", "is_enabled", "connection_state", "configured_at")
    list_filter = ("is_enabled", "connection_state", "module__adapter__school")
    search_fields = ("student__first_name", "student__last_name", "module__label")
