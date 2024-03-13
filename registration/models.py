import datetime
from django.db import models
from base.models import BaseModelWithUUID
from class_information.models import Section
from user_profile.models import Student


# Create your models here.
class Registration(BaseModelWithUUID):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)

    def __str__(self):
        return f"{self.student} - {self.section} - {self.academic_year}"

    @classmethod
    def current_academic_year(cls):
        today = datetime.date.today()
        year = today.year
        next_year = year + 1
        return f"{year}-{next_year}"
