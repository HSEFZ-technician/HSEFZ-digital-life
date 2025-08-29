from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.verify_student, name='verify_student'),
]
