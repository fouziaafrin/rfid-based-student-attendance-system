from django.urls import path
from . import views

urlpatterns = [
    path('start-session/', views.start_session, name='start_session'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
]
