from django.contrib import admin

from academic_record.models import AcademicYear
from base.admin import BaseAdmin
from class_information.models import Section
from user_profile.models import Student
from .models import Registration
from django import forms


@admin.register(Registration)
class RegistrationAdminView(admin.ModelAdmin):
    search_fields = ['student__user__last_name', 'student__user__first_name', 'section__name']
    list_display = ['student', 'contact_number', 'section', 'academic_year']
    list_filter = ['student', 'section',]
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
        })
    )

    def contact_number(self,obj):
        return obj.student.contact_number if obj.student else None
    contact_number.short_description="Contact Number"