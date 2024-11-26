from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CounselorProfile
from django.contrib.auth.decorators import login_required
from .models import CounselorProfile, BookingHistory, UserProfile, UserBookingHistory, CounselorRating
from django.db.models import Q, Value, CharField, When, Case, Avg, Count, F
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth import logout  
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import CareerField, Degree, Institution, JobRole
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import logging
import json


def index(request):
    return render(request, 'index.html')


def counsellor_login(request):
    if request.method == 'POST':
        username = request.POST.get('txtusername')
        password = request.POST.get('txtpassword')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                counselor_profile = CounselorProfile.objects.get(user=user)
                if counselor_profile:  
                    login(request, user)
                    return redirect('counsellorIndex')  
            except CounselorProfile.DoesNotExist:
                messages.error(request, "Profile not found. Please contact support.")
        else:
            messages.error(request, "Invalid Username or Password")
    
    return render(request, 'counsellorLogin.html')


def counselor_registration(request):
    if request.method == 'POST':
        name = request.POST.get('txtname', '').strip()
        email = request.POST.get('txtEmail', '').strip()
        phone = request.POST.get('txtnumber', '').strip()
        experience_str = request.POST.get('txtexperience', '').strip()
        address = request.POST.get('txtaddress', '').strip()
        username = request.POST.get('txtUsername', '').strip()
        password = request.POST.get('txtPassword', '')
        confirm_password = request.POST.get('txtConfirmPassword', '')

        if not all([name, email, phone, experience_str, address, username, password, confirm_password]):
            message = "All fields are required. Please fill in all the information."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        try:
            experience = int(experience_str)
            if experience < 0:
                raise ValueError
        except ValueError:
            message = "Experience must be a positive number."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        if not phone.isdigit() or len(phone) < 10:
            message = "Please enter a valid phone number."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        try:
            from django.core.validators import validate_email
            validate_email(email)
        except:
            message = "Please enter a valid email address."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        if User.objects.filter(username=username).exists():
            message = "Username already exists. Please choose a different username."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        if len(password) < 8:
            message = "Password must be at least 8 characters long."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        if password != confirm_password:
            message = "Passwords do not match. Please try again."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

        try:
            from django.db import transaction
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name
                )

                counselor_profile = CounselorProfile.objects.create(
                    user=user,
                    name=name,
                    email=email,
                    phone=phone,
                    experience=experience,
                    address=address,
                    booking_slots=json.dumps([])  
                )

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('counsellorLogin')

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Registration error: {str(e)}")
            
            message = "An error occurred during registration. Please try again."
            return render(request, 'counsellorRegistration.html', {'message': message, 'error': True})

    return render(request, 'counsellorRegistration.html')



@login_required
def counsellor_index(request):
    counselor_profile = CounselorProfile.objects.get(user=request.user)
    
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    client_name = request.GET.get('client_name', '')
    date_filter = request.GET.get('date_filter', '')
    status_filter = request.GET.get('status', '')
    
    bookings = counselor_profile.booking_history.all()
    
    if client_name:
        bookings = bookings.filter(client_name__icontains=client_name)
    
    if date_filter:
        if date_filter == 'today':
            bookings = bookings.filter(date=today)
        elif date_filter == 'week':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            bookings = bookings.filter(date__range=[week_start, week_end])
        elif date_filter == 'month':
            bookings = bookings.filter(date__year=today.year, date__month=today.month)
    
    if status_filter:
        if status_filter == 'scheduled':
            bookings = bookings.filter(
                Q(date__gt=today) |
                Q(date=today, time__gt=current_time)
            )
        elif status_filter == 'completed':
            bookings = bookings.filter(
                Q(date__lt=today) |
                Q(date=today, time__lt=current_time)
            )
        elif status_filter == 'cancelled':
            bookings = bookings.filter(status='cancelled')
    
    bookings = bookings.order_by('-date', '-time')
    
    available_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    selected_slots = counselor_profile.get_booking_slots()  

    return render(request, 'counsellorIndex.html', {
        'counselor_profile': counselor_profile,
        'bookings': bookings,
        'available_slots': available_slots,
        'selected_slots': selected_slots,  
        'today': today,
        'current_time': current_time,
    })

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                user_profile = UserProfile.objects.get(user=user)
                login(request, user)
                return redirect('studentIndex')
            except UserProfile.DoesNotExist:
                messages.error(request, "Profile not found. Please register first.")
        else:
            messages.error(request, "Invalid Username or Password")
    
    return render(request, 'studentLogin.html')

def student_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        city = request.POST.get('city')
        education = request.POST.get('education')
        occupation = request.POST.get('occupation')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'studentRegistration.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'studentRegistration.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'studentRegistration.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()

            UserProfile.objects.create(
                user=user,
                name=name,
                phone=phone,
                age=age,
                gender=gender,
                address=address,
                city=city,
                education=education,
                occupation=occupation
            )

            messages.success(request, "Registration successful! Please login.")
            return redirect('studentLogin')

        except Exception as e:
            messages.error(request, "An error occurred during registration")
            user.delete()  

    return render(request, 'studentRegistration.html')




@login_required
def student_index(request):
    user_profile = UserProfile.objects.get(user=request.user)
    bookings = user_profile.booking_history.all()
    
    search_query = request.GET.get('search', '')
    
    counselors = CounselorProfile.objects.all()
    
    if search_query:
        counselors = counselors.filter(
            Q(name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        ).distinct() 
    return render(request, 'studentIndex.html', {
        'user_profile': user_profile,
        'bookings': bookings,
        'counselors': counselors,
        'search_query': search_query
    })


@login_required
def get_counselor_slots(request, counselor_id):
    """AJAX view to get available slots for a specific date"""
    try:
        date_str = request.GET.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        counselor = CounselorProfile.objects.get(id=counselor_id)
        available_slots = counselor.get_available_slots(date)
        
        return JsonResponse({
            'slots': available_slots,
            'counselor_name': counselor.name
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
@login_required
def book_slot(request):
    """Handle slot booking"""
    try:
        counselor_id = request.POST.get('counselor_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        try:
            counselor = CounselorProfile.objects.get(id=counselor_id)
        except CounselorProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Selected counselor not found.'
            }, status=404)
        
        user_profile = UserProfile.objects.get(user=request.user)
        
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            booking_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date or time format.'
            })
        
        if booking_date < timezone.now().date():
            return JsonResponse({
                'success': False,
                'message': 'Cannot book slots for past dates.'
            })

        existing_booking = BookingHistory.objects.filter(
            counselor=counselor,
            date=booking_date,
            time=booking_time,
            status='scheduled'
        ).exists()

        if existing_booking:
            return JsonResponse({
                'success': False,
                'message': 'This slot has already been booked.'
            })
        
        with transaction.atomic():
            booking = BookingHistory.objects.create(
                counselor=counselor,
                client_name=user_profile.name,
                date=booking_date,
                time=booking_time,
                status='scheduled'
            )
            
            UserBookingHistory.objects.create(
                user=user_profile,
                counselor=counselor,
                date=booking_date,
                time=booking_time,
                status='scheduled'
            )

        return JsonResponse({
            'success': True,
            'message': 'Booking successful!',
            'booking_id': booking.id
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User profile not found.'
        }, status=404)
        
    except Exception as e:
        print(f"Booking error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while booking. Please try again.'
        }, status=400)

@login_required
def view_bookings(request):
    """View all bookings for the logged-in user"""
    user_profile = UserProfile.objects.get(user=request.user)
    bookings = user_profile.booking_history.all().order_by('date', 'time')
    
    return render(request, 'bookings.html', {
        'bookings': bookings
    })


@login_required
@require_POST
def cancel_booking(request, booking_id):
    try:
        user_booking = UserBookingHistory.objects.get(
            id=booking_id,
            user=request.user.userprofile,
            status='scheduled'
        )

        with transaction.atomic():
            user_booking.status = 'cancelled'
            user_booking.save()

            try:
                booking = BookingHistory.objects.get(
                    counselor=user_booking.counselor,
                    date=user_booking.date,
                    time=user_booking.time,
                    status='scheduled'
                )
                booking.status = 'cancelled'
                booking.save()
            except BookingHistory.DoesNotExist:
                pass

        return JsonResponse({
            'success': True,
            'message': 'Session cancelled successfully'
        })

    except UserBookingHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found or already cancelled'
        }, status=400)
    except Exception as e:
        print(f"Error cancelling booking: {str(e)}")  
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while cancelling the session'
        }, status=400)

@login_required
def verify_counselor_data(request):
    if not request.user.is_superuser:
        messages.error(request, "Unauthorized access")
        return redirect('index')
    
    bookings = BookingHistory.objects.all()
    invalid_bookings = []
    
    for booking in bookings:
        if not CounselorProfile.objects.filter(id=booking.counselor_id).exists():
            invalid_bookings.append(booking)
    
    for booking in invalid_bookings:
        booking.delete()
    
    messages.success(request, f"Cleaned up {len(invalid_bookings)} invalid bookings")
    return redirect('studentLogin')

@login_required
def verify_counselor_availability(request, counselor_id):
    try:
        counselor = CounselorProfile.objects.get(id=counselor_id)
        
        date_str = request.GET.get('date')
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        booked_slots = BookingHistory.objects.filter(
            counselor=counselor,
            date=booking_date,
            status='scheduled'
        ).values_list('time', flat=True)
        
        available_slots = counselor.get_booking_slots()
        
        available_slots = [
            slot for slot in available_slots 
            if datetime.strptime(slot, '%H:%M').time() not in booked_slots
        ]
        
        return JsonResponse({
            'success': True,
            'slots': available_slots
        })
        
    except CounselorProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Counselor not found'
        }, status=404)
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid date format'
        }, status=400)
    

@login_required
def get_counselor_bookings(request):
    try:
        counselor = CounselorProfile.objects.get(user=request.user)
        
        client_name = request.GET.get('client_name', '')
        date_filter = request.GET.get('date_filter', '')
        status_filter = request.GET.get('status', '')
        
        bookings = BookingHistory.objects.filter(counselor=counselor)
        
        if client_name:
            bookings = bookings.filter(client_name__icontains=client_name)
            
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        if date_filter:
            if date_filter == 'today':
                bookings = bookings.filter(date=today)
            elif date_filter == 'week':
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
                bookings = bookings.filter(date__range=[week_start, week_end])
            elif date_filter == 'month':
                bookings = bookings.filter(date__year=today.year, date__month=today.month)
        
        if status_filter:
            if status_filter == 'scheduled':
                bookings = bookings.filter(
                    Q(date__gt=today) |
                    Q(date=today, time__gt=current_time)
                )
            elif status_filter == 'completed':
                bookings = bookings.filter(
                    Q(date__lt=today) |
                    Q(date=today, time__lt=current_time)
                )
            elif status_filter == 'cancelled':
                bookings = bookings.filter(status='cancelled')
        
        bookings = bookings.annotate(
            current_status=Case(
                When(status='cancelled', then=Value('cancelled')),
                When(date__lt=today, then=Value('completed')),
                When(date=today, time__lt=current_time, then=Value('completed')),
                default=Value('scheduled'),
                output_field=CharField(),
            )
        ).order_by('-date', '-time')
        
        return JsonResponse({
            'success': True,
            'bookings': list(bookings.values())
        })
        
    except Exception as e:
        print(f"Error in get_counselor_bookings: {str(e)}")  
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

    
@login_required
def counsellor_index(request):
    counselor_profile = CounselorProfile.objects.get(user=request.user)
    
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    bookings = BookingHistory.objects.filter(counselor=counselor_profile).annotate(
        current_status=Case(
            When(date__gt=timezone.now().date(), then=Value('scheduled')),
            When(date=timezone.now().date(), time__gt=timezone.now().time(), then=Value('scheduled')),
            When(status='cancelled', then=Value('cancelled')),
            default=Value('completed'),
            output_field=CharField(),
        )
    ).order_by('-date', '-time')

    available_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    if request.method == 'POST':
        try:
            slots = request.POST.getlist('slots[]')
            counselor_profile.set_booking_slots(slots)
            counselor_profile.save()
            messages.success(request, "Booking slots updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating slots: {str(e)}")

    selected_slots = counselor_profile.get_booking_slots()
    print(f"Selected slots: {selected_slots}")  

    return render(request, 'counsellorIndex.html', {
        'counselor_profile': counselor_profile,
        'bookings': bookings,
        'available_slots': available_slots,
        'selected_slots': selected_slots,
        'today': today,
        'current_time': current_time,
    })

@login_required
def get_booking_details(request, booking_id):
    try:
        counselor = CounselorProfile.objects.get(user=request.user)
        booking = BookingHistory.objects.get(id=booking_id, counselor=counselor)
        
        user_booking = UserBookingHistory.objects.filter(
            counselor=counselor,
            date=booking.date,
            time=booking.time
        ).select_related('user').first()
        
        if not user_booking:
            return JsonResponse({
                'success': False,
                'message': 'Booking details not found'
            }, status=404)

        booking_data = {
            'id': booking.id,
            'client_name': booking.client_name,
            'client_email': user_booking.user.user.email,
            'client_phone': user_booking.user.phone,
            'client_education': user_booking.user.education,
            'client_age': user_booking.user.age,
            'date': booking.date,
            'time': booking.time,
            'status': booking.status
        }
        
        return JsonResponse({
            'success': True,
            'booking': booking_data
        })
    except BookingHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_booking_details: {str(e)}")  
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while fetching booking details'
        }, status=500)
    

@login_required
def debug_slots(request):
    counselor_profile = CounselorProfile.objects.get(user=request.user)
    raw_slots = counselor_profile.booking_slots
    parsed_slots = counselor_profile.get_booking_slots()
    
    return JsonResponse({
        'raw_slots': raw_slots,
        'parsed_slots': parsed_slots
    })

@login_required
@require_POST
def update_counselor_slots(request):
    try:
        counselor_profile = CounselorProfile.objects.get(user=request.user)
        slots = request.POST.getlist('slots[]')
        
        if not slots:
            return JsonResponse({
                'success': False,
                'message': 'Please select at least one slot'
            })
            
        valid_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", 
                      "14:00", "15:00", "16:00", "17:00"]
        if not all(slot in valid_slots for slot in slots):
            return JsonResponse({
                'success': False,
                'message': 'Invalid slot selection'
            })

        counselor_profile.set_booking_slots(slots)
        counselor_profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Slots updated successfully',
            'slots': slots  
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
    
@login_required
@require_POST
def cancel_counselor_booking(request, booking_id):
    try:
        with transaction.atomic():
            counselor = CounselorProfile.objects.get(user=request.user)
            booking = BookingHistory.objects.get(id=booking_id, counselor=counselor)
            
            booking.status = 'cancelled'
            booking.save()
            
            user_booking = UserBookingHistory.objects.get(
                counselor=counselor,
                date=booking.date,
                time=booking.time
            )
            user_booking.status = 'cancelled'
            user_booking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking cancelled successfully'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    


@login_required
@require_POST
def update_counselor_settings(request):
    try:
        counselor = CounselorProfile.objects.get(user=request.user)
        user = request.user
        password_changed = False  
        
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        experience = request.POST.get('experience')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not phone or not address or not experience:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            })
        
        counselor.phone = phone
        counselor.address = address
        counselor.experience = experience
        
        if new_password:
            if not current_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is required to set a new password.'
                })
            
            if not user.check_password(current_password):
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is incorrect.'
                })
                
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'New passwords do not match.'
                })
            
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False,
                    'message': 'Password must be at least 8 characters long.'
                })
            
            user.set_password(new_password)
            user.save()
            password_changed = True 
        
        counselor.save()
        
        if password_changed:
            logout(request)
            return JsonResponse({
                'success': True,
                'message': 'Settings updated successfully. Please log in with your new password.',
                'redirect': True,
                'redirect_url': '/counsellorLogin/'  
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Settings updated successfully',
                'redirect': False
            })
        
    except Exception as e:
        print(f"Error updating settings: {str(e)}")  
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while updating settings.'
        }, status=500)


from django.contrib.auth import logout

@login_required
@require_POST
def update_student_settings(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user = request.user
        password_changed = False
        
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        education = request.POST.get('education')
        address = request.POST.get('address')
        city = request.POST.get('city')
        occupation = request.POST.get('occupation')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not all([phone, age, education, address, city]):
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            })
        
        user_profile.phone = phone
        user_profile.age = age
        user_profile.education = education
        user_profile.address = address
        user_profile.city = city
        user_profile.occupation = occupation
        
        if new_password:
            if not current_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is required to set a new password.'
                })
            
            if not user.check_password(current_password):
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is incorrect.'
                })
                
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'New passwords do not match.'
                })
            
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False,
                    'message': 'Password must be at least 8 characters long.'
                })
            
            user.set_password(new_password)
            user.save()
            password_changed = True
        
        user_profile.save()
        
        if password_changed:
            logout(request)
            return JsonResponse({
                'success': True,
                'message': 'Settings updated successfully. Please log in with your new password.',
                'redirect': True,
                'redirect_url': '/studentLogin/'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Settings updated successfully',
                'redirect': False
            })
        
    except Exception as e:
        print(f"Error updating settings: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while updating settings.'
        }, status=500)
    



logger = logging.getLogger(__name__)

def career(request):
    """Main career listing view"""
    search_query = request.GET.get('search', '')
    has_colleges = request.GET.get('has_colleges', '')
    
    career_fields = CareerField.objects.all().prefetch_related(
        'degrees',
        'degrees__institutions',
        'job_roles'
    ).annotate(
        college_count=Count('degrees__institutions', distinct=True)
    ).order_by('name')  
    
    if search_query:
        career_fields = career_fields.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if has_colleges == 'yes':
        career_fields = career_fields.filter(college_count__gt=0)
    
    paginator = Paginator(career_fields, 9)
    page = request.GET.get('page', 1)
    career_fields = paginator.get_page(page)
    
    context = {
        'career_fields': career_fields,
        'search_query': search_query,
        'has_colleges': has_colleges,
    }
    return render(request, 'career.html', context)

def career_field_detail(request, slug):
    """Detailed career field view"""
    career_field = get_object_or_404(CareerField, slug=slug)
    
    degrees = career_field.degrees.all()
    job_roles = career_field.job_roles.all()  
    institutions = Institution.objects.filter(
        degrees__career_field=career_field
    ).distinct().order_by('ranking')

    print(f"Career Field: {career_field.name}")
    print(f"Number of job roles: {job_roles.count()}")
    for role in job_roles:
        print(f"Job Role: {role.title}")
    
    context = {
        'career_field': career_field,
        'degrees': degrees,
        'job_roles': job_roles,
        'institutions': institutions,
        'total_colleges': institutions.count(),
    }
    
    return render(request, 'career_field_detail.html', context)


def career_colleges(request, slug):
    """View for all colleges in a career field"""
    career_field = get_object_or_404(CareerField, slug=slug)
    
    institutions = Institution.objects.filter(
        degrees__career_field=career_field
    ).distinct().order_by('ranking')
    
    total_count = institutions.count()
    
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
        
    paginator = Paginator(institutions, 20)
    
    try:
        institutions = paginator.page(page_number)
    except PageNotAnInteger:
        institutions = paginator.page(1)
    except EmptyPage:
        institutions = paginator.page(paginator.num_pages)
    
    print(f"Total institutions: {total_count}")
    print(f"Current page: {page_number}")
    print(f"Items on current page: {len(institutions)}")
    
    context = {
        'career_field': career_field,
        'institutions': institutions,
        'total_colleges': total_count,
        'current_page': page_number,
        'total_pages': paginator.num_pages
    }
    
    return render(request, 'career_colleges.html', context)

def college_detail(request, id):
    """Detailed view for a specific college"""
    institution = get_object_or_404(Institution, id=id)
    
    context = {
        'institution': institution,
        'degrees': institution.degrees.all().select_related('career_field'),
        'career_fields': CareerField.objects.filter(degrees__institutions=institution).distinct(),
        'nirf_ranking': {
            'rank': institution.ranking,
            'score': institution.nirf_score,
            'year': institution.nirf_ranking_year
        }
    }
    
    return render(request, 'college_detail.html', context)

def institution_detail(request, id):
    """Detailed view for a specific institution"""
    
    institution = get_object_or_404(Institution.objects.prefetch_related(
        'degrees__career_field'
    ), id=id)
    
    context = {
        'institution': institution,
        'degrees': institution.degrees.all().order_by('name'),
        'nirf_scores': {
            'Overall': institution.nirf_score,
            'Teaching': institution.teaching_score,
            'Research': institution.research_score,
            'Infrastructure': institution.infrastructure_score,
            'Placement': institution.placement_score
        }
    }
    
    return render(request, 'institution_detail.html', context)

def college_rankings(request):
    """View for displaying college rankings across all fields"""
    
    career_field = request.GET.get('field', '')
    state = request.GET.get('state', '')
    rank_range = request.GET.get('rank_range', '')
    
    institutions = Institution.objects.all().select_related().prefetch_related('degrees__career_field')
    
    if career_field:
        institutions = institutions.filter(degrees__career_field__name=career_field)
    
    if state:
        institutions = institutions.filter(location__icontains=state)
        
    if rank_range:
        if rank_range == '1-50':
            institutions = institutions.filter(ranking__lte=50)
        elif rank_range == '51-100':
            institutions = institutions.filter(ranking__gt=50, ranking__lte=100)
        elif rank_range == '101-200':
            institutions = institutions.filter(ranking__gt=100, ranking__lte=200)
    
    institutions = institutions.order_by('ranking')
    
    states = Institution.objects.values_list('location', flat=True).distinct()
    career_fields = CareerField.objects.all()
    
    paginator = Paginator(institutions, 20) 
    page = request.GET.get('page')
    institutions = paginator.get_page(page)
    
    context = {
        'institutions': institutions,
        'states': states,
        'career_fields': career_fields,
        'selected_field': career_field,
        'selected_state': state,
        'selected_rank_range': rank_range,
    }
    
    return render(request, 'college_rankings.html', context)
