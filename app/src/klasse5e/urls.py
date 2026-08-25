from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls

from klasse5e.content import views as content_views
from klasse5e.core import views
from klasse5e.events import views as event_views

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
]
