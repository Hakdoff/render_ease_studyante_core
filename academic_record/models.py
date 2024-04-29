from django.db import models
from user_profile.models import Student, Teacher
from class_information.models import Subject, Section
from base.models import BaseModelWithUUID
from django.utils.timezone import now
from datetime import date


class AcademicYear(BaseModelWithUUID):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.CharField(max_length=100, blank=True)
    first_grading_dealine = models.DateField(null=True, blank=False)
    second_grading_dealine = models.DateField(null=True, blank=False)
    third_grading_dealine = models.DateField(null=True, blank=False)
    fourth_grading_dealine = models.DateField(null=True, blank=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


class Schedule(BaseModelWithUUID):
    academic_year = models.ForeignKey(
        AcademicYear, related_name='academic_schedule', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    time_start = models.TimeField()
    time_end = models.TimeField()
    is_view_grade = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.day} {self.time_start} - {self.time_end} {self.subject.name} - {self.teacher.user.last_name} {self.teacher.user.first_name}'


class Assessment(BaseModelWithUUID):
    TASK_TYPE_CHOICES = [
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('PROJECT', 'Project'),
        ('EXAM', 'Exam'),
    ]
    GRADING_PERIOD_CHOICES = (
        ('FIRST_GRADING', 'First Grading'),
        ('SECOND_GRADING', 'Second Grading'),
        ('THIRD_GRADING', 'Third Grading'),
        ('FOURTH_GRADING', 'Fourth Grading'),
    )
    ASSESSMENT_TYPE_CHOICES = (
        ('WRITTEN_WORKS', 'Written Works'),
        ('PERFORMANCE_TASK', 'Performance Task'),
        ('QUARTERLY_ASSESSMENT', 'Quarterly Assessment'),
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Assessment Name")
    assessment_type = models.CharField(
        max_length=50, choices=ASSESSMENT_TYPE_CHOICES, default='WRITTEN_WORKS')
    task_type = models.CharField(
        max_length=50, choices=TASK_TYPE_CHOICES, default='ASSIGNMENT')

    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grading_period = models.CharField(
        max_length=255, choices=GRADING_PERIOD_CHOICES, default="FIRST_GRADING")

    def __str__(self):
        return self.name


class StudentAssessment(BaseModelWithUUID):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ['assessment', 'student',]

    def __str__(self):
        return f'{self.assessment.name} - {self.student.user.last_name}, {self.student.user.first_name}'


class Attendance(BaseModelWithUUID):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time_in = models.DateTimeField(default=now, blank=True, null=True)
    time_out = models.DateTimeField(blank=True, null=True)
    is_present = models.BooleanField(default=False)
    attendance_date = models.DateField(default=date.today)

    def __str__(self):
        return f'{self.student.user.last_name} {self.student.user.first_name} - {self.is_present}'
