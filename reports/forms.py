from django import forms
from accounts.models import User

class AdminUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'role',
            'rfid_uid', 'pin', 'class_roll', 'exam_roll', 'registration_no',
            'password', 'confirm_password'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')
        rfid_uid = cleaned_data.get('rfid_uid')
        pin = cleaned_data.get('pin')

        # Password check
        if password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        # Role-based RFID/PIN logic
        if role in ['student', 'teacher'] and not rfid_uid:
            self.add_error('rfid_uid', 'RFID UID is required for students and teachers.')

        if role == 'teacher' and not pin:
            self.add_error('pin', 'PIN is required for teachers.')

        if role == 'student' and pin:
            self.add_error('pin', 'Students should not have a PIN.')

        if role == 'admin' and (rfid_uid or pin):
            self.add_error('rfid_uid', 'Admin should not have RFID UID.')
            self.add_error('pin', 'Admin should not have a PIN.')
            
        if role == 'student':
            for field in ['class_roll', 'exam_roll', 'registration_no']:
                if not cleaned_data.get(field):
                    self.add_error(field, f"{field.replace('_', ' ').capitalize()} is required for students.")

