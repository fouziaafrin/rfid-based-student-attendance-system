from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.views import role_required
from .forms import ManualAttendanceForm
from .models import Attendance
from django.contrib import messages
from datetime import date

@role_required('teacher')
def manual_attendance_view(request):
    if request.method == 'POST':
        form = ManualAttendanceForm(request.POST)
        if form.is_valid():
            date_selected = form.cleaned_data['date']
            students = form.cleaned_data['students']
            status = form.cleaned_data['status']
            teacher = request.user

            for student in students:
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=date_selected,
                    defaults={
                        'status': status,
                        'teacher': teacher,
                        'recorded_manually': True
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.teacher = teacher
                    attendance.recorded_manually = True
                    attendance.save()
            messages.success(request, "Attendance recorded successfully.")
            return redirect('accounts:teacher_dashboard')
    else:
        form = ManualAttendanceForm(initial={'date': date.today()})
    
    return render(request, 'attendance/manual_attendance.html', {'form': form})
