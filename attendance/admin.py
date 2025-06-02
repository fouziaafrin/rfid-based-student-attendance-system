from django.contrib import admin
from .models import Semester, Course, CourseSchedule, ClassSession, Attendance, LeaveRequest

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(CourseSchedule)
admin.site.register(ClassSession)
admin.site.register(Attendance)
admin.site.register(LeaveRequest)