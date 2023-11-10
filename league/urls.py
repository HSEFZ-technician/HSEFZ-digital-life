from . import views
from django.urls import path, include

app_name = 'league'
urlpatterns = [
    path('', views.index),
]
