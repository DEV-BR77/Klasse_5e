from django.contrib import admin
from wagtail.snippets.models import register_snippet

from .models import Gallery, Photo, PhotoModerationDecision, PhotoReport, PhotoSubjectDeclaration

register_snippet(Gallery)
for model in [Gallery, Photo, PhotoSubjectDeclaration, PhotoReport, PhotoModerationDecision]:
    admin.site.register(model)
