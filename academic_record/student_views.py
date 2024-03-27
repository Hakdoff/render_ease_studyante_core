from decimal import Decimal
from rest_framework import generics, permissions, response, status, exceptions

from academic_record.gpa_caluclate import gpa_calculate
from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (StudentScheduleSerialzers,
                          AttendanceSerializers, StudentAssessmentSerializers)
from .models import Schedule, AcademicYear, Attendance, StudentAssessment
from class_information.models import Subject
from registration.models import Registration
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.shortcuts import get_object_or_404


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
                # check wether complete subjects
                # set is_view_grade = true to display grades
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


class StudentOverAllGPAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_calculate_gap(self, student_assessments):

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

        return gpa_calculate(
            written_works, performance_tasks, quarterly_assessments)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'subject_id',
                openapi.IN_QUERY,
                description='Pass subject id to calculate overall subject gpa otherwise will return student gpa not found',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        user = self.request.user
        academic_years = AcademicYear.objects.all()
        subject_id = request.query_params.get('subject_id', None)

        if academic_years.exists():
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=user.pk)

            if register_users.exists():
                register_user = register_users.first()
                first_grading_assessments = None
                second_grading_assessments = None
                third_grading_assessments = None
                fourth_grading_assessments = None

                if subject_id:
                    subject = get_object_or_404(Subject, pk=subject_id)
                    schedule = Schedule.objects.get(
                        academic_year=current_academic, subject=subject, section=register_user.section)

                    if schedule.is_view_grade:
                        first_grading_assessments = StudentAssessment.objects.filter(
                            assessment__academic_year=current_academic, assessment__grading_period='FIRST_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                        second_grading_assessments = StudentAssessment.objects.filter(
                            assessment__academic_year=current_academic, assessment__grading_period='SECOND_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                        third_grading_assessments = StudentAssessment.objects.filter(
                            assessment__academic_year=current_academic, assessment__grading_period='THIRD_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                        fourth_grading_assessments = StudentAssessment.objects.filter(
                            assessment__academic_year=current_academic, assessment__grading_period='FOURTH_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')

                        data = {
                            'first_grading': self.get_calculate_gap(first_grading_assessments),
                            'second_grading': self.get_calculate_gap(second_grading_assessments),
                            'third_grading': self.get_calculate_gap(third_grading_assessments),
                            'fourth_grading': self.get_calculate_gap(fourth_grading_assessments),
                        }
                        if not 'N/A' in data.values():
                            temp_total_gpa = 0
                            for value in data.values():
                                temp_total_gpa += float(value)
                            temp_total_gpa = temp_total_gpa / \
                                len(data.values())
                            data['total_gpa'] = str(round(temp_total_gpa, 2))
                        else:
                            data['total_gpa'] = 'N/A'
                        data['is_view_grade'] = True

                    else:
                        data = {
                            'first_grading': 'N/A',
                            'second_grading': 'N/A',
                            'third_grading': 'N/A',
                            'fourth_grading': 'N/A',
                            'is_view_grade': False
                        }
                    return response.Response(data, status=status.HTTP_200_OK)

        data = {'error_message': 'Student GPA not found'}

        return response.Response(data, status=status.HTTP_400_BAD_REQUEST)
