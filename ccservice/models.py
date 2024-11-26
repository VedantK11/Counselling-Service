
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.utils import timezone
import json


# class CounselorProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=False)
#     phone = models.CharField(max_length=15)
#     experience = models.IntegerField()
#     address = models.TextField()
#     city = models.CharField(max_length=100,default="Mumbai") 
#     booking_slots = models.TextField(blank=True, default=json.dumps([]))

#     def clean(self):
#         if self.experience < 0:
#             raise ValidationError({'experience': _('Experience years cannot be negative.')})
        
#         if not self.phone.isdigit() or len(self.phone) < 10:
#             raise ValidationError({'phone': _('Please enter a valid phone number.')})
        
#         try:
#             slots = json.loads(self.booking_slots)
#             if not isinstance(slots, list):
#                 raise ValidationError({'booking_slots': _('Invalid booking slots format.')})
#         except json.JSONDecodeError:
#             raise ValidationError({'booking_slots': _('Invalid booking slots format.')})

#     def get_booking_slots(self):
#         try:
#             return json.loads(self.booking_slots)
#         except json.JSONDecodeError:
#             return []

#     def set_booking_slots(self, slots):
#         if not isinstance(slots, list):
#             slots = list(slots)
#         self.booking_slots = json.dumps(slots)


#     def get_available_slots(self, date=None):
#         """Get available slots for a specific date"""
#         booked_slots = BookingHistory.objects.filter(
#             counselor=self,
#             date=date,
#             status='scheduled'
#         ).values_list('time', flat=True)
        
#         all_slots = self.get_booking_slots()
#         available_slots = []
        
#         for slot in all_slots:
#             slot_time = datetime.strptime(slot, '%H:%M').time()
#             if slot_time not in booked_slots:
#                 available_slots.append(slot)
        
#         return available_slots

#     def get_available_dates(self):
#         """Get available dates for next month"""
#         today = datetime.now().date()
#         next_month = today + timedelta(days=30)
#         dates = []
        
#         current = today
#         while current <= next_month:
#             if self.get_available_slots(current):
#                 dates.append(current)
#             current += timedelta(days=1)
        
#         return dates

    
#     def __str__(self):
#         return f"{self.name} ({self.user.username})"

#     class Meta:
#         verbose_name = "Counselor Profile"
#         verbose_name_plural = "Counselor Profiles"

class CounselorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=15)
    experience = models.IntegerField()
    address = models.TextField()
    city = models.CharField(max_length=100, default="Mumbai")
    booking_slots = models.TextField(blank=True, default=json.dumps([]))

    def clean(self):
        if self.experience < 0:
            raise ValidationError({'experience': _('Experience years cannot be negative.')})
        
        if not self.phone.isdigit() or len(self.phone) < 10:
            raise ValidationError({'phone': _('Please enter a valid phone number.')})
        
        try:
            slots = json.loads(self.booking_slots)
            if not isinstance(slots, list):
                raise ValidationError({'booking_slots': _('Invalid booking slots format.')})
            # Additional validation for slot format
            for slot in slots:
                try:
                    datetime.strptime(slot, '%H:%M')
                except ValueError:
                    raise ValidationError({'booking_slots': _(f'Invalid time format in slot: {slot}')})
        except json.JSONDecodeError:
            raise ValidationError({'booking_slots': _('Invalid booking slots format.')})

    def get_booking_slots(self):
        """
        Get all configured booking slots
        Returns an empty list if slots are invalid
        """
        try:
            slots = json.loads(self.booking_slots)
            return sorted(slots) if isinstance(slots, list) else []
        except json.JSONDecodeError:
            return []

    def set_booking_slots(self, slots):
        """
        Set booking slots with validation
        Args:
            slots: List or iterable of time slots in "HH:MM" format
        """
        if not isinstance(slots, list):
            slots = list(slots)
        
        # Validate time format
        valid_slots = []
        for slot in slots:
            try:
                datetime.strptime(slot, '%H:%M')
                valid_slots.append(slot)
            except ValueError:
                continue
        
        self.booking_slots = json.dumps(sorted(valid_slots))
        
    def get_available_slots(self, date=None):
        """
        Get available slots for a specific date
        Args:
            date: Date to check availability for (defaults to today)
        Returns:
            List of available time slots
        """
        if date is None:
            date = datetime.now().date()
            
        # Get booked slots for the date
        booked_slots = BookingHistory.objects.filter(
            counselor=self,
            date=date,
            status='scheduled'
        ).values_list('time', flat=True)
        
        # Get all configured slots
        all_slots = self.get_booking_slots()
        available_slots = []
        
        # Current time for today's slots
        current_time = datetime.now().time() if date == datetime.now().date() else None
        
        for slot in all_slots:
            slot_time = datetime.strptime(slot, '%H:%M').time()
            # Skip past slots for today
            if current_time and date == datetime.now().date() and slot_time <= current_time:
                continue
            if slot_time not in booked_slots:
                available_slots.append(slot)
        
        return sorted(available_slots)

    def get_available_dates(self, days_ahead=30):
        """
        Get available dates for the specified number of days ahead
        Args:
            days_ahead: Number of days to look ahead (default 30)
        Returns:
            List of dates with available slots
        """
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        dates = []
        
        current = today
        while current <= end_date:
            if self.get_available_slots(current):
                dates.append(current)
            current += timedelta(days=1)
        
        return dates

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        verbose_name = "Counselor Profile"
        verbose_name_plural = "Counselor Profiles"

    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    education = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class UserBookingHistory(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="booking_history")
    counselor = models.ForeignKey('CounselorProfile', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')
    
    def __str__(self):
        return f"{self.user.name} - {self.counselor.name} - {self.date}"
    
    class Meta:
        verbose_name_plural = "User Booking Histories"

class BookingHistory(models.Model):
    counselor = models.ForeignKey(CounselorProfile, on_delete=models.CASCADE, related_name="booking_history")
    client_name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status_display(self):
        """Returns the status with proper formatting and current state"""
        if self.status == 'scheduled':
            current_datetime = timezone.now()
            booking_datetime = datetime.combine(self.date, self.time)
            if booking_datetime < current_datetime:
                return 'completed'
        return self.status
    
    class Meta:
        verbose_name_plural = "Booking Histories"
        constraints = [
            models.UniqueConstraint(
                fields=['counselor', 'date', 'time'],
                condition=models.Q(status='scheduled'),
                name='unique_active_booking'
            )
        ]

    def __str__(self):
        return f"{self.client_name} - {self.date} at {self.time}"
    
class CounselorRating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    counselor = models.ForeignKey(CounselorProfile, on_delete=models.CASCADE, related_name='ratings')
    booking = models.OneToOneField(UserBookingHistory, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'booking']   

    def __str__(self):
        return f"{self.counselor.name} - {self.rating}★ by {self.user.name}"


class CareerField(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='career_icons/', null=True, blank=True)  
    description = models.TextField()
    slug = models.SlugField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    scope = models.TextField(blank=True)
    future_prospects = models.TextField(blank=True)
    skill_requirements = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Degree(models.Model):
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    career_field = models.ForeignKey(CareerField, on_delete=models.CASCADE, related_name='degrees')
    description = models.TextField()
    eligibility = models.TextField()
    
    entrance_exams = models.TextField(blank=True)
    course_curriculum = models.TextField(blank=True)
    career_opportunities = models.TextField(blank=True)
    fees_range = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

# class Institution(models.Model):
#     name = models.CharField(max_length=200)
#     location = models.CharField(max_length=100)
#     degrees = models.ManyToManyField(Degree, related_name='institutions')
#     ranking = models.IntegerField(null=True, blank=True)
#     website = models.URLField(blank=True)
#     nirf_score = models.FloatField(null=True, blank=True)
#     nirf_ranking_year = models.IntegerField(default=2023)
    
#     class Meta:
#         ordering = ['ranking', 'name']
        
#     def __str__(self):
#         return self.name
    
# models.py

class Institution(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    degrees = models.ManyToManyField(Degree, related_name='institutions')
    ranking = models.IntegerField(null=True, blank=True)
    nirf_score = models.FloatField(null=True, blank=True)
    nirf_ranking_year = models.IntegerField(default=2023)
    
    class Meta:
        ordering = ['ranking', 'name']
        indexes = [
            models.Index(fields=['ranking']),
            models.Index(fields=['nirf_score']),
        ]
    
    def __str__(self):
        return f"{self.name} (Rank: {self.ranking})"
    
    def clean(self):
        # Clean name field
        if self.name:
            self.name = ' '.join(self.name.split())  # Remove extra spaces
            self.name = self.name.replace('More Details', '').replace('Close', '')
            self.name = self.name.strip()
        
        # Clean location field
        if self.location:
            self.location = ' '.join(self.location.split())
            self.location = self.location.strip()
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class JobRole(models.Model):
    title = models.CharField(max_length=100)
    career_field = models.ForeignKey(CareerField, related_name='job_roles', on_delete=models.CASCADE)
    description = models.TextField()
    average_salary = models.CharField(max_length=50)
    required_skills = models.TextField()