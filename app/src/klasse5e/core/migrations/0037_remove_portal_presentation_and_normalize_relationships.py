from django.db import migrations, models


def remove_retired_data(apps, schema_editor):
    """Remove the retired portal presentation and normalize legacy family roles."""

    GuardianChildRelationship = apps.get_model("core", "GuardianChildRelationship")
    FamilyAccessCode = apps.get_model("core", "FamilyAccessCode")
    PushPreference = apps.get_model("core", "PushPreference")
    UserNotification = apps.get_model("core", "UserNotification")
    Event = apps.get_model("events", "Event")

    GuardianChildRelationship.objects.filter(
        relationship_type__in=("mother", "father")
    ).update(relationship_type="guardian")
    FamilyAccessCode.objects.filter(
        existing_guardian_relationship_type__in=("mother", "father")
    ).update(existing_guardian_relationship_type="guardian")

    retired_event_ids = []
    for event_id, title in Event.objects.values_list("pk", "title").iterator():
        normalized = (title or "").casefold()
        is_portal_introduction = (
            ("portal" in normalized or "klassid" in normalized)
            and ("vorstell" in normalized or "kennenlern" in normalized)
        )
        if is_portal_introduction:
            retired_event_ids.append(event_id)

    UserNotification.objects.filter(revision="portal-presentation-v1").delete()
    if retired_event_ids:
        UserNotification.objects.filter(
            object_type="event", object_id__in=[str(event_id) for event_id in retired_event_ids]
        ).delete()
        Event.objects.filter(pk__in=retired_event_ids).delete()
    PushPreference.objects.filter(key__in=("push_carpool", "inapp_carpool")).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0036_useraccount_leak_status"),
        ("events", "0008_event_participation"),
    ]

    operations = [
        migrations.RunPython(remove_retired_data, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="familyaccesscode",
            name="existing_guardian_relationship_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("guardian", "Erziehungsberechtigte Person"),
                    ("foster", "Pflegeelternteil"),
                    ("step", "Stiefelternteil"),
                    ("other", "Sonstige autorisierte Bezugsperson"),
                ],
                default="",
                max_length=24,
            ),
        ),
        migrations.AlterField(
            model_name="guardianchildrelationship",
            name="relationship_type",
            field=models.CharField(
                choices=[
                    ("guardian", "Erziehungsberechtigte Person"),
                    ("foster", "Pflegeelternteil"),
                    ("step", "Stiefelternteil"),
                    ("other", "Sonstige autorisierte Bezugsperson"),
                ],
                max_length=24,
            ),
        ),
    ]
