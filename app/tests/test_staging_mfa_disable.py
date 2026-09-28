from django.test import override_settings

from klasse5e.core.adapters import ClosedAccountAdapter


def test_staging_mfa_disable_removes_mfa_login_stages():
    with override_settings(MFA_LOGIN_DISABLED=True):
        stages = ClosedAccountAdapter().get_login_stages()

    assert not any(stage.startswith("allauth.mfa.") for stage in stages)


def test_production_configuration_keeps_mfa_login_stage():
    with override_settings(MFA_LOGIN_DISABLED=False):
        stages = ClosedAccountAdapter().get_login_stages()

    assert "allauth.mfa.stages.AuthenticateStage" in stages
