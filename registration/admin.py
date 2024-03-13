from django.contrib import admin

from base.admin import BaseAdmin
from class_information.models import Section
from user_profile.models import Student
from .models import Registration


@admin.register(Registration)
class RegistrationAdminView(BaseAdmin):
    search_fields = ['user__email', 'user__firstname', 'user__lastname']
    list_fields = ('student', 'section', 'academic_year')
    readonly_fields = ['academic_year', 'created_at', 'updated_at']
    formfield_querysets = {
        'section': lambda: Section.objects.all(),
        'student': lambda: Student.objects.all()
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

    def save_model(self, request, obj, form, change):
        if obj.academic_year == '':  # If the object is being created
            obj.academic_year = obj.current_academic_year()
        obj.save()
