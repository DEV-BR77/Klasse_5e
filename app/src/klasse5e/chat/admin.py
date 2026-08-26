from django.contrib import admin

from .models import ChatPreference, ChatReport, ChatRoom

admin.site.register([ChatRoom, ChatReport, ChatPreference])
