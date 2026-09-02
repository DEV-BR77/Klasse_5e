from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls

from klasse5e.biometrics import views as biometric_views
from klasse5e.chat import views as chat_views
from klasse5e.content import views as content_views
from klasse5e.core import onboarding_experience_views, onboarding_views, ui_views, views
from klasse5e.events import views as event_views
from klasse5e.itslearning import views as itslearning_views
from klasse5e.itslearning.webdav import webdav
from klasse5e.media import views as media_views
from klasse5e.schedule import views as schedule_views
from klasse5e.webuntis import views as webuntis_views

urlpatterns = [
    path("registrieren/", views.register, name="register"),
    path("registrieren/email/<str:token>/", views.verify_registration_email, name="registration-email-verify"),
    path("aktivieren/<str:token>/", views.activate_registration, name="registration-activate"),
    path(
        "datenschutz/",
        TemplateView.as_view(template_name="privacy/information_v2.html"),
        name="privacy-information",
    ),
    path("onboarding/", onboarding_experience_views.onboarding_step, name="onboarding-resume"),
    path("onboarding/pausiert/", onboarding_experience_views.onboarding_paused, name="onboarding-paused"),
    path(
        "onboarding/schritt/<int:step>/",
        onboarding_experience_views.onboarding_step,
        name="onboarding-step",
    ),
    path(
        "einwilligungen/<slug:key>/<int:subject_id>/widerrufen/",
        onboarding_views.consent_withdraw,
        name="consent-withdraw",
    ),
    path("tutorial/", onboarding_experience_views.tutorial_step, name="tutorial-resume"),
    path(
        "tutorial/schritt/<int:step>/", onboarding_experience_views.tutorial_step, name="tutorial-step"
    ),
    path("", ui_views.dashboard, name="dashboard"),
    path("einstellungen/profil/", views.personal_profile, name="personal-profile"),
    path("profile/<int:person_id>/foto/", views.profile_photo, name="profile-photo"),
    path("benachrichtigungen/", views.notification_list, name="notification-list"),
    path("benachrichtigungen/<int:notification_id>/lesen/", views.notification_read, name="notification-read"),
    path("benachrichtigungen/alle-lesen/", views.notifications_read_all, name="notifications-read-all"),
    path("kalender/", ui_views.calendar, name="ui-calendar"),
    path("kontakte/", ui_views.contacts, name="ui-contacts"),
    path("schueler/", ui_views.students, name="ui-students"),
    path("chat/", ui_views.chat_overview, name="ui-chat"),
    path("chat/<uuid:room_id>/ansicht/", ui_views.chat_room, name="ui-chat-room"),
    path("verwaltung/", ui_views.portal_management, name="portal-management"),
    path("verwaltung/anmeldung/", ui_views.registration_invitation, name="registration-invitation"),
    path("verwaltung/anmeldung/qr.svg", ui_views.registration_invitation_qr, name="registration-invitation-qr"),
    path("pilot/melden/", ui_views.pilot_report, name="pilot-report"),
    path("mehr/", ui_views.more, name="ui-more"),
    path("mehr/dokumente/", ui_views.documents, name="ui-documents"),
    path("mehr/aktuelles/", ui_views.posts, name="ui-posts"),
    path("mehr/aktuelles/<int:post_id>/", ui_views.post_detail, name="ui-post-detail"),
    path("mehr/veranstaltungen/", ui_views.events, name="ui-events"),
    path("mehr/veranstaltungen/<int:event_id>/", ui_views.event, name="ui-event"),
    path("mehr/mitbringen/<int:item_id>/reservieren/", ui_views.reserve, name="ui-reserve"),
    path(
        "mehr/veranstaltungen/<int:event_id>/freier-beitrag/",
        ui_views.free_contribution,
        name="ui-free-contribution",
    ),
    path(
        "mehr/reservierungen/<int:reservation_id>/zuruecknehmen/",
        ui_views.cancel_reservation,
        name="ui-cancel-reservation",
    ),
    path("mehr/lehrkraefte/", ui_views.teachers, name="ui-teachers"),
    path("mehr/fotos/", ui_views.galleries, name="ui-galleries"),
    path("mehr/familie/", ui_views.family, name="ui-family"),
    path("mehr/einwilligungen/", ui_views.consents, name="ui-consents"),
    path("mehr/benachrichtigungen/", ui_views.notifications, name="ui-notifications"),
    path("mehr/webuntis/", webuntis_views.connection, name="webuntis-connection"),
    path("mehr/webuntis/testen/", webuntis_views.test_connection, name="webuntis-test"),
    path("mehr/webuntis/entfernen/", webuntis_views.remove_connection, name="webuntis-remove"),
    path("mehr/webuntis/funktionen/", webuntis_views.update_features, name="webuntis-features"),
    path("mehr/webuntis/aktuell-pruefen/", webuntis_views.sync_now, name="webuntis-sync"),
    path(
        "mehr/webuntis/<int:connection_id>/kalender.ics",
        webuntis_views.download_calendar,
        name="webuntis-calendar-download",
    ),
    path(
        "mehr/webuntis/<int:connection_id>/kalender-abo/",
        webuntis_views.issue_calendar,
        name="webuntis-calendar-issue",
    ),
    path(
        "webuntis/kalender/<str:token>/",
        webuntis_views.calendar_feed,
        name="webuntis-calendar-feed",
    ),
    path("itslearning/", itslearning_views.portal, name="itslearning-portal"),
    path("itslearning/zugang/", itslearning_views.save_connection, name="itslearning-save"),
    path("itslearning/<int:student_id>/kurse/", itslearning_views.add_course, name="itslearning-course"),
    path("itslearning/<int:student_id>/synchronisieren/", itslearning_views.sync_now, name="itslearning-sync"),
    path("itslearning/speicher/", itslearning_views.storage, name="itslearning-storage"),
    path("itslearning/speicher/einrichten/", itslearning_views.save_storage, name="itslearning-storage-save"),
    path("dav/<uuid:public_id>/", webdav, name="webdav-root"),
    path("dav/<uuid:public_id>/<path:resource>", webdav, name="webdav-resource"),
    path("mehr/ui-zustaende/", ui_views.demo_states, name="ui-demo-states"),
    path("mehr/systemstatus/", ui_views.system_status, name="ui-system-status"),
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("invitation/<str:token>/", views.accept_invitation, name="accept-invitation"),
    path("sessions/revoke-all/", views.revoke_all_sessions, name="revoke-all-sessions"),
    path("push/subscriptions/", views.push_subscriptions, name="push-subscriptions"),
    path("push/configuration/", views.push_configuration, name="push-configuration"),
    path("push/self-test/", views.push_self_test, name="push-self-test"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("service-worker.js", views.service_worker, name="service-worker"),
    path("offline/", views.offline, name="offline"),
    path(
        "documents/<int:document_id>/<str:variant>/",
        content_views.document_download,
        name="document-download",
    ),
    path("posts/<int:post_id>/comments/", content_views.create_comment, name="create-comment"),
    path(
        "comments/<int:comment_id>/withdraw/",
        content_views.withdraw_comment,
        name="withdraw-comment",
    ),
    path(
        "comments/<int:comment_id>/moderate/",
        content_views.moderate_comment,
        name="moderate-comment",
    ),
    path("events/<int:event_id>/", event_views.event_detail, name="event-detail"),
    path("items/<int:item_id>/reserve/", event_views.reserve_item, name="reserve-item"),
    path(
        "reservations/<int:reservation_id>/cancel/",
        event_views.cancel_reservation,
        name="cancel-reservation",
    ),
    path("galleries/<int:gallery_id>/", media_views.gallery_detail, name="gallery-detail"),
    path("galleries/<int:gallery_id>/upload/", media_views.upload_photos, name="gallery-upload"),
    path("photos/<uuid:photo_id>/moderate/", media_views.moderate_photo, name="photo-moderate"),
    path("photos/<uuid:photo_id>/report/", media_views.report_photo, name="photo-report"),
    path("photos/<uuid:photo_id>/withdraw/", media_views.withdraw_photo, name="photo-withdraw"),
    path("photos/<uuid:photo_id>/<str:variant>/", media_views.photo_file, name="photo-file"),
    path("biometrics/", biometric_views.search_home, name="biometric-search"),
    path("biometrics/moderation/", biometric_views.moderation_queue, name="biometric-moderation"),
    path(
        "biometrics/profiles/<int:student_id>/enable/<int:class_id>/",
        biometric_views.enable_biometric_profile,
        name="biometric-profile-enable",
    ),
    path(
        "biometrics/profiles/<uuid:public_id>/withdraw/",
        biometric_views.withdraw_biometric_profile,
        name="biometric-profile-withdraw",
    ),
    path(
        "biometrics/photos/<uuid:photo_id>/analyze/",
        biometric_views.analyze_photo,
        name="biometric-photo-analyze",
    ),
    path(
        "biometrics/matches/<uuid:public_id>/<str:decision>/",
        biometric_views.decide_match,
        name="biometric-decision",
    ),
    path("chat/rooms/<uuid:room_id>/", chat_views.room_detail, name="chat-room"),
    path("chat/rooms/<uuid:room_id>/messages/", chat_views.messages, name="chat-messages"),
    path(
        "chat/messages/<uuid:message_id>/", chat_views.edit_or_delete_message, name="chat-message"
    ),
    path("chat/messages/<uuid:message_id>/report/", chat_views.report_message, name="chat-report"),
    path(
        "chat/messages/<uuid:message_id>/moderate/",
        chat_views.moderate_message,
        name="chat-moderate",
    ),
    path("schedule/classes/<int:class_id>/week/", schedule_views.week, name="schedule-week"),
    path("schedule/ical/<str:token>/", schedule_views.ical_feed, name="schedule-ical"),
    path(
        "schedule/classes/<int:class_id>/ical-token/",
        schedule_views.issue_ical,
        name="schedule-ical-issue",
    ),
]
