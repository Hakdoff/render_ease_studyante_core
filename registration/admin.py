from django.contrib import admin

from academic_record.models import AcademicYear
from base.admin import BaseAdmin
from class_information.models import Section
from user_profile.models import Student
from .models import Registration
from django import forms


@admin.register(Registration)
class RegistrationAdminView(BaseAdmin):
    search_fields = ['user__email', 'user__firstname', 'user__lastname']
    list_fields = ('student', 'section', 'academic_year')
    formfield_querysets = {
        'section': lambda: Section.objects.all(),
        'student': lambda: Student.objects.all(),
        'academic_year': lambda: AcademicYear.objects.all(),
    }
    edit_fields = (
        ('Registration Information', {
            'fields': [
                'student',
                'section',
                'academic_year'
            ]
        }),
    )
