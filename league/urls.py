from . import views
from django.urls import path, include

app_name = 'league'
urlpatterns = [
    path('', views.index),
    path('league_manage', views.league_manage, name='league_manage'),
    path('create_league', views.create_league, name='create_league'),
    path('class_team_manage', views.class_team_manage, name='class_team_manage'),
    path('modify_league', views.modify_league, name='modify_league'),
    path('modify_class_team', views.modify_class_team, name='modify_class_team'),
    path('sports_detail', views.sports_detail, name='sports_detail')
]
