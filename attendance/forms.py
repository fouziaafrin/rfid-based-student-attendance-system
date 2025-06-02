from django import forms
from accounts.models import User
from .models import Attendance
from .models import LeaveRequest

class ManualAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    status = forms.ChoiceField(choices=[('present', 'Present'), ('absent', 'Absent')])
    

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3})
        }
