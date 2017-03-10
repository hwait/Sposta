from django.contrib import admin
from sposta_app.models import MEvent

@admin.register(MEvent)
class MEventAdmin(admin.ModelAdmin):
    pass

