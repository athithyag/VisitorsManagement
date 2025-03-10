from django.conf import settings
from celery import shared_task
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import datetime, timedelta
from myapp.models import Visitor, VisitorSchedule

@shared_task
def send_appointment_reminders():
    """Send email reminders to visitors 2 minutes before their appointment"""
    reminder_time = now() + timedelta(minutes=2)

    # Extract date and time parts separately
    reminder_date = reminder_time.date()
    reminder_hour = reminder_time.hour
    reminder_minute = reminder_time.minute

    upcoming_visitors = Visitor.objects.filter( 
        appointment_date=reminder_date,
        appointment_time__hour=reminder_hour,
        appointment_time__minute=reminder_minute,
        visitorschedule__status='Approved'  # Filter only approved visitors using related model

    )  

    print(f"Current Time: {now()}")
    print(f"Reminder Time: {reminder_time}")
    print(f"Visitors Found: {upcoming_visitors.count()}")

    for visitor in upcoming_visitors:
        email_subject = "Reminder: Upcoming Appointment at Pinesphere Solutions"
        email_message = f"""
Dear {visitor.visitor_name},

This is a friendly reminder about your scheduled appointment at Pinesphere Solutions.

🗓 Appointment Date: {visitor.appointment_date}
⏰ Appointment Time: {visitor.appointment_time.strftime('%H:%M')}

Please arrive on time. If you need to reschedule, contact us in advance.

Best Regards,  
Pinesphere Solutions
"""

        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,  # From email (set in settings.py)
            [visitor.visitor_email],
            fail_silently=False,
        )

    return f"Sent {len(upcoming_visitors)} reminders"







