from datetime import datetime, timedelta

from class_information.models import Section
from registration.models import Registration
from .models import AcademicYear, Attendance, Schedule


def perform_end_of_day_tasks():
    academic_years = AcademicYear.objects.all()
    sections = Section.objects.all()

    # perform student absent
    if academic_years.exists():
        current_date = datetime.now()
        recent_academic_year = academic_years.first()
        schedules = Schedule.objects.filter(
            section__in=sections, academic_year=recent_academic_year)
        registered_students = Registration.objects.filter(
            academic_year=recent_academic_year)
        if schedules.exists():
            for registered_student in registered_students:
                for schedule in schedules:
                    # validate student if he/she already have attendance
                    attendances = Attendance.objects.filter(
                        student__pk=registered_student.student.pk, time_in__date=current_date, schedule=schedule)
                    if not attendances.exists():
                        # perform creation of student absent
                        Attendance.objects.create(
                            student=registered_student.student, schedule=schedule, is_present=False, time_in=None)
