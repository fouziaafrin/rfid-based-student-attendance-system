from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('manual/', views.manual_attendance_view, name='manual_attendance'),
    path('leave/apply/', views.apply_leave_view, name='apply_leave'),
    path('leave/status/', views.view_leave_status, name='view_leave_status'),
    path('leave/manage/', views.manage_leave_requests, name='manage_leave_requests'),
    path('leave/approve/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('semester/add/', views.add_semester, name='add_semester'),
    path('course/add/', views.add_course, name='add_course'),
    path('semesters/', views.view_semesters, name='view_semesters'),
    path('courses/', views.view_courses, name='view_courses'),
    path('course-schedule/add/', views.add_course_schedule, name='add_course_schedule'),
    path('course-schedule/', views.view_course_schedules, name='view_course_schedules'),
]
