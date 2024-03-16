from django.db import models
from user_profile.models import Student, Teacher
from class_information.models import Subject, Section
from base.models import BaseModelWithUUID


class Grade(models.Model):
    GRADING_PERIOD_CHOICES = (
        ('First Grading', 'First Grading'),
        ('Second Grading', 'Second Grading'),
        ('Third Grading', 'Third Grading'),
        ('Fourth Grading', 'Fourth Grading'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grading_period = models.CharField(
        max_length=20, choices=GRADING_PERIOD_CHOICES)
    marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grading_period} - {self.marks}"


class Schedule(BaseModelWithUUID):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        return f'{self.day} {self.time_start} - {self.time_end} {self.subject.name} - {self.teacher.user.last_name} {self.teacher.user.first_name}'


class Assessment(BaseModelWithUUID):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class StudentAssessment(BaseModelWithUUID):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2)


class Attendance(BaseModelWithUUID):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
