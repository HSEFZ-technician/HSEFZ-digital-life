from . import views
from django.urls import path, include

app_name = 'volunteer'
urlpatterns = [
    path('', views.index),
    path('score_input', views.score_manage,  name='score_input'),
    path('score_event', views.event_manage,  name='score_event'),
    path('modify_score_event', views.modify_score_event,
         name='modify_score_event'),
    path('modify_score', views.modify_score,  name='modify_score'),
    path('search_user', views.search_user,  name='search_user'),
]
