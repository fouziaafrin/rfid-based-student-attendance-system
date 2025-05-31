from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, CustomLoginForm
from django.contrib import messages
from .models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from core.models import RFIDSession
from attendance.models import Attendance
from django.db.models import Q

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
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
                    return redirect('admin_dashboard')
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# Custom role-check decorators
def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You are not authorized to view this page.")
        return login_required(wrapper)
    return decorator

@role_required('admin')
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

@role_required('teacher')
def teacher_dashboard(request):
     # Fetch RFID sessions created by this teacher
    sessions = RFIDSession.objects.filter(teacher=request.user).order_by('-start_time')[:5]

    # Fetch attendance entries for this teacher
    attendance_records = Attendance.objects.filter(
    class_session__course__teacher=request.user
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
    class_session__course__teacher=request.user
).values_list('student', flat=True).distinct()

    students = User.objects.filter(id__in=student_ids, role='student')
    
    return render(request, 'accounts/student_list.html', {'students': students})


@role_required('teacher')
def student_attendance_detail(request, student_id):
    student = User.objects.get(id=student_id, role='student')
    
    # Only show attendance the current teacher has taken
    attendance_records = Attendance.objects.filter(
        student=student,
        class_session__course__teacher=request.user
    ).order_by('-date')

    return render(request, 'accounts/student_attendance_detail.html', {
        'student': student,
        'records': attendance_records
    })
