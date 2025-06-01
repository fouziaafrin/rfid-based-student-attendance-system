from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('register-user/', views.register_user_by_admin, name='register_user_by_admin'),
]
