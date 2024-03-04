from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group, Permission

from base.admin import BaseAdmin, Account
from .models import Student


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    list_fields = ('user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo')
    formfield_querysets = {
        'user': lambda: Account.objects.all()
    }
    edit_fields = (
        ('Identity Information', {
            'fields': [
                'contact_number',
                'age',
                'user',
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
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            },
        ),
    )
    search_fields = ('user__first_name', 'user__last_name')
