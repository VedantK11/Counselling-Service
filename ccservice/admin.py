from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CareerField, Degree, Institution, JobRole

@admin.register(CareerField)
class CareerFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'career_field', 'duration')
    list_filter = ('career_field',)
    search_fields = ('name', 'career_field__name')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'ranking')
    list_filter = ('location',)
    search_fields = ('name', 'location')
    filter_horizontal = ('degrees',)

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'career_field', 'average_salary')
    list_filter = ('career_field',)
    search_fields = ('title', 'career_field__name')
