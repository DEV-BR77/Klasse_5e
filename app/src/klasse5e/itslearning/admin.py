from django.contrib import admin

from .models import (
    ItslearningCalendarItem,
    ItslearningConnection,
    ItslearningCourse,
    ItslearningUpdate,
    WebDavSpace,
)
from .webdav import used_bytes


@admin.register(ItslearningConnection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("student", "owner", "active", "last_sync_status", "last_sync_at")
    readonly_fields = ("username_ciphertext", "password_ciphertext", "calendar_url_ciphertext")


@admin.register(WebDavSpace)
class WebDavSpaceAdmin(admin.ModelAdmin):
    list_display = ("student", "username", "usage", "quota_bytes", "active")
    readonly_fields = ("password_hash", "public_id")

    @admin.display(description="Belegt")
    def usage(self, obj):
        return used_bytes(obj)


admin.site.register(ItslearningCourse)
admin.site.register(ItslearningUpdate)
admin.site.register(ItslearningCalendarItem)
