from django.db import models
from base.models import BaseModelWithUUID, Account
from department.models import Department


class BaseProfile(BaseModelWithUUID):
    class Meta:
        abstract = True

    MALE = 'M'
    FEMALE = 'F'
    NA = 'N/A'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NA, 'N/A'),
    ]

    user = models.OneToOneField(
        Account, on_delete=models.CASCADE)
    address = models.TextField(blank=False, null=False)

    contact_number = models.CharField(max_length=25)
    age = models.IntegerField(null=False, blank=False)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default=NA)
    profile_photo = models.ImageField(
        upload_to='images/profiles/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'


class Student(BaseProfile):
    YEAR_LEVEL_CHOICES = [
        ('GRADE 7', 'Grade 7'),
        ('GRADE 8', 'Grade 8'),
        ('GRADE 9', 'Grade 9'),
        ('GRADE 10', 'Grade 10'),
        ('GRADE 11', 'Grade 11'),
        ('GRADE 12', 'Grade 12'),
    ]

    year_level = models.CharField(
        max_length=10, choices=YEAR_LEVEL_CHOICES, default='GRADE 7')
    qr_code_photo = models.ImageField(
        upload_to='images/qr_code/', blank=False, null=False)

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'


class Teacher(BaseProfile):
    department = models.ForeignKey(
        Department, related_name='teacher_department', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'
