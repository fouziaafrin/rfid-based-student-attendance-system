from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.models import User
from .models import RFIDSession
from attendance.models import Attendance
from datetime import datetime

# TEACHER STARTS SESSION
@api_view(['POST'])
def start_session(request):
    uid = request.data.get('uid')
    pin = request.data.get('pin')

    try:
        teacher = User.objects.get(rfid_uid=uid, role='teacher')
        if teacher.pin == pin:
            session = RFIDSession.objects.create(teacher=teacher)
            return Response({'status': 'success', 'session_id': session.id})
        else:
            return Response({'status': 'error', 'message': 'Invalid PIN'})
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
