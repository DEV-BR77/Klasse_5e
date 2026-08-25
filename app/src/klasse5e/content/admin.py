from django.contrib import admin
from wagtail.snippets.models import register_snippet

from .models import Comment, CommentReport, Post, ProtectedDocument, TeacherProfile

for model in [ProtectedDocument, TeacherProfile, Post]:
    register_snippet(model)

for model in [ProtectedDocument, TeacherProfile, Post, Comment, CommentReport]:
    admin.site.register(model)
