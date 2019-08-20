from django.contrib import admin
from .models import Log, AmoUser, AmoLead, FBAccount


admin.site.register(Log)
admin.site.register(AmoUser)
admin.site.register(AmoLead)
admin.site.register(FBAccount)
