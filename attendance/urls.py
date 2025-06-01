from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('manual/', views.manual_attendance_view, name='manual_attendance'),
]
