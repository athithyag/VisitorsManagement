from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture', 'name', 'emp_id', 'email', 
            'designation', 'department', 'reporting_to', 'mobile'
        ]

from django import forms
from .models import Visitor

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            'visitor_name', 'visitor_email', 'category', 'appointment_date',
            'appointment_time', 'reason', 'designated_attendee', 'document'
        ]


from django import forms
from .models import Visitor

class RescheduleMeetForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['appointment_date', 'appointment_time']  # Allow only date and time to be updated
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

