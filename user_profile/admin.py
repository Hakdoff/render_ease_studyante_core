from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group, Permission

from base.admin import BaseAdmin, User
from .models import Student, Teacher, Parent
from department.models import Department


class StudentCreationForm(forms.ModelForm):
    # Add fields for creating a new user
    email = forms.CharField(label='Email', widget=forms.EmailInput)
    first_name = forms.CharField(
        label='Firstname', widget=forms.TextInput)
    last_name = forms.CharField(label='Lastname', widget=forms.TextInput)

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['user', 'delete_remarks',
                   'update_remarks', 'deleted_at', 'deleted_by_id']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        contact_number = cleaned_data.get('contact_number')

        instance = getattr(self, 'instance', None)

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance and instance.pk:
            user = User.objects.get(pk=instance.user.pk)

            # Check for uniqueness
            if User.objects.filter(username=email).exclude(username=user.email).exists():
                self.add_error('email', 'Email already exists')

            if Student.objects.exclude(user__email=user.email, contact_number=contact_number).filter(contact_number=contact_number).exists():
                self.add_error('contact_number', 'Contact already exists')
        else:
            # Check for uniqueness
            if User.objects.filter(username=email).exists():
                self.add_error('email', 'Email already exists')

            if Student.objects.filter(contact_number=contact_number).exists():
                self.add_error('contact_number', 'Contact already exists')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        email = self.cleaned_data['email']

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance.pk:
            user = User.objects.get(pk=instance.user.pk)
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.username = email
            user.email = email

        else:
            # Save the user and student objects
            user = User.objects.create_user(
                username=email,
                password='1234',
                email=email,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            )
            instance.user = user

        if commit:
            instance.save()
        return instance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentCreationForm
    formfield_querysets = {
        'user': lambda: User.objects.all(),
    }
    fieldsets = (
        ('Student Information', {
            'fields': [
                'email',
                'first_name',
                'last_name',
                'contact_number',
                'address',
                'age',
                'gender',
                'profile_photo',
            ],
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(StudentAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            if obj.user:
                form.base_fields['first_name'].initial = obj.user.first_name
                form.base_fields['last_name'].initial = obj.user.last_name
                form.base_fields['email'].initial = obj.user.email
        return form


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_fields = ('user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo')
    formfield_querysets = {
        'user': lambda: User.objects.all(),
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
        'user': lambda: User.objects.all(),
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
