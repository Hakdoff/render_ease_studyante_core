from django.db import models
from base.models import BaseModelWithUUID

YEAR_LEVEL_CHOICES = [
    ('GRADE 7', 'GRADE 7'),
    ('GRADE 8', 'GRADE 8'),
    ('GRADE 9', 'GRADE 9'),
    ('GRADE 10', 'GRADE 10'),
    ('GRADE 11', 'GRADE 11'),
    ('GRADE 12', 'GRADE 12'),
]


class Department(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.code + " " + self.name


class Section(BaseModelWithUUID):
    name = models.CharField(max_length=250)
    year_level = models.CharField(
        max_length=10, choices=YEAR_LEVEL_CHOICES, default='GRADE 7')

    def __str__(self) -> str:
        return f'{self.name} - {self.year_level}'


class Subject(BaseModelWithUUID):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year_level = models.CharField(
        max_length=10, choices=YEAR_LEVEL_CHOICES, default='GRADE 7')

    def __str__(self) -> str:
        return f'{self.name} - {self.year_level}'
