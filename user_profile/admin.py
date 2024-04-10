from io import BytesIO
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q

import qrcode

from base.admin import BaseAdmin, BaseStackedInline, User
from .models import Student, Teacher, Parent
from class_information.models import Department
from reedsolo import RSCodec, ReedSolomonError

""" 
    Base Model profile since both student, parent and teacher have common entities
    BaseModelWithUUID to replace django id's (1,2, 3) to UUID base ids
    class Meta: To define what model django to be configure, 
        abstract means that the models is abstracted and can be inherited
    
    Student, Teacher and Parent are inherited in BaseProfile model
"""


class StudentCreationForm(forms.ModelForm):
    # Add fields for creating a new user
    email = forms.CharField(label='Email', widget=forms.EmailInput)
    first_name = forms.CharField(
        label='Firstname', widget=forms.TextInput)
    last_name = forms.CharField(label='Lastname', widget=forms.TextInput)

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['user',]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        contact_number = cleaned_data.get('contact_number')

        instance = getattr(self, 'instance', None)

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance and instance.pk and instance.user_id:
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
        last_name = self.cleaned_data['last_name']
        contact_number = self.cleaned_data.get('contact_number', '')
        

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance.pk and instance.user_id:
            user = User.objects.get(pk=instance.user.pk)
            user.first_name = self.cleaned_data['first_name']
            user.last_name = last_name
            user.username = email
            user.email = email

        else:
            last_4_digits = contact_number[-4:]
            last_name += '_' * max(0, 4 - len(last_name))
            password = (last_name[:4] + last_4_digits)
            # Save the user and student objects
            user = User.objects.create_user(
                username=email,
                password=password,
                email=email,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            )
            instance.user = user

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # rsc = RSCodec(10)
            # user_id = str(user.pk)
            # encoded = user_id.encode('utf-8')
            # encoded_value = rsc.encode(bytearray(encoded))

            # You can pass any data you want to encode in the QR code
            qr.add_data(user.pk)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save QR code image to ImageField
            buffer = BytesIO()
            img.save(buffer)
            file_name = f'qr_code_{user.pk}.png'
            file_buffer = buffer.getvalue()
            instance.qr_code_photo.save(file_name, InMemoryUploadedFile(
                file=BytesIO(file_buffer),
                field_name=None,
                name=file_name,
                content_type='image/png',
                size=len(file_buffer),
                charset=None
            ), save=False)

        if commit:
            instance.save()
        return instance
    
class TeacherCreationForm(forms.ModelForm):
    # Add fields for creating a new user
    email = forms.CharField(label='Email', widget=forms.EmailInput)
    first_name = forms.CharField(
        label='Firstname', widget=forms.TextInput)
    last_name = forms.CharField(label='Lastname', widget=forms.TextInput)

    class Meta:
        model = Teacher
        fields = '__all__'
        exclude = ['user',]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        contact_number = cleaned_data.get('contact_number')

        instance = getattr(self, 'instance', None)

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance and instance.pk and instance.user_id:
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
        last_name = self.cleaned_data['last_name']
        contact_number = self.cleaned_data.get('contact_number', '')

        # Check if instance exists and has an id (indicating it's an existing object)
        if instance.pk and instance.user_id:
            user = User.objects.get(pk=instance.user.pk)
            user.first_name = self.cleaned_data['first_name']
            user.last_name = last_name
            user.username = email
            user.email = email

        else:
            last_4_digits = contact_number[-4:]
            last_name += '_' * max(0, 4 - len(last_name))
            password = (last_name[:4] + last_4_digits)

            # Save the user and student objects
            user = User.objects.create_user(
                username=email,
                password=password,
                email=email,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            )
            instance.user = user

        if commit:
            instance.save()
        return instance



class ParentCreationForm(forms.ModelForm):
    email = forms.CharField(label='Email', widget=forms.EmailInput)
    first_name = forms.CharField(label='First Name', widget=forms.TextInput)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput)

    class Meta:
        model = Parent
        fields = '__all__'
        exclude = ['user',]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        contact_number = cleaned_data.get('contact_number')

        instance = getattr(self, 'instance', None)

        if instance and instance.pk and instance.user_id:
            user = User.objects.get(pk=instance.user.pk)

            if User.objects.filter(username=email).exclude(username=user.email).exists():
                self.add_error('email', 'email already exists')

            if Parent.objects.exclude(user__email=user.email, contact_number=contact_number).filter(contact_number=contact_number).exists():
                self.add_error('contact_number',
                               'contact number already exists')
        else:
            if User.objects.filter(username=email).exists():
                self.add_error('email', 'email already exists')

            if Parent.objects.filter(contact_number=contact_number).exists():
                self.add_error('contact_number',
                               'contact number already exists')

        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        email = self.cleaned_data['email']
        last_name = self.cleaned_data['last_name']
        contact_number = self.cleaned_data.get('contact_number', '')

        if instance.pk and instance.user_id:
            user = User.objects.get(pk=instance.user.pk)
            user.first_name = self.cleaned_data['first_name']
            user.last_name = last_name
            user.username = email
            user.email = email

        else:
            last_4_digits = contact_number[-4:]
            last_name += '_' * max(0, 4 - len(last_name))
            password = (last_name[:4] + last_4_digits)

            user = User.objects.create_user(
                username=email,
                password=password,
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
    list_display = ('user', 'year_level')
    search_fields = ['user__email', 'user__firstname', 'user__lastname']
    list_filter = ['user',]
    form = StudentCreationForm
    formfield_querysets = {
        'user': lambda: User.objects.all(),
    }
    readonly_fields = ['qr_code_photo']
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
                'year_level',
                'profile_photo',
                'qr_code_photo',
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
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    list_filter = ['user', 'department']
    form = TeacherCreationForm
    formfield_querysets = {
        'user': lambda: User.objects.all(),
        'department': lambda: Department.objects.all(),
    }
    edit_fields = (
        ('Teacher Information', {
            'fields': [
                'email',
                'first_name',
                'last_name',
                'contact_number',
                'address',
                'age',
                'gender',
                'profile_photo',
                'department'
            ],
        }),
    )
    # add_fieldsets = (
    #     (
    #         None,
    #         {
    #             'classes': ('wide',),
    #             'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
    #         },
    #     ),
    # )
    search_fields = ['user__first_name', 'user__last_name']
    def get_form(self, request, obj=None, **kwargs):
        form = super(TeacherAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            if obj.user:
                form.base_fields['first_name'].initial = obj.user.first_name
                form.base_fields['last_name'].initial = obj.user.last_name
                form.base_fields['email'].initial = obj.user.email
        return form


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    form = ParentCreationForm
    list_display = ['user', 'address', 'contact_number',
                   'age', 'gender', 'profile_photo']
    list_filter =  ['user',]
    formfield_querysets = {
        'user': lambda: User.objects.all(),
        'students': lambda: Student.objects.all()
    }
    edit_fields = (
        ('Parent Information', {
            'fields': [
                'email',
                'first_name',
                'last_name',
                'contact_number',
                'age',
                'gender',
                'address',
                'profile_photo',
                'students'
            ]
        }),
    )
    filter_vertical = ['students']
    search_fields = ('user__first_name', 'user__last_name')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ParentAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            if obj.user:
                form.base_fields['first_name'].initial = obj.user.first_name
                form.base_fields['last_name'].initial = obj.user.last_name
                form.base_fields['email'].initial = obj.user.email
        return form
