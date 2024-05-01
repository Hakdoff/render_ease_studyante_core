from django import forms
from django.contrib import admin
from .models import Registration

class RegistrationAdminForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        academic_year = cleaned_data.get('academic_year')  # Ensure academic_year is in the form

        if student and academic_year:
            # Check if the student is already registered in the same academic year
            if Registration.objects.filter(student=student, academic_year=academic_year).exists():
                self.add_error('student', 'This student is already registered for this academic year.')
        
        return cleaned_data

@admin.register(Registration)
class RegistrationAdminView(admin.ModelAdmin):
    search_fields = ['student__user__last_name',
                     'student__user__first_name', 'section__name']
    list_display = ['student', 'contact_number', 'section', 'academic_year']
    list_filter = ['student', 'section',]
    form = RegistrationAdminForm
    autocomplete_fields = ['student', 'section', 'academic_year']

    def contact_number(self, obj):
        return obj.student.contact_number if obj.student else None
    contact_number.short_description = "Contact Number"
