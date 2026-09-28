from pathlib import Path


TEMPLATES = Path(__file__).parents[1] / "templates"


def _template(path):
    return (TEMPLATES / path).read_text(encoding="utf-8")


def test_data_entry_pages_use_the_shared_cancel_and_save_actions():
    expected_contracts = {
        "ui/school_detail.html": ("?tab=data", "?tab=classes"),
        "ui/chat_retention_settings.html": ("retention_cancel_url",),
        "ui/event_poll.html": ("poll_cancel_url",),
        "ui/family.html": ("?tab=overview",),
        "itslearning/storage.html": ("itslearning_cancel_url",),
    }

    for template_name, cancel_targets in expected_contracts.items():
        source = _template(template_name)
        assert 'ui/_form_actions.html' in source, template_name
        for cancel_target in cancel_targets:
            assert cancel_target in source, f"{template_name}: {cancel_target}"


def test_school_deactivation_is_visually_and_semantically_separated():
    source = _template("ui/school_detail.html")

    assert 'class="settings-panel danger-panel"' in source
    assert 'class="button button-danger"' in source
    assert 'data-confirm="Diese Schule wirklich aus dem Portal entfernen?"' in source


def test_shared_form_actions_keep_cancel_left_and_save_right():
    source = _template("ui/_form_actions.html")

    cancel_position = source.index("button-secondary")
    save_position = source.index("button-primary")
    assert cancel_position < save_position
