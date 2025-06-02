from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('manual/', views.manual_attendance_view, name='manual_attendance'),
    path('leave/apply/', views.apply_leave_view, name='apply_leave'),
    path('leave/status/', views.view_leave_status, name='view_leave_status'),
]
