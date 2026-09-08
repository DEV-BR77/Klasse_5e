from django.contrib import admin
from django.utils import timezone

from klasse5e.core.models import AuditEvent

from .models import (
    ChatPreference,
    ChatReport,
    ChatRetentionCategory,
    ChatRoom,
)


@admin.register(ChatRetentionCategory)
class ChatRetentionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "automatic_deletion_enabled", "retention_days", "intended_for_events", "is_active")
    list_editable = ("automatic_deletion_enabled", "retention_days", "is_active")
    list_filter = ("automatic_deletion_enabled", "intended_for_events", "is_active")


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("title", "school_class", "appearance", "is_open", "retention_category")
    list_filter = ("appearance", "is_open", "retention_category")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(direct_conversation__isnull=True)


@admin.register(ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = ("message", "reporter", "reason", "created_at", "resolved_at")
    list_filter = ("reason", "resolved_at")
    fields = (
        "reason",
        "reported_text",
        "reported_attachment",
        "reporter",
        "created_at",
        "resolved_at",
    )
    readonly_fields = (
        "reason",
        "reported_text",
        "reported_attachment",
        "reporter",
        "created_at",
    )
    actions = ("hide_reported_messages",)

    @admin.display(description="Gemeldeter Text")
    def reported_text(self, obj):
        return obj.message.body or "Kein Nachrichtentext"

    @admin.display(description="Gemeldeter Anhang")
    def reported_attachment(self, obj):
        return obj.message.attachment_name or "Kein Anhang"

    @admin.action(description="Gemeldete Nachrichten ausblenden und Meldungen abschließen")
    def hide_reported_messages(self, request, queryset):
        now = timezone.now()
        for report in queryset.select_related("message"):
            message = report.message
            message.hidden_at = now
            message.hidden_by = request.user
            message.save(update_fields=["hidden_at", "hidden_by"])
            report.resolved_at = now
            report.save(update_fields=["resolved_at"])
            AuditEvent.objects.create(
                actor=request.user,
                action="chat.message.hidden",
                target_type="chat_message",
                target_id=str(message.public_id),
            )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ChatPreference)
