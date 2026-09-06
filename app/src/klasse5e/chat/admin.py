from django.contrib import admin

from .models import ChatPreference, ChatReport, ChatRetentionCategory, ChatRoom


@admin.register(ChatRetentionCategory)
class ChatRetentionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "automatic_deletion_enabled", "retention_days", "intended_for_events", "is_active")
    list_editable = ("automatic_deletion_enabled", "retention_days", "is_active")
    list_filter = ("automatic_deletion_enabled", "intended_for_events", "is_active")


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("title", "school_class", "appearance", "is_open", "retention_category")
    list_filter = ("appearance", "is_open", "retention_category")


admin.site.register([ChatReport, ChatPreference])
