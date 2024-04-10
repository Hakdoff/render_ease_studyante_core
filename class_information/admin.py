from django.contrib import admin

from base.admin import BaseAdmin
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


@admin.register(Section)
class SectionAdminView(admin.ModelAdmin):
    list_display = ['name', 'year_level']
    search_fields = ['name', 'year_level']
    list_filter = ('name', 'year_level')
    edit_fields = (
        ('Section Information', {
            'fields': [
                'name',
                'year_level',
            ]
        }),
    )
