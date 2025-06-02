from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.views import role_required
from .forms import ManualAttendanceForm
from .models import Attendance, Semester, Course, CourseSchedule, ClassSession
from django.contrib import messages
from datetime import date
from .models import LeaveRequest
from .forms import LeaveRequestForm, SemesterForm, CourseForm, CourseScheduleForm

@role_required('teacher')
def manual_attendance_view(request):
    if request.method == 'POST':
        form = ManualAttendanceForm(request.POST)
        if form.is_valid():
            date_selected = form.cleaned_data['date']
            students = form.cleaned_data['students']
            status = form.cleaned_data['status']
            mode = form.cleaned_data['mode']
            teacher = request.user

            # Get all class sessions taught by this teacher on the selected date
            sessions = ClassSession.objects.filter(
                date=date_selected,
                course_schedule__course__teacher=teacher
            )

            if not sessions.exists():
                messages.error(request, "No class session found for the selected date.")
                return redirect('attendance:manual_attendance')

            for session in sessions:
                for student in students:
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        class_session=session,
                        defaults={
                            'status': status,
                            'teacher': teacher,
                            'recorded_manually': True,
                            'mode': mode
                        }
                    )
                    if not created:
                        attendance.status = status
                        attendance.teacher = teacher
                        attendance.recorded_manually = True
                        attendance.mode = mode
                        attendance.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('accounts:teacher_dashboard')
    else:
        form = ManualAttendanceForm(initial={'date': date.today()})
    
    return render(request, 'attendance/manual_attendance.html', {'form': form})

@role_required('student')
def apply_leave_view(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.student = request.user
            leave.save()
            messages.success(request, "Leave request submitted.")
            return redirect('attendance:view_leave_status')
    else:
        form = LeaveRequestForm()
    return render(request, 'attendance/apply_leave.html', {'form': form})

@role_required('student')
def view_leave_status(request):
    leaves = LeaveRequest.objects.filter(student=request.user).order_by('-submitted_at')
    return render(request, 'attendance/leave_status.html', {'leaves': leaves})


@role_required('teacher')
def manage_leave_requests(request):
    pending_leaves = LeaveRequest.objects.filter(status='pending').order_by('-submitted_at')
    return render(request, 'attendance/teacher_leave_list.html', {'leaves': pending_leaves})

@role_required('teacher')
def approve_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'approved'
    leave.approved_by = request.user
    leave.save()
    messages.success(request, f"Approved leave for {leave.student.full_name}")
    return redirect('attendance:manage_leave_requests')

@role_required('teacher')
def reject_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'rejected'
    leave.approved_by = request.user
    leave.save()
    messages.warning(request, f"Rejected leave for {leave.student.full_name}")
    return redirect('attendance:manage_leave_requests')


@role_required('admin')
def add_semester(request):
    form = SemesterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Semester added successfully.")
        return redirect('attendance:view_semesters')
    return render(request, 'reports/add_semester.html', {'form': form})

@role_required('admin')
def add_course(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Course added successfully.")
        return redirect('attendance:view_courses')
    return render(request, 'reports/add_course.html', {'form': form})

@role_required('admin')
def view_semesters(request):
    semesters = Semester.objects.all().order_by('-order')
    return render(request, 'reports/view_semesters.html', {'semesters': semesters})

@role_required('admin')
def view_courses(request):
    courses = Course.objects.select_related('semester', 'teacher').order_by('semester__order')
    return render(request, 'reports/view_courses.html', {'courses': courses})


@role_required('admin')
def add_course_schedule(request):
    form = CourseScheduleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Course schedule added.")
        return redirect('attendance:view_course_schedules')
    return render(request, 'reports/add_course_schedule.html', {'form': form})

@role_required('admin')
def view_course_schedules(request):
    schedules = CourseSchedule.objects.select_related('course').order_by('course__semester__order', 'day_of_week')
    return render(request, 'reports/view_course_schedules.html', {'schedules': schedules})
