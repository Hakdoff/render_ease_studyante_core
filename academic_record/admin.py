from django.contrib import admin
from django import forms

from base.admin import BaseAdmin
from class_information.models import Section, Subject
from user_profile.models import Student, Teacher

from .models import Assessment, Attendance, Schedule, StudentAssessment, AcademicYear


@admin.register(AcademicYear)
class AcademicYearView(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name', 'start_date', 'end_date']
    list_filter = ('name',)
    edit_fields = (
        ('Department', {
            'fields': [
                'code',
                'name',
            ]
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'time_start', 'time_end',
                    'section', 'subject']
    search_fields = ('teacher__user__first_name',
                     'teacher__user__last_name', 'section__name', 'subject__name')
    list_filter = ['teacher', 'section__name', 'subject', ]
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
        self.fields = ('academic_year', 'subject', 'teacher', 'section',
                       'day', 'time_start', 'time_end')
        return super().add_view(request, *args, **kwargs)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule',  'is_present', 'attendance_date']
    search_fields = ['student__user__last_name', 'student__user__first_name',]
    list_filter = ['student', 'schedule',]
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
    list_filter = ('assessment_type', 'subject', 'teacher')
    autocomplete_fields = ['subject', 'teacher', 'academic_year']
    inlines = [StudentAssessmentTabularInLine,]


@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    search_fields = ['assessment__name',
                     'student__user__last_name', 'student__user__first_name',]
    list_display = ['assessment', 'student', 'obtained_marks']
    list_filter = ['assessment', 'student',]
    autocomplete_fields = ['student', 'assessment']
