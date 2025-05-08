from django.contrib import admin

from .models import Signal, SignalFeatures
# Register your models here.

admin.site.register(Signal)
admin.site.register(SignalFeatures)
