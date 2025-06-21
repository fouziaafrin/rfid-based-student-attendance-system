from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('my-students/', views.student_list_for_teacher, name='student_list'),
    path('my-students/<int:student_id>/', views.student_attendance_detail, name='student_attendance_detail'),
     path('teacher/schedule/', views.teacher_weekly_schedule, name='teacher_schedule'),
    path('student/schedule/', views.student_weekly_schedule, name='student_schedule'),
]
