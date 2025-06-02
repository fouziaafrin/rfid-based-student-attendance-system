from django.db import models
from accounts.models import User
from django.utils import timezone

    
    
# temporary for handling schedule

class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., "1st Year 1st Semester"
    code = models.CharField(max_length=20, unique=True)  # e.g., "Y1S1" or "2025-SPR"
    is_active = models.BooleanField(default=True)  # Admin controls this
    order = models.PositiveIntegerField()  # For sequencing semesters (Y1S1 = 1, Y1S2 = 2, ...)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)  # e.g., "CSE-301"
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.code} - {self.name}"

    

class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    started_by = models.ForeignKey(User, limit_choices_to={'role': 'teacher'}, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.code} on {self.date} from {self.start_time} to {self.end_time}"

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='student_attendance')
    # teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'}, related_name='teacher_attendance')
    # date = models.DateField()
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    recorded_manually = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'class_session')

    def __str__(self):
        return f"{self.student.full_name} - {self.class_session} - {self.status}"
    