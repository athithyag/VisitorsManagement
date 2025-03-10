from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from .models import Visitor, VisitorSchedule, Profile, RescheduledMeet
from django.conf import settings
from django.contrib.auth import logout
from .forms import ProfileForm, VisitorForm, RescheduleMeetForm
from myapp.models import VisitorSchedule
import qrcode
from django.contrib import messages
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.views.decorators.cache import cache_control
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils.dateparse import parse_time

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 





def home(request):
    return render(request, 'home.html') 



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def dashboard(request):
    # Get the names of groups the user belongs to
    user_groups = request.user.groups.values_list('name', flat=True)
    
    # Pass the group data to the template
    context = {
        'user_groups': user_groups,
    }
    return render(request, 'dashboard.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def visitor_registration(request):
    success = False  # Flag to show success notification 

    if request.method == 'POST':
        # Get form data
        visitor_name = request.POST.get('visitor_name')
        visitor_email = request.POST.get('visitor_email')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        document = request.FILES.get('document')
        designated_attendee = request.POST.get('designated_attendee')

        # Ensure unique visitor ID
        last_visitor = Visitor.objects.order_by('-visitor_id').first()
        next_visitor_id = last_visitor.visitor_id + 1 if last_visitor else 101

        try:
            # Validate appointment date
            appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            today = datetime.today().date()
            max_date = today + timedelta(days=10)

            if appointment_date_obj < today or appointment_date_obj > max_date:
                messages.error(request, 'Appointment date must be between today and the next 10 days.')
                return redirect('visitor_registration')

            # Validate appointment time
            appointment_time_obj = datetime.strptime(appointment_time, '%H:%M').time()
            if appointment_time_obj < datetime.strptime('09:00', '%H:%M').time() or appointment_time_obj > datetime.strptime('18:00', '%H:%M').time():
                messages.error(request, 'Appointment time must be between 09:00 AM and 06:00 PM.')
                return redirect('visitor_registration')

            # Send email to the designated attendee
            attendee_email_mapping = {
                'Member 1': 'athithyag24@gmail.com',
                'Member 2': 'athithyag24@gmail.com',
                'General': 'athithyag24@gmail.com',
            }
            attendee_email = attendee_email_mapping.get(designated_attendee)

            if attendee_email:
                try:
                    attendee_subject = f'New Visitor Scheduled - {visitor_name}'
                    attendee_message = f"""
Dear Team,

A new visitor Appointment has been scheduled. Below are the details of the visitor's appointment:

Visitor Name: {visitor_name}
Appointment Date: {appointment_date}
Appointment Time: {appointment_time}
Reason: {request.POST.get('reason')}

Please ensure all necessary arrangements are made to facilitate the visitor's appointment.

Best Regards,
Pinesphere Solutions
"""
                    send_mail(
                        attendee_subject,
                        attendee_message,
                        settings.EMAIL_HOST_USER,
                        [attendee_email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email to attendee: {e}")
                    messages.error(request, 'There was an issue notifying the designated attendee.')

            # Ensure unique visitor ID
            while Visitor.objects.filter(visitor_id=next_visitor_id).exists():
                next_visitor_id += 1

            # Save visitor data to the database
            new_visitor = Visitor(
                visitor_id=next_visitor_id,
                visitor_name=visitor_name,
                visitor_email=visitor_email,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                document=document,
                category=request.POST.get('category'),
                reason=request.POST.get('reason'),
                designated_attendee=designated_attendee,
            )
            new_visitor.save()

            # Email content for visitor
            email_subject = 'Visitor Registration Successful - Pinesphere Solutions'
            email_message = f"""
Dear {visitor_name},

Thank you for registering as a visitor with Pinesphere Solutions. Below are the details of your scheduled appointment:

Your appointment has been successfully scheduled as follows:

Appointment Date: {appointment_date}
Appointment Time: {appointment_time}

If you need to reschedule your appointment, please click the link below:
Reschedule Your Appointment: http://127.0.0.1:8000/reschedule-meet/{new_visitor.id}/

We look forward to welcoming you to our office.

Best Regards,
Pinesphere Solutions
"""

            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [visitor_email],
                fail_silently=False,
            )

            # Create a corresponding VisitorSchedule object
            VisitorSchedule.objects.create(visitor=new_visitor, designated_attendee=designated_attendee)

            success = True
            # messages.success(request, 'Visitor registration successful!')

        except ValueError:
            messages.error(request, 'Invalid date or time format.')
            return redirect('visitor_registration')

    return render(request, 'home.html', {'success': success})





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def forms(request):
      
    # Get the names of groups the user belongs to
    user_groups = request.user.groups.values_list('name', flat=True)

    # Fetch all visitors ordered by ID 
    visitors_list = Visitor.objects.all().order_by('id')
    
    # Get the number of entries per page from the request or default to 10
    entries_per_page = int(request.GET.get('entries', 10))
    paginator = Paginator(visitors_list, entries_per_page)
    
    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Pass the paginated data to the template
    context = {
        'page_obj': page_obj,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count,
        'user_groups': user_groups,
    }
    return render(request, 'forms.html', context)


 


def get_next_visitor_id(request):
    last_visitor = Visitor.objects.order_by('-visitor_id').first()
    next_visitor_id = last_visitor.visitor_id + 1 if last_visitor else 101
    return JsonResponse({'next_visitor_id': next_visitor_id})




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def profile(request):
    # Get the names of groups the user belongs to
    user_groups = request.user.groups.values_list('name', flat=True)

    # Fetch all profile data
    profiles = Profile.objects.all()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the form data to the model
            return redirect('profile')  # Redirect to the dashboard after saving

    else:
        form = ProfileForm()  # Initialize a new empty form

    return render(request, 'profile.html', {
        'user': request.user,
        'form': form,
        'profiles': profiles,
        'user_groups': user_groups
    })




def edit_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})
                                                                                                    




    profiles = Profile.objects.all()
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm()

    return render(request, 'dashboard.html', {'profiles': profiles, 'form': form})


# Function to check if the user is in the "Team" group
def is_team_member(user):
    return user.is_authenticated and user.groups.filter(name="Team").exists()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_team_member)
def schedule_meets(request):
    user_groups = request.user.groups.values_list('name', flat=True)

    pending_meets_list = VisitorSchedule.objects.filter(status='Pending')

    # Filter based on the logged-in user's designated role
    if "team1" in user_groups:
        pending_meets_list = pending_meets_list.filter(designated_attendee="Member 1")
    elif "team2" in user_groups:
        pending_meets_list = pending_meets_list.filter(designated_attendee="Member 2")
    elif "general" in user_groups:  # Adding general user filter
        pending_meets_list = pending_meets_list.filter(designated_attendee="General")   
        

    pending_meets_list = pending_meets_list.order_by('-id') 

    entries_per_page = int(request.GET.get('entries', 10))
    paginator = Paginator(pending_meets_list, entries_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count,
        'user_groups': user_groups,
    }
    return render(request, 'schedule.html', context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_team_member)
def approved_meets(request):

    user_groups = request.user.groups.values_list('name', flat=True)

    # Filter and order the approved meetings by 'id'
    approved_meets_queryset = VisitorSchedule.objects.filter(status='Approved').order_by('-id')

    
    # Filter based on the logged-in user's designated role
    if "team1" in user_groups:
        approved_meets_queryset = approved_meets_queryset.filter(designated_attendee="Member 1")
    elif "team2" in user_groups:
        approved_meets_queryset = approved_meets_queryset.filter(designated_attendee="Member 2")
    elif "general" in user_groups:  # Adding general user filter
        approved_meets_queryset = approved_meets_queryset.filter(designated_attendee="General")

    # Get the number of entries per page from the query parameters (default to 10)
    entries_per_page = int(request.GET.get('entries', 10))

    # Use Django's Paginator to paginate the queryset
    paginator = Paginator(approved_meets_queryset, entries_per_page)

    # Get the current page number from the query parameters (default to 1)
    page_number = request.GET.get('page', 1)

    # Get the current page's data
    page_obj = paginator.get_page(page_number)

    # Pass the page object and other data to the template
    context = {
        'approved_meets': page_obj,  # Paginated data
        'page_obj': page_obj,  # For pagination controls
        'entries_per_page': entries_per_page,  # Current entries per page
        'total_entries': paginator.count,  # Total number of entries
        'user_groups': user_groups,  # User groups
    }

    return render(request, 'approved.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_team_member)
def rejected_meets(request):

    user_groups = request.user.groups.values_list('name', flat=True)


    # Fetch all rejected meets and order by 'id'
    rejected_meets_list = VisitorSchedule.objects.filter(status='Rejected').order_by('-id')

    # Filter based on the logged-in user's designated role
    if "team1" in user_groups:
        rejected_meets_list = rejected_meets_list.filter(designated_attendee="Member 1")
    elif "team2" in user_groups:
        rejected_meets_list = rejected_meets_list.filter(designated_attendee="Member 2")
    elif "general" in user_groups:  # Adding general user filter
        rejected_meets_list = rejected_meets_list.filter(designated_attendee="General")
    
    # Get the number of entries per page from the request or default to 10
    entries_per_page = int(request.GET.get('entries', 10))
    paginator = Paginator(rejected_meets_list, entries_per_page)
    
    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Pass the data to the template
    context = {
        'page_obj': page_obj,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count,
        'user_groups': user_groups,
    }
    return render(request, 'rejected.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_team_member)
def rescheduled_meets(request):

    user_groups = request.user.groups.values_list('name', flat=True)


    # Fetch all rescheduled meets and order by 'id'
    rescheduled_meets_list = VisitorSchedule.objects.filter(status='Rescheduled').order_by('-id')

    # Filter based on the logged-in user's designated role
    if "team1" in user_groups:
        rescheduled_meets_list = rescheduled_meets_list.filter(designated_attendee="Member 1")
    elif "team2" in user_groups:
        rescheduled_meets_list = rescheduled_meets_list.filter(designated_attendee="Member 2")
    elif "general" in user_groups:  # Adding general user filter
        rescheduled_meets_list = rescheduled_meets_list.filter(designated_attendee="General")
    
    # Get the number of entries per page from the request or default to 10
    entries_per_page = int(request.GET.get('entries', 10))
    paginator = Paginator(rescheduled_meets_list, entries_per_page)
    
    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Pass the data to the template
    context = {
        'page_obj': page_obj,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count,
        'user_groups': user_groups,
    }
    return render(request, 'rescheduled.html', context)


def approve_meet(request, visitor_id):
    # Get the visitor schedule by ID
    visitor_schedule = get_object_or_404(VisitorSchedule, visitor_id=visitor_id)
    
    # Set the status to 'Approved'
    visitor_schedule.status = 'Approved'
    visitor_schedule.save()

    # Generate and save the verification code
    visitor_schedule.generate_verification_code()

    # Generate the reschedule link
    reschedule_link = f'http://127.0.0.1:8000/reschedule-meet/{visitor_schedule.visitor.id}/'

    # Send email to the visitor with the verification code and reschedule link
    email_subject = 'Your Meeting Request Has Been Approved - Pinesphere Solutions'
    email_message = f"""
Hello {visitor_schedule.visitor.visitor_name},

We are pleased to inform you that your meeting request has been approved. Below are the details of your scheduled appointment:

Appointment Date: {visitor_schedule.visitor.appointment_date}
Appointment Time: {visitor_schedule.visitor.appointment_time}
Designated Attendee: {visitor_schedule.visitor.designated_attendee}

To ensure a smooth check-in process, please scan the verification code provided below at the reception:
Verification Code: {visitor_schedule.verification_code}

If you need to reschedule your appointment, please use the following link:
Reschedule Your Appointment : {reschedule_link}

Thank you for choosing Pinesphere Solutions. We look forward to welcoming you.

Best Regards,
Pinesphere Solutions
"""

    send_mail(
        email_subject,
        email_message,
        settings.DEFAULT_FROM_EMAIL,  # From email (set in settings.py)
        [visitor_schedule.visitor.visitor_email],  # To email
        fail_silently=False,
    )

    # Redirect to the schedule meets page
    return redirect('approved_meets')




def reject_meet(request, visitor_id):
    visitor_schedule = get_object_or_404(VisitorSchedule, visitor_id=visitor_id)
    visitor_schedule.status = 'Rejected'
    visitor_schedule.save()

     # Send email to the visitor with the verification code and reschedule link
    email_subject = 'Regarding Your Visit Request - Pinesphere Solutions'
    email_message = f"""
Dear {visitor_schedule.visitor.visitor_name},

We appreciate your interest in visiting Pinesphere Solutions. After careful consideration, we regret to inform you that your visit request has not been approved at this time.

Unfortunately, due to scheduling conflicts, we are unable to accommodate your request.

We apologize for any inconvenience this may cause and encourage you to reach out to us should you have any questions or require further clarification.

Thank you for your understanding.

Best Regards,
Pinesphere Solutions
"""

    send_mail(
        email_subject,
        email_message,
        settings.DEFAULT_FROM_EMAIL,  # From email (set in settings.py)
        [visitor_schedule.visitor.visitor_email],  # To email
        fail_silently=False,
    )

    return redirect('rejected_meets')




from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse

def reschedule_meet(request, visitor_id):
    visitor_schedule = get_object_or_404(VisitorSchedule, visitor_id=visitor_id)
    if request.method == 'POST':
        form = RescheduleMeetForm(request.POST, instance=visitor_schedule.visitor)
        if form.is_valid():
            # Update visitor appointment date and time
            visitor_schedule.visitor.appointment_date = form.cleaned_data['appointment_date']
            visitor_schedule.visitor.appointment_time = form.cleaned_data['appointment_time']
            visitor_schedule.visitor.save()

            # Update visitor schedule status and reschedule details
            visitor_schedule.status = 'Rescheduled'
            visitor_schedule.rescheduled_date = form.cleaned_data['appointment_date']
            visitor_schedule.rescheduled_time = form.cleaned_data['appointment_time']
            visitor_schedule.save()

            if request.user.groups.values_list('name', flat=True):
                return JsonResponse({
                    'redirect': True,
                    'url': reverse('rescheduled_meets'),  # Use URL name 'rescheduled_meets'
                    'message': 'The meeting has been rescheduled successfully.',
                    'status': 'success'
                })
            else:  # User logic
                return JsonResponse({
                    'message': 'The meeting has been rescheduled successfully.',
                    'status': 'success'
                })
    else:
        form = RescheduleMeetForm(instance=visitor_schedule.visitor)
    
    return render(request, 'reschedule.html', {'form': form, 'visitor_schedule': visitor_schedule})





def approve_rescheduled_meet(request, meet_id):
    if request.method == "POST":
        meet = get_object_or_404(RescheduledMeet, id=meet_id)
        meet.status = 'approved'  # Update status to approved
        meet.save()
        messages.success(request, "The rescheduled meet has been approved.")
    return redirect('rescheduled_meets')

def reject_rescheduled_meet(request, meet_id):
    if request.method == "POST":
        meet = get_object_or_404(RescheduledMeet, id=meet_id)
        meet.status = 'rejected'  # Update status to rejected
        meet.save()
        messages.error(request, "The rescheduled meet has been rejected.")
    return redirect('rescheduled_meets')


 

def generate_static_qr_code(request):
    # Static URL for the QR Scanner form
    qr_scanner_url = request.build_absolute_uri('/qr-scanner/')

    # Generate the QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_scanner_url)
    qr.make(fit=True)

    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Serve the image as an HTTP response
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    response['Content-Disposition'] = 'attachment; filename="office_qr_code.png"'
    return response





def qr_scanner(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        out_time = request.POST.get('out_time')  # Get out_time if provided

        try:
            # Try to fetch the visitor schedule by the verification code
            visitor_schedule = VisitorSchedule.objects.get(verification_code=verification_code, status='Approved')
            
            # If in_time is not set, set it to the current time
            if not visitor_schedule.in_time:
                visitor_schedule.in_time = now()  # Automatically set in_time to current time
                visitor_schedule.save()
                
            # If out_time is provided, update it as well
            if out_time:
                visitor_schedule.out_time = out_time
                visitor_schedule.save()

            # Return the in_time and out_time back to the frontend
            return JsonResponse({
                'message': 'In time recorded successfully!',
                'status': 'success',
                'in_time': visitor_schedule.in_time.strftime('%H:%M')  # Format the in_time as 'HH:MM'
            })

        except VisitorSchedule.DoesNotExist:
            return JsonResponse({'message': 'Invalid verification code.', 'status': 'error'})
    
    # Pre-fill the verification code if it exists in the query string
    verification_code = request.GET.get('verification_code', '')
    return render(request, 'qr_form.html', {'verification_code': verification_code})






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_team_member)
def reports(request):

    user_groups = request.user.groups.values_list('name', flat=True)


    approved_visitors_list = VisitorSchedule.objects.filter(status='Approved').order_by('id')

    # Filter based on the logged-in user's designated role
    if "team1" in user_groups:
        approved_visitors_list = approved_visitors_list.filter(designated_attendee="Member 1")
    elif "team2" in user_groups:
        approved_visitors_list = approved_visitors_list.filter(designated_attendee="Member 2")
    elif "general" in user_groups:  # Adding general user filter
        approved_visitors_list = approved_visitors_list.filter(designated_attendee="General")
    
    # Pagination setup
    entries_per_page = int(request.GET.get('entries', 10))  # Default 10 entries per page
    paginator = Paginator(approved_visitors_list, entries_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

   # Format `in_time` and `out_time` for all visitors in the current page
    for visitor in page_obj:
      visitor.in_time = visitor.in_time.strftime('%H:%M') if visitor.in_time else ""
      visitor.out_time = visitor.out_time.strftime('%H:%M') if visitor.out_time else ""


    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        feedback = request.POST.get('feedback', '')
        out_time = request.POST.get('out_time', '')

        try:
            visitor_schedule = VisitorSchedule.objects.get(id=schedule_id)

            if out_time:
                try:
                    out_time_obj = datetime.strptime(out_time, '%H:%M').time()
                    in_time_obj = datetime.combine(datetime.today(), visitor_schedule.in_time)
                    out_time_obj = datetime.combine(datetime.today(), out_time_obj)

                    if out_time_obj < in_time_obj:
                        out_time_obj += timedelta(days=1)

                    visitor_schedule.out_time = out_time_obj.time()
                    visitor_schedule.total_duration = out_time_obj - in_time_obj
                    visitor_schedule.save()
                except ValueError as ve:
                    print(f"Invalid time format for out_time: {out_time}. Error: {ve}")

            visitor_schedule.feedback = feedback
            visitor_schedule.save()
        except VisitorSchedule.DoesNotExist:
            print(f"VisitorSchedule with ID {schedule_id} does not exist.")
        except Exception as e:
            print(f"Error updating VisitorSchedule: {e}")

    return render(
        request,
        'reports.html',
        {'page_obj': page_obj, 'entries_per_page': entries_per_page, 'total_entries': paginator.count, 'user_groups': user_groups}
    )



def validate_file_size(value):
    max_size = 2 * 1024 * 1024  # 2 MB in bytes
    if value.size > max_size:
        raise ValidationError('File size should not exceed 2 MB.')   
    




def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
            )
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
    return render(request, 'myapp/password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('password_reset_complete')
        return render(request, 'myapp/password_reset_confirm.html')
    else:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password_reset_request')

def password_reset_complete(request):
    return render(request, 'myapp/password_reset_complete.html')

