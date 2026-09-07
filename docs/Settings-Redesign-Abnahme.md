# Einstellungen-Redesign: Prüfung vom 07.09.2026

Die Einstellungsseiten verwenden gemeinsame Navigation und Formularstile.
Die Starthilfe lässt sich verlassen, ohne Einwilligungen zu erteilen; der
bisherige Einführungsschritt bleibt über einen Fortsetzen-Link erreichbar.
Die Avatar-Übernahme aktiviert die Avatar-Auswahl im jeweiligen Profilformular.

## Prüfstand

Das Docker-Image `klasse-5e-app:redesign-20260907` wurde aus einem Export des
Git-Index gebaut. Lokale Dashboard-Hilfsänderungen, Entwicklungseinstellungen,
Theme-Beispieltemplate, Laufzeitmedien und lose Dokumente wurden weder in den
Build-Stand noch in diesen Commit übernommen. Benutzerdateien bleiben erhalten.
Es erfolgte kein Produktivdeployment.

- Vollständige Django-Suite im bereinigten Export: **203 bestanden, 9 Fehler**.
- Alle neun verbleibenden Fehler wurden in denselben Testmodulen des
  unveränderten Vorgängercommits reproduziert (58 bestanden, 9 Fehler).
- Die veraltete Onboarding-Testannahme wurde auf die neue Übersicht und den
  Link zum gespeicherten Einführungsschritt angepasst.
- Ruff für geänderte Python-Anwendungsdateien/Redesign-Tests, JavaScript-
  Syntaxprüfung und `git diff --cached --check` bestanden.
- Browser-Smoke-Test im Image, ohne Netzwerk und ohne produktive Volumes:
  Login, Starthilfe, Profil, Familie, Benachrichtigungen, MFA und Avatar-Übernahme
  bei 390 und 1280 Pixeln; kein horizontaler Überlauf und keine JS-Ausnahmen.
  Login mobil und Profil am Desktop zusätzlich anhand der Screenshots geprüft.
- Synthetische Daten und Screenshots entstehen ausschließlich im Testcontainer.

Die Gesamtsuite ist damit **nicht vollständig grün**. Bekannte bestehende Fehler:

| Modul | Test |
| --- | --- |
| test_admin_workflows | test_portal_admin_menu_exposes_school_class_and_family_workflows |
| test_family_context | test_dashboard_combines_important_items_for_all_children |
| test_phase2 | test_dashboard_renders_when_personal_lessons_are_empty |
| test_portal_adapter_management | test_guardian_can_only_activate_school_approved_modules_for_own_child |
| test_portal_management | test_admin_can_delete_a_chat_room_and_room_uses_selected_appearance |
| test_school_consolidation | test_consolidates_legacy_thg_school_without_losing_roles |
| test_spoonacular | test_organizer_can_search_food_without_sending_event_data |
| test_spoonacular | test_food_provider_failure_is_a_safe_ui_state |
| test_phase5 | test_service_worker_does_not_cache_gallery_media |

Der letzte Test erwartet einen Pfad relativ zur Repository-Wurzel und scheitert
beim hier verwendeten Arbeitsverzeichnis `app`. Die anderen Fehler betreffen
bestehende UI-/Fixture-/Funktionsannahmen außerhalb dieses Redesign-Pakets.

## Browser-Prüfung wiederholen

Aus der Repository-Wurzel mit einem frischen Container ausführen:

```powershell
docker run --rm --network none -e PYTHONPATH=/srv/app/src:/srv/app --mount "type=bind,source=$PWD/tools/Test-SettingsRedesign.py,target=/tmp/smoke.py,readonly" --entrypoint python klasse-5e-app:redesign-20260907 /tmp/smoke.py
```

Zum Aufbewahren der Screenshots `--rm` durch einen eindeutigen `--name` ersetzen
und danach `/tmp/redesign-qa` mit `docker cp` aus dem Testcontainer kopieren.
