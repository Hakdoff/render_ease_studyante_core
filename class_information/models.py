from django.db import models
from django.forms import ValidationError
from base.models import BaseModelWithUUID, User

YEAR_LEVEL_CHOICES = [
    ('GRADE 7', 'GRADE 7'),
    ('GRADE 8', 'GRADE 8'),
    ('GRADE 9', 'GRADE 9'),
    ('GRADE 10', 'GRADE 10'),
    ('GRADE 11', 'GRADE 11'),
    ('GRADE 12', 'GRADE 12'),
]

GRADING_PERIOD_CHOICES = (
    ('FIRST_GRADING', 'First Grading'),
    ('SECOND_GRADING', 'Second Grading'),
    ('THIRD_GRADING', 'Third Grading'),
    ('FOURTH_GRADING', 'Fourth Grading'),
)


class GradeEncode(BaseModelWithUUID):
    grading_period = models.CharField(
        max_length=255, choices=GRADING_PERIOD_CHOICES, default="FIRST_GRADING")
    is_enable = models.BooleanField(default=False)

    class Meta:
        unique_together = ["grading_period", "is_enable"]

    def __str__(self) -> str:
        return f'{self.grading_period} - {self.is_enable}'


class Department(models.Model):
    department_head = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=False, null=True)
    name = models.CharField(max_length=250, verbose_name="Department Name")
    code = models.CharField(max_length=50, verbose_name="Department Code")

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'


class Section(BaseModelWithUUID):
    name = models.CharField(max_length=250, verbose_name="Section Name")
    year_level = models.CharField(
        max_length=10, choices=YEAR_LEVEL_CHOICES, default='GRADE 7')

    def __str__(self) -> str:
        return f'{self.name} - {self.year_level}'


class Subject(BaseModelWithUUID):
    name = models.CharField(max_length=250, verbose_name="Subject Name")
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year_level = models.CharField(
        max_length=10, choices=YEAR_LEVEL_CHOICES, default='GRADE 7')
    written_work = models.IntegerField(default=0)
    performance_task = models.IntegerField(default=0)
    quartery_assessment = models.IntegerField(default=0)

    def clean(self):
        written_work = self.written_work
        performance_task = self.performance_task
        quartery_assessment = self.quartery_assessment

        if written_work <= 1 or performance_task <= 1 or quartery_assessment <= 1:
            raise ValidationError(
                "Each of the following (written work, performance task, quartery assessmeent) field value must be greater than 1.")

        total = written_work + performance_task + quartery_assessment

        if total != 100:
            raise ValidationError("The sum of the fields must be 100.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure the model is clean before saving
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} - {self.year_level}'
