from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, 'admin', password, **extra_fields)

# User Model
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    rfid_uid = models.CharField(max_length=50, blank=True, null=True)
    pin = models.CharField(max_length=10, blank=True, null=True)
    
    # Student-specific fields
    class_roll = models.CharField(max_length=10, blank=True, null=True)
    exam_roll = models.CharField(max_length=20, blank=True, null=True)
    registration_no = models.CharField(max_length=30, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"
