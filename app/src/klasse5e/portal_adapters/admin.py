from django.contrib import admin

from .models import (
    ChildModuleConnection,
    PortalAdapter,
    PortalAdapterDefinition,
    PortalAdapterDefinitionModule,
    PortalAdapterModule,
)


class PortalAdapterDefinitionModuleInline(admin.TabularInline):
    model = PortalAdapterDefinitionModule
    extra = 0
    fields = ("key", "label", "access_model", "is_published")


@admin.register(PortalAdapterDefinition)
class PortalAdapterDefinitionAdmin(admin.ModelAdmin):
    list_display = ("label", "provider", "integration_type", "is_published", "is_technically_reviewed")
    list_filter = ("integration_type", "is_published", "is_technically_reviewed")
    search_fields = ("label", "provider", "hint")
    inlines = (PortalAdapterDefinitionModuleInline,)


@admin.register(PortalAdapterDefinitionModule)
class PortalAdapterDefinitionModuleAdmin(admin.ModelAdmin):
    list_display = ("label", "definition", "access_model", "is_published")
    list_filter = ("access_model", "is_published", "definition")
    search_fields = ("label", "key", "definition__label")


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
