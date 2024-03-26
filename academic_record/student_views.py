from decimal import Decimal
from rest_framework import generics, permissions, response, status, exceptions

from academic_record.gpa_caluclate import gpa_calculate
from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (StudentScheduleSerialzers,
                          AttendanceSerializers, StudentAssessmentSerializers)
from .models import Schedule, AcademicYear, Attendance, StudentAssessment
from registration.models import Registration


class StudentScheduleListView(generics.ListAPIView):
    serializer_class = StudentScheduleSerialzers
    queryset = Schedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=user.pk)

            if register_users.exists():
                # check the user wether is register to current academic or not
                register_user = register_users.first()
                return Schedule.objects.filter(academic_year=current_academic, section__pk=register_user.section.pk).order_by('time_start')

        return []


class StudentAttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializers
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=user.pk)

            if register_users.exists():
                # check the user wether is register to current academic or not
                register_user = register_users.first()
                return Attendance.objects.filter(student=register_user.student.pk).order_by('-attendance_date', '-time_in')

        return []


class StudentAttendanceRetrieveView(generics.RetrieveAPIView):
    serializer_class = AttendanceSerializers
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class StudentAssessmentListView(generics.ListAPIView):
    serializer_class = StudentAssessmentSerializers
    queryset = StudentAssessment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()
        grading_period = self.request.GET.get('grading_period', None)

        if academic_years.exists() and grading_period:
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=user.pk)

            if register_users.exists():
                # check the user wether is register to current academic or not
                register_user = register_users.first()
                return StudentAssessment.objects.filter(assessment__academic_year=current_academic, assessment__grading_period=grading_period, student=register_user.student).order_by('created_at', 'assessment__grading_period')

        return []

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Get all student assessment results
        student_assessments = self.get_queryset()

        written_works_marks = []
        performance_tasks_marks = []
        quarterly_assessments_marks = []
        written_weightage = 0
        performance_task_weightage = 0
        quarterly_assessment_weightage = 0

        # Calculate the total weighted marks
        for sa in student_assessments:
            if sa.assessment.assessment_type == 'WRITTEN_WORKS':
                written_works_marks.append(
                    sa.obtained_marks/sa.assessment.max_marks)
                if written_weightage == 0:
                    written_weightage = sa.assessment.subject.written_work / 100
            if sa.assessment.assessment_type == 'PERFORMANCE_TASK':
                performance_tasks_marks.append(
                    sa.obtained_marks/sa.assessment.max_marks)
                if performance_task_weightage == 0:
                    performance_task_weightage = sa.assessment.subject.performance_task / 100
            if sa.assessment.assessment_type == 'QUARTERLY_ASSESSMENT':
                quarterly_assessments_marks.append(
                    sa.obtained_marks/sa.assessment.max_marks)
                if quarterly_assessment_weightage == 0:
                    quarterly_assessment_weightage = sa.assessment.subject.quartery_assessment / 100

        written_works = {"weightage": written_weightage,
                         "obtained_marks": written_works_marks, }
        performance_tasks = {"weightage": performance_task_weightage,
                             "obtained_marks": performance_tasks_marks, }
        quarterly_assessments = {
            "weightage": quarterly_assessment_weightage, "obtained_marks": quarterly_assessments_marks, }

        my_gap = gpa_calculate(
            written_works, performance_tasks, quarterly_assessments)

        # Modify the response data to include the average GPA
        response.data['gpa'] = my_gap
        return response
