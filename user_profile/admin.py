from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group, Permission

from base.admin import BaseAdmin, Account
from .models import Student, Teacher, Parent
from department.models import Department


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_fields = ('user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo')
    formfield_querysets = {
        'user': lambda: Account.objects.all()
    }
    edit_fields = (
        ('Student Information', {
            'fields': [
                'user',
                'contact_number',
                'age',
                'gender',
                'profile_photo',
                'year_level',
                'qr_code_photo'
            ],
        }),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )
    search_fields = ('user__first_name', 'user__last_name')


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_fields = ('user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo')
    formfield_querysets = {
        'user': lambda: Account.objects.all(),
        'department': lambda: Department.objects.all(),
    }
    edit_fields = (
        ('Teacher Information', {
            'fields': [
                'user',
                'contact_number',
                'age',
                'gender',
                'profile_photo',
                'department'
            ],
        }),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )
    search_fields = ('user__first_name', 'user__last_name')


@admin.register(Parent)
class ParentAdmin(BaseAdmin):
    list_fields = ('user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo')
    formfield_querysets = {
        'user': lambda: Account.objects.all(),
        'students': lambda: Student.objects.all(),
    }
    edit_fields = (
        ('Teacher Information', {
            'fields': [
                'user',
                'contact_number',
                'age',
                'gender',
                'profile_photo',
                'students'
            ],
        }),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )
    search_fields = ('user__first_name', 'user__last_name')
