from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('register-user/', views.register_user_by_admin, name='register_user_by_admin'),
    path('students/', views.admin_student_list, name='admin_student_list'),
    path('teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('attendance/', views.admin_attendance_report, name='admin_attendance_report'),
]
