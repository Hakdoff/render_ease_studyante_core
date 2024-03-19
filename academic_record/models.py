from django.db import models
from user_profile.models import Student, Teacher
from class_information.models import Subject, Section
from base.models import BaseModelWithUUID
from django.utils.timezone import now


class AcademicYear(BaseModelWithUUID):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Grade(BaseModelWithUUID):
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
    academic_year = models.ForeignKey(
        AcademicYear, related_name='academic_schedule', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        return f'{self.day} {self.time_start} - {self.time_end} {self.subject.name} - {self.teacher.user.last_name} {self.teacher.user.first_name}'


class Assessment(BaseModelWithUUID):
    ASSESSMENT_TYPE_CHOICES = [
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('EXAM', 'Exam'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    assessment_type = models.CharField(
        max_length=50, choices=ASSESSMENT_TYPE_CHOICES)
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
    date_attend = models.DateTimeField(default=now)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.user.last_name} {self.student.user.first_name} - {self.is_present}'
