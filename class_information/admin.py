from django.contrib import admin

from base.admin import BaseAdmin
from .models import Subject, Department, Section

admin.site.register(Subject)


@admin.register(Department)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(Section)
class SectionAdminView(BaseAdmin):
    list_fields = ('name', 'year_level')
    search_fields = ('name',)
    list_filter = ['year_level',]
    edit_fields = (
        ('Section Information', {
            'fields': [
                'name',
                'year_level',
            ]
        }),
    )
