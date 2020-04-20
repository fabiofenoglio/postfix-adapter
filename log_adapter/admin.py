from django.contrib import admin

# Register your models here.

from .models import MailStatus, MailStatusAttribute

admin.site.register(MailStatus)
admin.site.register(MailStatusAttribute)