from django.contrib import admin

from .models import SyncRun, SyncSchedule, WebUntisConnection, WebUntisFeaturePreference


@admin.register(SyncSchedule)
class SyncScheduleAdmin(admin.ModelAdmin):
    list_display = ("enabled", "timezone_name", "times", "max_runs_per_day", "min_interval_minutes")
    fields = (
        "enabled",
        "timezone_name",
        "times",
        "weekdays_only",
        "weekends",
        "holidays",
        "max_runs_per_day",
        "min_interval_minutes",
    )


@admin.register(WebUntisConnection)
class WebUntisConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "student", "status", "last_checked_at", "last_successful_sync_at")
    readonly_fields = (
        "username_encrypted",
        "password_encrypted",
        "last_checked_at",
        "last_successful_sync_at",
    )


@admin.register(SyncRun)
class SyncRunAdmin(admin.ModelAdmin):
    list_display = (
        "connection",
        "trigger",
        "status",
        "started_at",
        "finished_at",
        "change_count",
        "error_code",
    )
    readonly_fields = [field.name for field in SyncRun._meta.fields]


admin.site.register(WebUntisFeaturePreference)
