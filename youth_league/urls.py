from . import views
from django.urls import path, include

app_name = 'youth_league'
urlpatterns = [
    path('', views.index),
    path('homework_inquiry.html', views.homework_inquiry, name='homework_inquiry'),
    path('test_inquiry.html', views.test_inquiry, name='test_inquiry'),
    path('course_manage', views.course_manage, name='course_manage'),
    path('course_score_manage', views.course_score_manage, name='course_score_manage'),
    path('test_manage', views.test_manage, name='test_manage'),
    path('test_score_manage', views.test_score_manage, name='test_score_manage'),
    path('appeal_respond', views.appeal_respond, name='appeal_respond'),
    path('appeal_test_respond', views.appeal_test_respond, name='appeal_test_respond'),
    path('import_course_data', views.import_course_data, name='import_course_data'),
    path('export_course_data', views.export_course_data, name='export_course_data'),
    path('import_course_score_data', views.import_course_score_data, name='import_course_score_data'),
    path('export_course_score_data', views.export_course_score_data, name='export_course_score_data'),
    path('import_test_data', views.import_test_data, name='import_test_data'),
    path('export_test_data', views.export_test_data, name='export_test_data'),
    path('import_test_score_data', views.import_test_score_data, name='import_test_score_data'),
    path('export_test_score_data', views.export_test_score_data, name='export_test_score_data'),
]
