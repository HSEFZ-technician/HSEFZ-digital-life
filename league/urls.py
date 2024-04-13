from . import views
from django.urls import path, include

app_name = 'league'
urlpatterns = [
    path('', views.index),
    path('league_manage', views.league_manage, name='league_manage'),
    path('modify_league', views.modify_league, name='modify_league'),
    path('sports_detail', views.sports_detail, name='sports_detail')
]
