from django.contrib import admin
from .models import SelectionEvent, EventClassType

# Register your models here.


class SelectionEventAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'title')


class EventClassTypeAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'type_name')


admin.site.register(SelectionEvent, SelectionEventAdmin)
admin.site.register(EventClassType, EventClassTypeAdmin)
