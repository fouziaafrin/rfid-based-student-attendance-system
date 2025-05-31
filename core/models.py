from django.db import models
from accounts.models import User
from datetime import timedelta, datetime

class RFIDSession(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.start_time + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def has_expired(self):
        return datetime.now() >= self.expires_at

    def __str__(self):
        return f"Session by {self.teacher.full_name} at {self.start_time}"
