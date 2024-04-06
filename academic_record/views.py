from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions,  status, viewsets, response

from academic_record.gpa_caluclate import gpa_calculate
from academic_record.uuid_checker import is_valid_uuid
from class_information.models import Subject
from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (StudentAssessmentSerializers,
                          TeacherScheduleSerialzers, AttendanceSerializers, StudentRegisterSerializers)
from .models import Schedule, AcademicYear, Attendance, StudentAssessment
from registration.models import Registration
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from reedsolo import RSCodec, ReedSolomonError
from registration.models import Registration
from django.db.models import Q
import uuid


class TeacherScheduleListView(generics.ListAPIView):
    serializer_class = TeacherScheduleSerialzers
    queryset = Schedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        queryset = []

        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
            user = self.request.user
            current_academic = academic_years.first()
            return Schedule.objects.filter(academic_year=current_academic, teacher__user__pk=user.pk)

        return queryset


class AttendanceTeacherListView(generics.ListAPIView):
    serializer_class = AttendanceSerializers
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student_id',
                openapi.IN_QUERY,
                description='Add student id to filter specific attendance otherwise will display all attendance',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'subject_id',
                openapi.IN_QUERY,
                description='Add subject id to filter specific attendance otherwise will display all attendance',
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def get_queryset(self):
        academic_years = AcademicYear.objects.all()
        student = self.request.GET.get('student_id', None)
        subject = self.request.GET.get('subject_id', None)

        attendance = []
        user = self.request.user

        if academic_years.exists():
            register_students = Registration.objects.filter(
                student__user__pk=student, academic_year=academic_years.first())
            if register_students.exists():
                if student and subject:
                    attendance = Attendance.objects.filter(
                        schedule__teacher__user__pk=user.pk, schedule__subject__pk=subject, student=register_students.first().student).order_by('-attendance_date', '-time_in')
            else:
                attendance = Attendance.objects.filter(
                    schedule__teacher__user__pk=user.pk).order_by('-attendance_date', '-time_in')

        return attendance


class AttendanceTeacherViewSet(viewsets.ViewSet):
    serializer_class = AttendanceSerializers
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def create(self, request):
        student = request.data.get('student', None)
        academic_years = AcademicYear.objects.all()

        if is_valid_uuid(student):
            if academic_years.exists():
                # rsc = RSCodec(10)
                # student_id = rsc.decode( bytearray. )[0]
                register_students = Registration.objects.filter(
                    student__user__pk=student, academic_year=academic_years.first())

            if register_students.exists():
                teacher = self.request.user
                register_student = register_students.first()
                schedules = Schedule.objects.filter(
                    teacher__user__pk=teacher.pk, section__pk=register_student.section.pk)
                current_date = datetime.now()

                attendances = Attendance.objects.filter(
                    student__pk=register_student.student.pk, time_in__date=current_date)

                if schedules.exists() and not attendances.exists():
                    schedule = schedules.first()

                    attendance = Attendance.objects.create(
                        student=register_student.student, schedule=schedule, is_present=True)

                    serializer = AttendanceSerializers(attendance)

                    return Response(serializer.data)
                serializer = AttendanceSerializers(attendances.first())
                serializer_data = serializer.data
                error = {
                    "error_message": "Student already time in",
                }
                serializer_data.update(error)

                return Response(data=serializer_data, status=status.HTTP_200_OK)
        error = {
            "error_message": "QR Code is invalid",
        }
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class TeacherAssessmentListView(generics.ListAPIView):
    serializer_class = StudentAssessmentSerializers
    queryset = StudentAssessment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()
        grading_period = self.request.GET.get('grading_period', None)
        student_id = self.request.GET.get('student_id', None)

        if academic_years.exists() and grading_period and student_id:
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=student_id)

            if register_users.exists():
                # check the user wether is register to current academic or not
                register_user = register_users.first()
                return StudentAssessment.objects.filter(assessment__academic_year=current_academic, assessment__grading_period=grading_period, student=register_user.student,
                                                        assessment__teacher__user__pk=user.pk).order_by('created_at', 'assessment__grading_period')

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


class TeacherStudentOverAllGPAView(APIView):
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
                'student_id',
                openapi.IN_QUERY,
                description='Pass student_id to get student record, otherwise will return student gpa not found',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'subject_id',
                openapi.IN_QUERY,
                description='Pass subject id of the student to calculate overall subject gpa otherwise will return student gpa not found',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        user = self.request.user
        academic_years = AcademicYear.objects.all()
        subject_id = request.query_params.get('subject_id', None)
        student_id = request.query_params.get('student_id', None)

        if academic_years.exists() and subject_id and student_id:
            user = self.request.user
            current_academic = academic_years.first()
            register_users = Registration.objects.filter(
                academic_year=current_academic, student__user__pk=student_id)

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

                    first_grading_assessments = StudentAssessment.objects.filter(
                        assessment__teacher__user__pk=user.pk,
                        assessment__academic_year=current_academic, assessment__grading_period='FIRST_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                    second_grading_assessments = StudentAssessment.objects.filter(
                        assessment__teacher__user__pk=user.pk,
                        assessment__academic_year=current_academic, assessment__grading_period='SECOND_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                    third_grading_assessments = StudentAssessment.objects.filter(
                        assessment__teacher__user__pk=user.pk,
                        assessment__academic_year=current_academic, assessment__grading_period='THIRD_GRADING', student=register_user.student, assessment__subject__pk=subject_id).order_by('created_at', 'assessment__grading_period')
                    fourth_grading_assessments = StudentAssessment.objects.filter(
                        assessment__teacher__user__pk=user.pk,
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

                    return response.Response(data, status=status.HTTP_200_OK)

        data = {'error_message': 'Student GPA not found'}

        return response.Response(data, status=status.HTTP_400_BAD_REQUEST)


class TeacherSearchStudentChatListView(generics.ListAPIView):
    serializer_class = StudentRegisterSerializers
    queryset = Registration.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='Query params for student search it will be based on surname',
                type=openapi.TYPE_STRING
            )
        ],
        operation_id='list_students'
    )
    def get_queryset(self):
        q = self.request.GET.get('q', None)

        user = self.request.user
        schedules = Schedule.objects.filter(
            teacher__user=user).values('section')

        if schedules.exists() and q:
            return Registration.objects.filter(Q(section__pk__in=schedules) & Q(Q(student__user__first_name__icontains=q) | Q(student__user__last_name__icontains=q))).order_by('student__user__lastname')

        return []
