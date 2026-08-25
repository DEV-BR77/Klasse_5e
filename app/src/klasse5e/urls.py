from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls

from klasse5e.core import views

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
]
