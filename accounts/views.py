from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, CustomLoginForm
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from core.models import RFIDSession
from attendance.models import Attendance, CourseSchedule
from django.db.models import Q
from accounts.decorators import role_required
from collections import defaultdict
from django.utils.timezone import localtime

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.role == 'admin':
                    return redirect('accounts:admin_dashboard')
                elif user.role == 'teacher':
                    return redirect('accounts:teacher_dashboard')
                else:
                    return redirect('accounts:student_dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@role_required('admin')
def admin_dashboard(request):
    student_count = User.objects.filter(role='student').count()
    teacher_count = User.objects.filter(role='teacher').count()
    attendance_count = Attendance.objects.count()
    
    return render(request, 'accounts/admin_dashboard.html',{
        'student_count': student_count,
        'teacher_count': teacher_count,
        'attendance_count': attendance_count, 
    })

@role_required('teacher')
def teacher_dashboard(request):
     # Fetch RFID sessions created by this teacher
    sessions = RFIDSession.objects.filter(teacher=request.user).order_by('-start_time')[:5]

    # Fetch attendance entries for this teacher
    attendance_records = Attendance.objects.filter(
    class_session__course_schedule__course__teacher=request.user
).order_by('-class_session__date')[:10]


    return render(request, 'accounts/teacher_dashboard.html', {
        'sessions': sessions,
        'attendance_records': attendance_records,
    })

@role_required('student')
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')


@role_required('teacher')
def student_list_for_teacher(request):
    # Get students this teacher has marked attendance for
    student_ids = Attendance.objects.filter(
    class_session__course_schedule__course__teacher=request.user
).values_list('student', flat=True).distinct()

    students = User.objects.filter(id__in=student_ids, role='student')
    
     # Build list with attendance percentage
    student_data = []
    for student in students:
        records = Attendance.objects.filter(student=student, class_session__course_schedule__course__teacher=request.user)
        total = records.count()
        present = records.filter(status='present').count()
        percentage = round((present / total) * 100, 2) if total > 0 else 0
        student_data.append({
            'student': student,
            'total': total,
            'present': present,
            'percentage': percentage,
        })

    return render(request, 'accounts/student_list.html', {'student_data': student_data})


@role_required('teacher')
def student_attendance_detail(request, student_id):
    student = User.objects.get(id=student_id, role='student')
    
    # Only show attendance the current teacher has taken
    attendance_records = Attendance.objects.filter(
        student=student,
        class_session__course_schedule__course__teacher=request.user
    ).order_by('-class_session__date')
    
    total = attendance_records.count()
    present = attendance_records.filter(status='present').count()
    percentage = round((present / total) * 100, 2) if total > 0 else 0

    return render(request, 'accounts/student_attendance_detail.html', {
        'student': student,
        'records': attendance_records,
        'total': total,
        'present': present,
        'percentage': percentage,
    })


@role_required('teacher')
def teacher_weekly_schedule(request):
    schedules = CourseSchedule.objects.filter(course__teacher=request.user).order_by('day_of_week', 'start_time')
    
    # Define the time slots (hour-based blocks)
    hour_blocks = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']
    
     # Prepare data structure: schedule_map[day][hour] = list of schedules
    schedule_map = defaultdict(lambda: defaultdict(list))
    for schedule in schedules:
        start_hour = schedule.start_time.strftime('%H:00')
        schedule_map[schedule.day_of_week][start_hour].append(schedule)

    context = {
        'schedules': schedules,
        'days': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'hour_blocks': hour_blocks,
        'schedule_map': dict(schedule_map),
    }
    
    return render(request, 'accounts/teacher_schedule.html', {'schedules': schedules})

@role_required('student')
def student_weekly_schedule(request):
    semester = request.user.semester
    schedules = CourseSchedule.objects.filter(course__semester=semester).order_by('day_of_week', 'start_time')
    return render(request, 'accounts/student_schedule.html', {'schedules': schedules})
