from django.db import migrations


def configure_schedule(apps, schema_editor):
    schedule_model = apps.get_model("webuntis", "SyncSchedule")
    schedule = schedule_model.objects.order_by("pk").first()
    if schedule is None:
        schedule = schedule_model()
    schedule.enabled = True
    schedule.timezone_name = "Europe/Berlin"
    schedule.times = ["06:00", "12:00", "18:00"]
    schedule.max_runs_per_day = 3
    schedule.min_interval_minutes = 15
    schedule.save()


class Migration(migrations.Migration):
    dependencies = [
        ("webuntis", "0004_alter_syncschedule_max_runs_per_day"),
    ]

    operations = [
        migrations.RunPython(configure_schedule, migrations.RunPython.noop),
    ]
