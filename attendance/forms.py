from django import forms
from accounts.models import User
from .models import Attendance, Semester, Course, CourseSchedule
from .models import LeaveRequest

class ManualAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    status = forms.ChoiceField(choices=[('present', 'Present'), ('absent', 'Absent')])
    mode = forms.ChoiceField(choices=Attendance._meta.get_field('mode').choices)
    

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3})
        }

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['name', 'code', 'is_active', 'order']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'teacher', 'semester']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')
        
class CourseScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['course', 'day_of_week', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()
