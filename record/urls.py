from . import views
from django.urls import path, include

app_name = 'record'
urlpatterns = [
    path('', views.index),
    path('sport', views.sport_record),
    path('fun', views.fun_record),
    path('record_manage', views.record_manage,  name='record_manage'),
    path('create_record', views.create_record,  name='create_record'),
    path('modify_record', views.modify_record,  name='modify_record'),
    path('record_holder_manage', views.record_holder_manage,  name='record_holder_manage'),
    path('create_record_holder', views.create_record_holder,  name='create_record_holder'),
    path('modify_record_holder', views.modify_record_holder,  name='modify_record_holder'),
    path('import_record', views.import_record, name='import_record'),
    path('export_record', views.export_record, name='emport_record'),
    path('import_record_holder', views.import_record_holder, name='import_record_holder'),
    path('export_record_holder', views.export_record_holder, name='emport_record_holder'),
]
