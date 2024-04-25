from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from academic_record.models import AcademicYear, Schedule
from base.admin import BaseAdmin
from user_profile.models import Teacher
from registration.models import Registration
from .models import Subject, Department, Section, GradeEncode


@admin.register(GradeEncode)
class GradeEncodeAdminView(BaseAdmin):
    list_fields = ('grading_period', 'is_enable',)
    search_fields = ('grading_period',)
    list_filter = ['grading_period', 'is_enable']
    edit_fields = (
        ('Grade Encoding', {
            'fields': [
                'grading_period',
                'is_enable',
            ]
        }),
    )


class ScheduleTabularInline(admin.TabularInline):
    verbose_name = "Schedule"
    verbose_name_plural = "Schedules"
    model = Schedule
    fields = ('section',)
    readonly_fields = ('section',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(ScheduleTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs


@admin.register(Subject)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'year_level']
    search_fields = ['name', 'year_level', 'code',]
    list_filter = ('name', 'year_level',)
    inlines = [ScheduleTabularInline,]
    edit_fields = (
        ('Subject', {
            'fields': [
                'name',
                'code',
                'department',
                'year_level',
                'written_work',
                'performance_task',
                'quartery_assessment',
            ]
        }),
    )


class TeachersTabularInline(admin.TabularInline):
    verbose_name = "Teacher"
    verbose_name_plural = "Teachers"
    model = Teacher
    fields = ('user', 'department',)
    readonly_fields = ('user',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        departments = Department.objects.all()
        qs = super(TeachersTabularInline, self).get_queryset(request)
        if departments.exists():
            return qs.filter(department__in=departments)

        return qs


@admin.register(Department)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    list_filter = ('code', 'name')
    inlines = [TeachersTabularInline,]
    edit_fields = (
        ('Department', {
            'fields': [
                'code',
                'name',
            ]
        }),
    )


class RegistrationTabularInline(admin.TabularInline):
    verbose_name = "Student"
    verbose_name_plural = "Students"
    model = Registration
    fields = ('student', 'academic_year')
    readonly_fields = ('student', 'academic_year')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(RegistrationTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs

class SubjectTabularInline(admin.TabularInline):
    verbose_name = "Subject"
    verbose_name_plural = "Subjects"
    model = Schedule
    fields = ('subject', 'academic_year',)
    readonly_fields = ('subject', 'academic_year',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(SubjectTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs
    
@admin.register(Section)
class SectionAdminView(admin.ModelAdmin):
    list_display = ['name', 'year_level']
    search_fields = ['name', 'year_level']
    list_filter = ('name', 'year_level')
    inlines = [RegistrationTabularInline, SubjectTabularInline,]
    edit_fields = (
        ('Section Information', {
            'fields': [
                'name',
                'year_level',
            ]
        }),
    )
