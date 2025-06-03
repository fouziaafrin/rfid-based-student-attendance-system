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

            weekday = date_selected.strftime('%A')  # e.g. 'Monday'

            # Get the teacher’s scheduled courses on that weekday
            schedules = CourseSchedule.objects.filter(
                course__teacher=teacher,
                day_of_week=weekday
            )

            if not schedules.exists():
                messages.error(request, f"No scheduled classes found for {weekday}.")
                return redirect('attendance:manual_attendance')

            # Create ClassSession(s) if they don’t already exist for the date
            sessions = []
            for schedule in schedules:
                session, created = ClassSession.objects.get_or_create(
                    course_schedule=schedule,
                    date=date_selected,
                    defaults={
                        'start_time': schedule.start_time,
                        'end_time': schedule.end_time,
                        'started_by': teacher,
                        'is_active': True
                    }
                )
                sessions.append(session)

            for session in sessions:
                for student in students:
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        class_session=session,
                        defaults={
                            'status': status,
                            'recorded_manually': True,
                            'mode': mode
                        }
                    )
                    if not created:
                        attendance.status = status
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
