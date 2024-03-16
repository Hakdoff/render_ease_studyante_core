from django.contrib import admin
from django import forms

from base.admin import BaseAdmin
from class_information.models import Section, Subject
from user_profile.models import Teacher

from .models import Assessment, Attendance, Schedule, StudentAssessment, Grade, AcademicYear

admin.site.register(AcademicYear)


@admin.register(Schedule)
class ScheduleAdmin(BaseAdmin):
    formfield_querysets = {
        'subject': lambda: Subject.objects.all(),
        'teacher': lambda: Teacher.objects.all(),
        'section': lambda: Section.objects.all(),
    }
    edit_fields = (
        ('Schedule Information', {
            'fields': [
                'subject',
                'teacher',
                'section',
                'day',
                'time_start',
                'time_end'
            ]
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            # Get the selected subject ID from the form data
            subject_id = request.GET.get('subject', None)
            if subject_id:
                try:
                    # Fetch the subject instance
                    subject = Subject.objects.get(pk=subject_id)
                    # Filter the queryset of teachers based on the subject's department
                    kwargs["queryset"] = subject.department.teacher_set.all()
                except Subject.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def add_view(self, request, *args, **kwargs):
        # This method is called when the admin page for adding a new Schedule is requested
        # We include the subject field in the form to ensure its value is available in the form data
        self.fields = ('subject', 'teacher', 'section',
                       'day', 'time_start', 'time_end')
        return super().add_view(request, *args, **kwargs)


admin.site.register(Attendance)
admin.site.register(Assessment)
admin.site.register(StudentAssessment)
admin.site.register(Grade)
