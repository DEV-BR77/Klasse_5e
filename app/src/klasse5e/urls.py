from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls

from klasse5e.biometrics import views as biometric_views
from klasse5e.content import views as content_views
from klasse5e.core import views
from klasse5e.events import views as event_views
from klasse5e.media import views as media_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("health/", views.health, name="health"),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("invitation/<str:token>/", views.accept_invitation, name="accept-invitation"),
    path("sessions/revoke-all/", views.revoke_all_sessions, name="revoke-all-sessions"),
    path("push/subscriptions/", views.push_subscriptions, name="push-subscriptions"),
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
]
