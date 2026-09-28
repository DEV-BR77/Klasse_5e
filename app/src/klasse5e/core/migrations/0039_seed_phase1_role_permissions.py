from django.db import migrations


def seed_phase1_permissions(apps, schema_editor):
    PortalModule = apps.get_model("core", "PortalModule")
    RoleModulePermission = apps.get_model("core", "RoleModulePermission")

    actions = ("view", "read", "create", "edit", "moderate", "publish")
    phase1_roles = {
        "primary_admin",
        "content_manager",
        "editor",
        "moderator",
    }
    module_keys = set(PortalModule.objects.values_list("key", flat=True))

    allowed = {
        "content_manager": {
            "events": {"view", "read", "create", "edit", "publish"},
            "chat": {"view", "read", "create", "edit", "publish"},
        },
        "editor": {
            "events": {"view", "read", "edit", "publish"},
            "calendar": {"view", "read", "edit", "publish"},
            "chat": {"view", "read", "edit", "publish"},
        },
        "moderator": {
            "gallery": {"view", "read", "moderate"},
            "photo_memory": {"view", "read", "moderate"},
            "chat": {"view", "read", "moderate"},
        },
    }

    for role in phase1_roles:
        for module_key in module_keys:
            if role == "primary_admin":
                role_actions = set(actions)
                scope = "platform"
            else:
                role_actions = allowed.get(role, {}).get(module_key, set())
                scope = "platform"
            module_id = PortalModule.objects.get(key=module_key).pk
            for action in role_actions:
                RoleModulePermission.objects.update_or_create(
                    role=role,
                    module_id=module_id,
                    action=action,
                    defaults={"scope": scope, "active": True},
                )


class Migration(migrations.Migration):
    dependencies = [("core", "0038_rolemodulepermission")]
    operations = [migrations.RunPython(seed_phase1_permissions, migrations.RunPython.noop)]
