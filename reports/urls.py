from django.urls import path
from . import views

urlpatterns = [
    path('register-user/', views.register_user_by_admin, name='register_user_by_admin'),
]
