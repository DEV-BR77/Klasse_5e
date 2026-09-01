import pytest
from django.core.exceptions import ValidationError

from klasse5e.core.models import PortalModule, PortalModuleOverride
from klasse5e.core.module_flags import module_enabled, set_module_override


@pytest.mark.django_db
def test_module_inheritance_and_reset(school_class, admin_user):
    assert module_enabled("chat", school_class)
    school_override = set_module_override(
        key="chat", enabled=False, actor=admin_user, school=school_class.school
    )
    assert not module_enabled("chat", school_class)
    class_override = set_module_override(
        key="chat", enabled=True, actor=admin_user, school_class=school_class
    )
    assert module_enabled("chat", school_class)
    class_override.delete()
    assert not module_enabled("chat", school_class)
    school_override.delete()
    assert module_enabled("chat", school_class)


@pytest.mark.django_db
def test_module_dependency_is_enforced(school_class, admin_user):
    PortalModuleOverride.objects.create(
        module=PortalModule.objects.get(key="gallery"),
        school_class=school_class,
        enabled=False,
        updated_by=admin_user,
    )
    with pytest.raises(ValidationError):
        set_module_override(
            key="photo_memory", enabled=True, actor=admin_user, school_class=school_class
        )
