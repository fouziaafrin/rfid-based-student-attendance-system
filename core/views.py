from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.models import User
from .models import RFIDSession
from attendance.models import Attendance
from datetime import datetime
from attendance.models import Course, ClassSession
from datetime import datetime, timedelta
from django.utils import timezone

# TEACHER STARTS SESSION
@api_view(['POST'])
def start_session(request):
    uid = request.data.get('uid')
    pin = request.data.get('pin')
    selected_course_id = request.data.get('course_id')

    try:
        teacher = User.objects.get(rfid_uid=uid, role='teacher')
        if teacher.pin != pin:
            return Response({'status': 'error', 'message': 'Invalid PIN'})

        now = timezone.now()
        weekday = now.strftime('%A')
        current_time = now.time()

        # If course is already selected by teacher (step 2)
        if selected_course_id:
            try:
                course = Course.objects.get(id=selected_course_id, teacher=teacher)
            except Course.DoesNotExist:
                return Response({'status': 'error', 'message': 'Invalid course selection'})

            session = ClassSession.objects.create(
                course=course,
                teacher=teacher
            )
            return Response({
                'status': 'success',
                'session_id': session.id,
                'course': course.code,
                'semester': course.semester.name,
                'start_time': str(session.start_time),
            })

        # Step 1: Try to auto-detect possible classes
        possible_courses = Course.objects.filter(
            teacher=teacher,
            day_of_week=weekday,
            start_time__lte=current_time,
            end_time__gte=current_time,
            semester__start_date__lte=now.date(),
            semester__end_date__gte=now.date()
        )

        if not possible_courses.exists():
            return Response({'status': 'error', 'message': 'No scheduled class at this time'})

        if possible_courses.count() == 1:
            # One match → auto-create
            course = possible_courses.first()
            session = ClassSession.objects.create(course=course, teacher=teacher)
            return Response({
                'status': 'success',
                'session_id': session.id,
                'course': course.code,
                'semester': course.semester.name,
                'start_time': str(session.start_time),
            })

        # Multiple matches → ask teacher to select
        course_options = [{
            'id': c.id,
            'code': c.code,
            'name': c.name,
            'semester': c.semester.name,
            'start_time': str(c.start_time),
            'end_time': str(c.end_time),
        } for c in possible_courses]

        return Response({
            'status': 'choose_course',
            'message': 'Multiple matching courses found. Please select one.',
            'options': course_options
        })

    except User.DoesNotExist:
        return Response({'status': 'error', 'message': 'Teacher not found'})


# STUDENT TAP
@api_view(['POST'])
def mark_attendance(request):
    uid = request.data.get('uid')

    try:
        student = User.objects.get(rfid_uid=uid, role='student')
        session = RFIDSession.objects.filter(is_active=True).order_by('-start_time').first()

        if not session or session.has_expired():
            return Response({'status': 'error', 'message': 'No active session'})
        
        if student.semester != session.course.semester:
            return Response({'status': 'error', 'message': 'Student not enrolled in this semester'})


        # Save attendance
        Attendance.objects.get_or_create(
            student=student,
            date=datetime.today().date(),
            defaults={
                'status': 'present',
                'teacher': session.teacher,
                'recorded_manually': False
            }
        )

        return Response({'status': 'success', 'message': 'Attendance marked'})
    except User.DoesNotExist:
        return Response({'status': 'error', 'message': 'Student not found'})
