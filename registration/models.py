import datetime
from django.db import models
from academic_record.models import AcademicYear
from base.models import BaseModelWithUUID
from class_information.models import Section
from user_profile.models import Student


# Create your models here.
class Registration(BaseModelWithUUID):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.section}"
