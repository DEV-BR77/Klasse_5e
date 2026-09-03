from django.contrib import admin

from .models import ChatPreference, ChatReport, ChatRetentionCategory, ChatRoom

admin.site.register([ChatRoom, ChatReport, ChatPreference, ChatRetentionCategory])
