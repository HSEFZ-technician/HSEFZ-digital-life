from django.contrib import admin
from .models import SelectionEvent, EventClassType, EventClassInformation


class SelectionEventAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'title')
    search_fields = ('title',) 
    filter_horizontal = ('student_group', 'teachers_group')


class EventClassTypeAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'type_name')
    search_fields = ('type_name',)


class EventClassInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_id', 'class_type', 'max_num', 'current_num')
    list_filter = ('event_id', 'class_type')
    search_fields = ('name', 'desc', 'full_desc')
    autocomplete_fields = ('class_type', 'event_id')


admin.site.register(SelectionEvent, SelectionEventAdmin)
admin.site.register(EventClassType, EventClassTypeAdmin)
admin.site.register(EventClassInformation, EventClassInformationAdmin)