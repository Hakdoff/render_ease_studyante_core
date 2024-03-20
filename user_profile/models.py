from django.db import models
from base.models import BaseModelWithUUID, User
from class_information.models import Department


""" 
    Base Model profile since both student, parent and teacher have common entities
    BaseModelWithUUID to replace django id's (1,2, 3) to UUID base ids
    class Meta: To define what model django to be configure, 
        abstract means that the models is abstracted and can be inherited
    
    Student, Teacher and Parent are inherited in BaseProfile model
"""


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
        User, on_delete=models.CASCADE)
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
        return f'{self.user.last_name} - {self.user.first_name}'


class Teacher(BaseProfile):
    department = models.ForeignKey(
        Department, related_name='teacher_department', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'


class Parent(BaseProfile):
    students = models.ManyToManyField(
        Student, 'kids')

    def __str__(self):
        return f'{self.user.last_name}- {self.user.first_name}'
