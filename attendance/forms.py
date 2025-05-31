from django import forms
from accounts.models import User
from .models import Attendance

class ManualAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    status = forms.ChoiceField(choices=[('present', 'Present'), ('absent', 'Absent')])
