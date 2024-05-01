from django.contrib import admin
from django import forms

from base.admin import BaseAdmin
from class_information.models import Section, Subject
from user_profile.models import Student, Teacher

from .models import Assessment, Attendance, Schedule, StudentAssessment, AcademicYear

class AcademicYearForm(forms.ModelForm):

    class Meta:
        model = AcademicYear
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if name and start_date and end_date:
            # Check if an AcademicYear with the same name and date range already exists
            if AcademicYear.objects.filter(
                name=name,
                start_date=start_date,
                end_date=end_date
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("An Academic Year with the same name and date range already exists.")

        return cleaned_data

@admin.register(AcademicYear)
class AcademicYearView(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name', 'start_date', 'end_date']
    list_filter = ('name',)
    form = AcademicYearForm
    edit_fields = (
        ('Department', {
            'fields': [
                'code',
                'name',
            ]
        }),
    )

class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        day = cleaned_data.get('day')
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')

        if teacher and day and time_start and time_end:
            # Check if there's any schedule that overlaps with the new one
            overlapping_schedules = Schedule.objects.filter(
                teacher=teacher,
                day=day,
                time_start__lte=time_end,  # Starting during or before the new schedule ends
                time_end__gte=time_start   # Ending during or after the new schedule starts
            )

            # Exclude the current instance from the check if it exists
            if self.instance and self.instance.pk:
                overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)

            if overlapping_schedules.exists():
                self.add_error(
                    'time_start', 
                    'This teacher already has a conflicting schedule at this time and day.'
                )
                raise forms.ValidationError('Schedule conflict detected.')

        return cleaned_data

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day', 'time_start', 'time_end',
                    'section', 'subject']
    search_fields = ('teacher__user__first_name',
                     'teacher__user__last_name', 'section__name', 'subject__name')
    form = ScheduleAdminForm
    list_filter = ('teacher__user__teacher', 'section__name', 'subject', )
    formfield_querysets = {
        'subject': lambda: Subject.objects.all(),
        'teacher': lambda: Teacher.objects.all(),
        'section': lambda: Section.objects.all(),
        'academic_year': lambda: AcademicYear.objects.all(),
    }
    autocomplete_fields = ['subject', 'teacher', 'section', 'academic_year']
    edit_fields = (
        ('Schedule Information', {
            'fields': [
                'academic_year',
                'subject',
                'teacher',
                'section',
                'day',
                'is_view_grade',
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
        self.fields = ('academic_year', 'subject', 'teacher', 'section', 'is_view_grade',
                       'day', 'time_start', 'time_end')
        return super().add_view(request, *args, **kwargs)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule',  'is_present', 'attendance_date']
    search_fields = ['student__user__last_name', 'student__user__first_name',]
    list_filter = ('student', 'schedule__day',)
    formfield_querysets = {
        'student': lambda: Student.objects.all(),
        'schedule': lambda: Schedule.objects.all(),
    }
    autocomplete_fields = ['student', 'schedule',]
    edit_fields = (
        ('Attendance', {
            'fields': [
                'schedule',
                'student',
                'time_in',
                'time_out',
                'is_present',
                'attendance_date',
            ]
        }),
    )


class StudentAssessmentTabularInLine(admin.TabularInline):
    model = StudentAssessment
    autocomplete_fields = ['student', ]
    fields = ('assessment', 'student', 'obtained_marks')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_fields = ('name', 'teacher', 'subject', 'academic_year')
    search_fields = ('name', 'subject__name',)
    ordering = ('name',)
    formfield_querysets = {
        'subject': lambda: Subject.objects.all(),
        'teacher': lambda: Teacher.objects.all(),
        'academic_year': lambda: AcademicYear.objects.all(),
    }
    list_filter = ('assessment_type', 'subject', 'teacher__user__teacher')
    autocomplete_fields = ['subject', 'teacher', 'academic_year']
    inlines = [StudentAssessmentTabularInLine,]


@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    search_fields = ['assessment__name',
                     'student__user__last_name', 'student__user__first_name',]
    list_display = ['assessment', 'student', 'obtained_marks']
    list_filter = ['assessment', 'student',]
    autocomplete_fields = ['student', 'assessment']
