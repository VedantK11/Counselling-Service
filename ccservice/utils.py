from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_booking_confirmation_email(booking):
    subject = 'Counseling Session Confirmation'
    context = {
        'user_name': booking.user.name,
        'counselor_name': booking.counselor.name,
        'date': booking.date,
        'time': booking.time,
    }
    html_message = render_to_string('emails/booking_confirmation.html', context)
    plain_message = render_to_string('emails/booking_confirmation.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.user.email],
        fail_silently=False,
    )

def send_reschedule_notification(booking, old_date, old_time):
    subject = 'Counseling Session Rescheduled'
    context = {
        'user_name': booking.user.name,
        'counselor_name': booking.counselor.name,
        'old_date': old_date,
        'old_time': old_time,
        'new_date': booking.date,
        'new_time': booking.time,
    }
    html_message = render_to_string('emails/session_rescheduled.html', context)
    plain_message = render_to_string('emails/session_rescheduled.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.user.email],
        fail_silently=False,
    )