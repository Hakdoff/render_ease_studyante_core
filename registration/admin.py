from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdminView(admin.ModelAdmin):
    search_fields = ['student__user__last_name',
                     'student__user__first_name', 'section__name']
    list_display = ['student', 'contact_number', 'section', 'academic_year']
    list_filter = ['student', 'section',]
    autocomplete_fields = ['student', 'section', 'academic_year']

    def contact_number(self, obj):
        return obj.student.contact_number if obj.student else None
    contact_number.short_description = "Contact Number"
