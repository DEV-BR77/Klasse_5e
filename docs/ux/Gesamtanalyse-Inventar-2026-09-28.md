# Routen- und Templateinventar – 28.09.2026

Ergänzung zur [Gesamtanalyse](Gesamtanalyse-2026-09-28.md).
Lesende statische Inventur; kein Nachweis erfolgreicher HTTP-Aufrufe oder
abgeschlossener Bedienabläufe. Keine echten IDs, Tokens oder Personendaten.

## Routen

Quelle: `app/src/klasse5e/urls.py`.
SHA-256: `94C8B7DED333015479DF43C5BEE8F51F7A36B590CE9FFD981AFEE88C281B4C1E`.
177 Definitionen, 174 unterschiedliche Pfade.
Drei Kalenderpfade sind doppelt definiert. Bibliotheksunterrouten aus
Accounts, Django-Admin und Wagtail sind über Includes angebunden und müssen
im jeweiligen Fachpaket ergänzt werden.

| Pfad | URL-Name |
|---|---|
| `/verwaltung/modellvisualisierung/` | `model-visualizer` |
| `/verwaltung/modellvisualisierung/api/graph/` | `model-visualizer-api` |
| `/verwaltung/modellvisualisierung/export/` | `model-visualizer-export` |
| `/abwesenheiten/` | `absence-portal` |
| `/registrieren/` | `register` |
| `/einladung/` | `invitation-entry` |
| `/familie/start/<str:token>/` | `family-register` |
| `/registrieren/email/<str:token>/` | `registration-email-verify` |
| `/aktivieren/<str:token>/` | `registration-activate` |
| `/datenschutz/` | `privacy-information` |
| `/projekt/` | `project` |
| `/demo/` | `demo` |
| `/scan/<path:token>/` | `temporary-scan-access` |
| `/onboarding/` | `onboarding-resume` |
| `/onboarding/pausiert/` | `onboarding-paused` |
| `/onboarding/schritt/<int:step>/` | `onboarding-step` |
| `/einwilligungen/<slug:key>/<int:subject_id>/widerrufen/` | `consent-withdraw` |
| `/tutorial/` | `tutorial-resume` |
| `/tutorial/schritt/<int:step>/` | `tutorial-step` |
| `/` | `dashboard` |
| `/familie/ansicht/` | `family-overview-select` |
| `/familie/ansicht/<int:student_id>/` | `family-child-select` |
| `/hausaufgaben/<int:homework_id>/erledigt/` | `homework-progress` |
| `/einstellungen/profil/` | `personal-profile` |
| `/einstellungen/design/` | `theme-settings` |
| `/einstellungen/design/vorschau/<int:theme_id>/<slug:page>/` | `portal-theme-preview` |
| `/einstellungen/konto-loeschen/` | `delete-account` |
| `/profile/<int:person_id>/foto/` | `profile-photo` |
| `/familie/foto/<int:photo_id>/` | `family-photo` |
| `/benachrichtigungen/` | `notification-list` |
| `/benachrichtigungen/<int:notification_id>/lesen/` | `notification-read` |
| `/benachrichtigungen/alle-lesen/` | `notifications-read-all` |
| `/kalender/` | `ui-calendar` |
| `/kontakte/` | `ui-contacts` |
| `/schueler/` | `ui-students` |
| `/chat/` | `ui-chat` |
| `/chat/direkt/<int:person_id>/starten/` | `direct-conversation-start` |
| `/chat/<uuid:room_id>/ansicht/` | `ui-chat-room` |
| `/chat/nachricht/<uuid:message_id>/anhang/` | `ui-chat-attachment` |
| `/verwaltung/rollen/` | `role-management` |
| `/verwaltung/rollen/berechtigungen/` | `role-permissions` |
| `/verwaltung/rollen/personen/` | `role-people` |
| `/verwaltung/` | `portal-management` |
| `/verwaltung/pilotmeldungen/` | `pilot-reports-management` |
| `/verwaltung/pilotmeldungen/<int:report_id>/screenshot/` | `pilot-report-screenshot` |
| `/verwaltung/betrieb/` | `monitoring-dashboard` |
| `/verwaltung/betrieb/konfiguration/` | `monitoring-configuration` |
| `/intern/monitoring/messwerte/` | `monitoring-ingest` |
| `/intern/monitoring/zustaende/` | `monitoring-component-state` |
| `/verwaltung/automatische-abmeldung/` | `session-timeout-settings` |
| `/verwaltung/schulen/` | `school-management` |
| `/verwaltung/schulen/<int:school_id>/` | `school-detail` |
| `/verwaltung/klassen/<int:class_id>/` | `school-class-detail` |
| `/verwaltung/schulen/import/` | `school-catalog-import` |
| `/verwaltung/schulen/stammdaten-export.csv` | `school-setup-export` |
| `/verwaltung/schulen/stammdaten-import/` | `school-setup-import` |
| `/verwaltung/adapter/` | `portal-adapter-management` |
| `/verwaltung/adapter/<int:adapter_id>/` | `portal-adapter-detail` |
| `/verwaltung/adapter-definition/<int:definition_id>/` | `portal-adapter-definition-detail` |
| `/verwaltung/anmeldung/` | `registration-invitation` |
| `/verwaltung/familien-einladungen/` | `family-invitations` |
| `/verwaltung/themes/` | `theme-management` |
| `/verwaltung/designsystem/` | `design-system` |
| `/verwaltung/menue/` | `menu-management` |
| `/verwaltung/terminumfrage/` | `presentation-poll-settings` |
| `/verwaltung/chat-aufbewahrung/` | `chat-retention-settings` |
| `/verwaltung/chat-elemente/` | `chat-assets-settings` |
| `/verwaltung/anmeldung/qr.svg` | `registration-invitation-qr` |
| `/pilot/melden/` | `pilot-report` |
| `/mehr/` | `ui-more` |
| `/mehr/lernportale/` | `ui-learning-portals` |
| `/mehr/dokumente/` | `ui-documents` |
| `/mehr/aktuelles/` | `ui-posts` |
| `/mehr/aktuelles/<int:post_id>/` | `ui-post-detail` |
| `/mehr/veranstaltungen/` | `ui-events` |
| `/mehr/veranstaltungen/umfrage/neu/` | `ui-create-event-poll` |
| `/mehr/veranstaltungen/umfrage/<int:poll_id>/` | `ui-event-poll` |
| `/mehr/veranstaltungen/umfrage/<int:poll_id>/festlegen/` | `ui-finalize-event-poll` |
| `/mehr/mobilitaet/` | `mobility-overview` |
| `/mehr/mobilitaet/<uuid:public_id>/` | `mobility-detail` |
| `/mehr/mobilitaet/<uuid:public_id>/treffpunkt/` | `mobility-meeting-point` |
| `/mehr/mobilitaet/<uuid:public_id>/reagieren/` | `mobility-react` |
| `/mehr/mobilitaet/<uuid:public_id>/status/` | `mobility-status` |
| `/mehr/mobilitaet/<uuid:public_id>/melden/` | `mobility-report` |
| `/mehr/mobilitaet/<uuid:public_id>/moderieren/` | `mobility-moderate` |
| `/mobility/reactions/<int:reaction_id>/decision/` | `mobility-reaction-decision` |
| `/mobility/reactions/<int:reaction_id>/pickup/` | `mobility-pickup-disclose` |
| `/mobility/pickups/<int:disclosure_id>/revoke/` | `mobility-pickup-revoke` |
| `/mehr/veranstaltungen/<int:event_id>/` | `ui-event` |
| `/mehr/veranstaltungen/<int:event_id>/bearbeiten/` | `ui-edit-event` |
| `/mehr/veranstaltungen/<int:event_id>/loeschen/` | `ui-delete-event` |
| `/mehr/veranstaltungen/<int:event_id>/teilnahme/` | `ui-event-attendance` |
| `/mehr/veranstaltungen/<int:event_id>/mitbringliste/` | `ui-add-contribution-list` |
| `/mehr/mitbringen/<int:item_id>/reservieren/` | `ui-reserve` |
| `/mehr/veranstaltungen/<int:event_id>/freier-beitrag/` | `ui-free-contribution` |
| `/mehr/reservierungen/<int:reservation_id>/zuruecknehmen/` | `ui-cancel-reservation` |
| `/mehr/lehrkraefte/` | `ui-teachers` |
| `/mehr/fotos/` | `ui-galleries` |
| `/mehr/speiseplan/` | `meal-plans` |
| `/mehr/familie/` | `ui-family` |
| `/mehr/einwilligungen/` | `ui-consents` |
| `/mehr/benachrichtigungen/` | `ui-notifications` |
| `/mehr/benachrichtigungen/einstellung/` | `ui-notification-preference` |
| `/mehr/webuntis/` | `webuntis-connection` |
| `/mehr/webuntis/synchronisierung/` | `webuntis-toggle-sync` |
| `/mehr/webuntis/testen/` | `webuntis-test` |
| `/mehr/webuntis/entfernen/` | `webuntis-remove` |
| `/mehr/webuntis/funktionen/` | `webuntis-features` |
| `/mehr/webuntis/aktuell-pruefen/` | `webuntis-sync` |
| `/kalender/verbinden/` | `webuntis-calendar-settings` |
| `/mehr/webuntis/<int:connection_id>/kalender.ics` | `webuntis-calendar-download` |
| `/mehr/webuntis/<int:connection_id>/kalender-abo/` | `webuntis-calendar-issue` |
| `/webuntis/kalender/<str:token>/` | `webuntis-calendar-feed` |
| `/itslearning/` | `itslearning-portal` |
| `/itslearning/zugang/` | `itslearning-save` |
| `/itslearning/<int:student_id>/kurse/` | `itslearning-course` |
| `/itslearning/<int:student_id>/synchronisieren/` | `itslearning-sync` |
| `/itslearning/speicher/` | `itslearning-storage` |
| `/itslearning/speicher/einrichten/` | `itslearning-storage-save` |
| `/dav/<uuid:public_id>/` | `webdav-root` |
| `/dav/<uuid:public_id>/<path:resource>` | `webdav-resource` |
| `/mehr/ui-zustaende/` | `ui-demo-states` |
| `/mehr/systemstatus/` | `ui-system-status` |
| `/health/` | `health` |
| `/admin/` | Include / eigene Systemoberfläche |
| `/cms/` | Include / eigene Systemoberfläche |
| `/accounts/` | Include / eigene Systemoberfläche |
| `/invitation/<str:token>/` | `accept-invitation` |
| `/sessions/revoke-all/` | `revoke-all-sessions` |
| `/sessions/idle-timeout/` | `idle-session-timeout` |
| `/push/subscriptions/` | `push-subscriptions` |
| `/push/configuration/` | `push-configuration` |
| `/push/self-test/` | `push-self-test` |
| `/manifest.webmanifest` | `manifest` |
| `/service-worker.js` | `service-worker` |
| `/offline/` | `offline` |
| `/documents/<int:document_id>/<str:variant>/` | `document-download` |
| `/posts/<int:post_id>/comments/` | `create-comment` |
| `/comments/<int:comment_id>/withdraw/` | `withdraw-comment` |
| `/comments/<int:comment_id>/moderate/` | `moderate-comment` |
| `/events/<int:event_id>/` | `event-detail` |
| `/events/<int:event_id>/recipes/<int:recipe_id>/import/` | `event-recipe-import` |
| `/impressum/` | `imprint` |
| `/open-source-lizenzen/` | `open-source-licenses` |
| `/nutzung/` | `terms` |
| `/mehr/reservierungen/<int:reservation_id>/erledigt/` | `ui-fulfill-reservation` |
| `/events/<int:event_id>/food/<str:source_id>/import/` | `event-food-import` |
| `/items/<int:item_id>/reserve/` | `reserve-item` |
| `/reservations/<int:reservation_id>/cancel/` | `cancel-reservation` |
| `/galleries/<int:gallery_id>/` | `gallery-detail` |
| `/galleries/<int:gallery_id>/upload/` | `gallery-upload` |
| `/photos/<uuid:photo_id>/kind-zuweisen/` | `photo-assign-child` |
| `/photos/<uuid:photo_id>/kind/<int:person_id>/entfernen/` | `photo-remove-child` |
| `/photos/<uuid:photo_id>/moderate/` | `photo-moderate` |
| `/photos/<uuid:photo_id>/resubmit/` | `photo-resubmit` |
| `/photos/<uuid:photo_id>/report/` | `photo-report` |
| `/photos/<uuid:photo_id>/withdraw/` | `photo-withdraw` |
| `/photos/<uuid:photo_id>/<str:variant>/` | `photo-file` |
| `/biometrics/` | `biometric-search` |
| `/biometrics/moderation/` | `biometric-moderation` |
| `/biometrics/profiles/<int:student_id>/enable/<int:class_id>/` | `biometric-profile-enable` |
| `/biometrics/profiles/<uuid:public_id>/withdraw/` | `biometric-profile-withdraw` |
| `/biometrics/photos/<uuid:photo_id>/analyze/` | `biometric-photo-analyze` |
| `/biometrics/matches/<uuid:public_id>/<str:decision>/` | `biometric-decision` |
| `/chat/rooms/<uuid:room_id>/` | `chat-room` |
| `/chat/rooms/<uuid:room_id>/messages/` | `chat-messages` |
| `/chat/sticker-assets/<int:asset_id>/image/` | `chat-asset-image` |
| `/chat/messages/<uuid:message_id>/` | `chat-message` |
| `/chat/messages/<uuid:message_id>/report/` | `chat-report` |
| `/chat/messages/<uuid:message_id>/moderate/` | `chat-moderate` |
| `/schedule/classes/<int:class_id>/week/` | `schedule-week` |
| `/schedule/ical/<str:token>/` | `schedule-ical` |
| `/schedule/classes/<int:class_id>/ical-token/` | `schedule-ical-issue` |
| `/schedule/classes/<int:class_id>/week/` | `schedule-week` |
| `/schedule/ical/<str:token>/` | `schedule-ical` |
| `/schedule/classes/<int:class_id>/ical-token/` | `schedule-ical-issue` |
| `/api/portal-navigation/` | `api_portal_navigation` |

## Templates

122 HTML-Dateien unter `app/templates` und `app/src`.
Enthält Teiltemplates und Altvarianten; das Vorhandensein einer Datei beweist
keine aktive Route. Vor Änderungen den tatsächlich verwendeten Renderpfad
prüfen. Die zusätzlichen zwei Biometrie-Templates liegen im Modulverzeichnis.

- `app/templates/base.html`
- `app/templates/Navigation.html`
- `app/templates/account/login.html`
- `app/templates/account/password_reset_from_key_done.html`
- `app/templates/account/password_reset_from_key.html`
- `app/templates/admin/core/school/change_list.html`
- `app/templates/admin/core/school/import_csv.html`
- `app/templates/allauth/layouts/base.html`
- `app/templates/allauth/layouts/entrance.html`
- `app/templates/allauth/layouts/manage.html`
- `app/templates/core/accept_invitation.html`
- `app/templates/core/dashboard.html`
- `app/templates/core/demo.html`
- `app/templates/core/family_invitation_invalid.html`
- `app/templates/core/family_register.html`
- `app/templates/core/family_registration_received.html`
- `app/templates/core/invitation_entry.html`
- `app/templates/core/invitation_invalid.html`
- `app/templates/core/offline.html`
- `app/templates/core/project.html`
- `app/templates/core/register.html`
- `app/templates/core/registration_activated.html`
- `app/templates/core/registration_received.html`
- `app/templates/core/registration_verified.html`
- `app/templates/includes/site_footer.html`
- `app/templates/itslearning/portal.html`
- `app/templates/itslearning/storage.html`
- `app/templates/legal/imprint.html`
- `app/templates/legal/open_source_licenses.html`
- `app/templates/legal/terms.html`
- `app/templates/meals/_codes.html`
- `app/templates/meals/_day_options.html`
- `app/templates/meals/plans.html`
- `app/templates/media/gallery_detail.html`
- `app/templates/mfa/index.html`
- `app/templates/mobility/detail.html`
- `app/templates/mobility/overview.html`
- `app/templates/model_visualizer/index.html`
- `app/templates/onboarding/_illustration.html`
- `app/templates/onboarding/experience_step.html`
- `app/templates/onboarding/missing_profile.html`
- `app/templates/onboarding/overview.html`
- `app/templates/onboarding/paused.html`
- `app/templates/onboarding/step.html`
- `app/templates/onboarding/tutorial_v2.html`
- `app/templates/onboarding/tutorial.html`
- `app/templates/privacy/information_v2.html`
- `app/templates/privacy/information.html`
- `app/templates/ui/_account_sections.html`
- `app/templates/ui/_app_installation.html`
- `app/templates/ui/_avatar_designer.html`
- `app/templates/ui/_family_person_card.html`
- `app/templates/ui/_form_actions.html`
- `app/templates/ui/_icon.html`
- `app/templates/ui/_password_toggle.html`
- `app/templates/ui/_settings_navigation.html`
- `app/templates/ui/_theme_selection.html`
- `app/templates/ui/account_deleted.html`
- `app/templates/ui/calendar_v2.html`
- `app/templates/ui/calendar.html`
- `app/templates/ui/chat_asset_form.html`
- `app/templates/ui/chat_assets_settings.html`
- `app/templates/ui/chat_overview.html`
- `app/templates/ui/chat_retention_settings.html`
- `app/templates/ui/chat_room.html`
- `app/templates/ui/chat.html`
- `app/templates/ui/consents_v2.html`
- `app/templates/ui/consents.html`
- `app/templates/ui/contacts.html`
- `app/templates/ui/dashboard_v2.html`
- `app/templates/ui/dashboard.html`
- `app/templates/ui/delete_account.html`
- `app/templates/ui/demo_states.html`
- `app/templates/ui/design_system.html`
- `app/templates/ui/documents.html`
- `app/templates/ui/event_detail.html`
- `app/templates/ui/event_poll.html`
- `app/templates/ui/events.html`
- `app/templates/ui/family_child_data.html`
- `app/templates/ui/family_invitations.html`
- `app/templates/ui/family_overview.html`
- `app/templates/ui/family.html`
- `app/templates/ui/galleries.html`
- `app/templates/ui/learning_portals.html`
- `app/templates/ui/menu_management.html`
- `app/templates/ui/monitoring_dashboard.html`
- `app/templates/ui/more.html`
- `app/templates/ui/notification_list.html`
- `app/templates/ui/notifications.html`
- `app/templates/ui/personal_profile_data.html`
- `app/templates/ui/personal_profile.html`
- `app/templates/ui/pilot_reports_management.html`
- `app/templates/ui/portal_adapter_definition_detail.html`
- `app/templates/ui/portal_adapter_detail.html`
- `app/templates/ui/portal_adapter_management.html`
- `app/templates/ui/portal_management.html`
- `app/templates/ui/post_detail.html`
- `app/templates/ui/posts.html`
- `app/templates/ui/presentation_poll_settings.html`
- `app/templates/ui/registration_invitation.html`
- `app/templates/ui/role_management.html`
- `app/templates/ui/role_people.html`
- `app/templates/ui/role_permissions.html`
- `app/templates/ui/school_catalog_import.html`
- `app/templates/ui/school_class_detail.html`
- `app/templates/ui/school_detail.html`
- `app/templates/ui/school_management.html`
- `app/templates/ui/school_setup_import.html`
- `app/templates/ui/session_timeout_settings.html`
- `app/templates/ui/students.html`
- `app/templates/ui/system_status.html`
- `app/templates/ui/teachers.html`
- `app/templates/ui/template_preview.html`
- `app/templates/ui/theme_form.html`
- `app/templates/ui/theme_management.html`
- `app/templates/ui/theme_settings.html`
- `app/templates/webuntis/absences.html`
- `app/templates/webuntis/calendar_settings.html`
- `app/templates/webuntis/connection_v2.html`
- `app/templates/webuntis/connection.html`
- `app/src/klasse5e/biometrics/templates/biometrics/moderation.html`
- `app/src/klasse5e/biometrics/templates/biometrics/search.html`
