from django import forms
from accounts.models import User

class AdminUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'rfid_uid', 'pin', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if pwd != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
