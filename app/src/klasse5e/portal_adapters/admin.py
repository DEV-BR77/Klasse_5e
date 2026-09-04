from django.contrib import admin

from .models import PortalAdapter, PortalAdapterModule


class PortalAdapterModuleInline(admin.TabularInline):
    model = PortalAdapterModule
    extra = 0


@admin.register(PortalAdapter)
class PortalAdapterAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "school", "is_enabled", "last_check_status", "updated_at")
    list_filter = ("provider", "is_enabled", "school")
    search_fields = ("name", "school__name", "project_identifier", "institution_identifier")
    inlines = (PortalAdapterModuleInline,)


@admin.register(PortalAdapterModule)
class PortalAdapterModuleAdmin(admin.ModelAdmin):
    list_display = ("label", "adapter", "is_enabled", "status", "last_synced_at")
    list_filter = ("is_enabled", "status", "adapter__provider")
    search_fields = ("label", "adapter__name", "adapter__school__name")
