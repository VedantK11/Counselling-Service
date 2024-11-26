"""OCCS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ccservice import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.index,name='index'),
    path('counsellorLogin/', views.counsellor_login, name='counsellorLogin'),
    path('counsellorRegistration/', views.counselor_registration, name='counsellorRegistration'),
    path('counsellorIndex/', views.counsellor_index, name='counsellorIndex'),  
    path('update-counselor-slots/', views.update_counselor_slots, name='update_counselor_slots'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('studentLogin/', views.student_login, name='studentLogin'),
    path('studentRegistration/', views.student_registration, name='studentRegistration'),
    path('studentIndex/', views.student_index, name='studentIndex'),  
    path('get-counselor-slots/<int:counselor_id>/', views.get_counselor_slots, name='get_counselor_slots'),
    path('book-slot/', views.book_slot, name='book_slot'),
    path('bookings/', views.view_bookings, name='view_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('verify-counselor-data/', views.verify_counselor_data, name='verify_counselor_data'),
    path('get-counselor-bookings/', views.get_counselor_bookings, name='get_counselor_bookings'),
    path('get-booking-details/<int:booking_id>/', views.get_booking_details, name='get_booking_details'),
    path('cancel-counselor-booking/<int:booking_id>/', views.cancel_counselor_booking, name='cancel_counselor_booking'),
    path('update-counselor-settings/', views.update_counselor_settings, name='update_counselor_settings'),
    path('update-student-settings/', views.update_student_settings, name='update_student_settings'),
    path('career', views.career, name='career'),
    # path('field/<slug:slug>/', views.career_field_detail, name='career_field_detail'),
    path('colleges/', views.college_rankings, name='college_rankings'),
    path('college/<int:id>/', views.college_detail, name='college_detail'),
    path('field/<slug:slug>/', views.career_field_detail, name='career_field_detail'),
    path('field/<slug:slug>/colleges/', views.career_colleges, name='career_colleges'),
    path('institution/<int:id>/', views.institution_detail, name='institution_detail'),
   
]



