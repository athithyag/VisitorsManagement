from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home, dashboard
from . import views
from django.contrib.auth.views import LogoutView,  LoginView
from .views import custom_logout_view, edit_profile
from .views import schedule_meets, approved_meets, rejected_meets, rescheduled_meets, approve_meet, reject_meet, reschedule_meet
from .views import reports
from .views import qr_scanner, generate_static_qr_code
from .views import password_reset_request, password_reset_confirm, password_reset_complete


urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.visitor_registration, name='visitor_registration'),
    path('forms/', views.forms, name='forms'), 
    path('get-next-visitor-id/', views.get_next_visitor_id, name='get_next_visitor_id'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'),  # Replace LoginView with your view
    path('profile/', views.profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/edit/<int:profile_id>/', edit_profile, name='edit_profile'),
    path('schedule/', schedule_meets, name='schedule_meets'),
    path('approved/', approved_meets, name='approved_meets'),
    path('rejected/', rejected_meets, name='rejected_meets'),
    path('rescheduled/', views.rescheduled_meets, name='rescheduled_meets'),
    path('approve-meet/<int:visitor_id>/', approve_meet, name='approve_meet'),
    path('reject-meet/<int:visitor_id>/', reject_meet, name='reject_meet'),
    path('reschedule-meet/<int:visitor_id>/', reschedule_meet, name='reschedule_meet'),
    path('rescheduled-meet/approve/<int:meet_id>/', views.approve_rescheduled_meet, name='approve_rescheduled_meet'),
    path('rescheduled-meet/reject/<int:meet_id>/', views.reject_rescheduled_meet, name='reject_rescheduled_meet'),
    path('reports/', views.reports, name='reports'),  # Add this line
    path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('generate_static_qr_code/', views.generate_static_qr_code, name='generate_static_qr_code'),

    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', password_reset_complete, name='password_reset_complete'),

]



  