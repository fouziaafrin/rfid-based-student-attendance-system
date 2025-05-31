from django.urls import path
from . import views

urlpatterns = [
    path('manual/', views.manual_attendance_view, name='manual_attendance'),
]
