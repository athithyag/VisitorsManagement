from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import random
from datetime import timedelta, datetime
from django import forms



class Visitor(models.Model):
    visitor_id = models.PositiveIntegerField(unique=True)  # Unique ID
    visitor_name = models.CharField(max_length=100)
    visitor_email = models.EmailField()
    category = models.CharField(max_length=50)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    designated_attendee = models.CharField(max_length=100)
    document = models.FileField(upload_to='visitor_documents/', null=True, blank=True)  # Document upload

    def __str__(self):
        return self.visitor_name
    



class Profile(models.Model):
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    name = models.CharField(max_length=255)
    emp_id = models.CharField(max_length=10)
    email = models.EmailField()
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    reporting_to = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.name



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture', 'name', 'emp_id', 'email', 
            'designation', 'department', 'reporting_to', 'mobile'
        ]



class RescheduledMeet(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    rescheduled_date = models.DateField()
    rescheduled_time = models.TimeField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')





class VisitorSchedule(models.Model):
    visitor = models.OneToOneField('Visitor', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Rescheduled', 'Rescheduled'),
    ])
    rescheduled_date = models.DateField(blank=True, null=True)
    rescheduled_time = models.TimeField(blank=True, null=True)
    designated_attendee = models.CharField(blank=True, null=True, max_length=100)

    # Verification code field
    verification_code = models.CharField(max_length=4, blank=True, null=True)
    
    # New fields for QR code functionality
    in_time = models.TimeField(blank=True, null=True)  # Stores when the visitor checks in
    out_time = models.TimeField(blank=True, null=True)  # Stores when the visitor checks out
    total_duration = models.DurationField(blank=True, null=True)  # Duration of the visit
    feedback = models.TextField(blank=True, null=True)  # Feedback or summary of the meeting

    def generate_verification_code(self):
        """Generates a random 4-digit code."""
        self.verification_code = str(random.randint(1000, 9999))
        self.save()

    def calculate_duration(self):
        """Calculates the total duration of the visit based on in_time and out_time."""
        if self.in_time and self.out_time:
            in_datetime = datetime.combine(datetime.today(), self.in_time)
            out_datetime = datetime.combine(datetime.today(), self.out_time)
            if out_datetime < in_datetime:
                out_datetime += timedelta(days=1)
            duration = out_datetime - in_datetime
            self.total_duration = duration
            self.save()

    def get_total_duration_formatted(self):
        if self.total_duration:
            total_seconds = int(self.total_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return ""


    def __str__(self):
        return f"{self.visitor.visitor_name} - {self.status}"




