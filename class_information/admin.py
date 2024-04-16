from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from academic_record.models import AcademicYear
from base.admin import BaseAdmin
from registration.models import Registration
from .models import Subject, Department, Section


@admin.register(Subject)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'year_level']
    search_fields = ['name', 'code', ]
    list_filter = ('name', 'code',)
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


@admin.register(Department)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    list_filter = ('code', 'name')
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


@admin.register(Section)
class SectionAdminView(admin.ModelAdmin):
    list_display = ['name', 'year_level']
    search_fields = ['name', 'year_level']
    list_filter = ('name', 'year_level')
    inlines = [RegistrationTabularInline,]
    edit_fields = (
        ('Section Information', {
            'fields': [
                'name',
                'year_level',
            ]
        }),
    )
