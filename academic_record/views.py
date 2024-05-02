from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions,  status, viewsets, response, filters

from academic_record.custom_filter_assessment import CustomFilterAssessment, CustomFilterStudentAssessment
from academic_record.gpa_caluclate import gpa_calculate
from academic_record.uuid_checker import is_valid_uuid
from aes.aes_implementation import decrypt
from class_information.models import Subject
from core.paginate import ExtraSmallResultsSetPagination
from ease_studyante_core import settings
from user_profile.models import  Student, Teacher
from .serializers import (StudentAssessmentSerializers, TeacherScheduleSerialzers, AttendanceSerializers,
                           AssessmentSerializers, TimeOutAttendanceSerializers)
from .models import Schedule, AcademicYear, Attendance, StudentAssessment, Assessment
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
        # student will be aes 256
        student = request.data.get('student', None)
        academic_years = AcademicYear.objects.all()

        aes_256_split = student.split('$')

        temp_encrpyted = {
            'cipher_text': aes_256_split[0],
            'salt': aes_256_split[1],
            'nonce': aes_256_split[2],
            'tag': aes_256_split[3]
        }

        decrypted = decrypt(temp_encrpyted, settings.AES_SECRET_KEY)
        student = bytes.decode(decrypted)

        if is_valid_uuid(student):
            if academic_years.exists():
                register_students = Registration.objects.filter(
                    student__pk=student, academic_year=academic_years.first())

            if register_students.exists():
                teacher = self.request.user
                register_student = register_students.first()
                schedules = Schedule.objects.filter(
                    teacher__user__pk=teacher.pk, section__pk=register_student.section.pk)
                current_date = datetime.now()
                attendance = None

                if schedules.exists():
                    schedule = schedules.first()
                    attendances = Attendance.objects.filter(
                        student__pk=register_student.student.pk, time_in__date=current_date, schedule=schedule)

                    if not attendances.exists():

                        attendance = Attendance.objects.create(
                            student=register_student.student, schedule=schedule, is_present=True)

                        serializer = AttendanceSerializers(attendance)
                        return Response(serializer.data)
                    else:
                        attendance = attendances.first()

                serializer = AttendanceSerializers(attendance)
                serializer_data = serializer.data
                error = {
                    "error_message": "Student already time in",
                }
                serializer_data.update(error)

                return Response(data=serializer_data, status=status.HTTP_200_OK)
            else:
                error = {
                    "error_message": "Student not yet register.",
                }
                return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
        error = {
            "error_message": "QR Code is invalid",
        }
        return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class TeacherStudentAssessmentListView(generics.ListAPIView):
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




class TeacherAssessmentListView(generics.ListAPIView):
    serializer_class = AssessmentSerializers
    queryset = Assessment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [CustomFilterAssessment, filters.OrderingFilter]
    ordering_fileds = ['name',]

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()
        if academic_years.exists():
            user = self.request.user
            teacher = get_object_or_404(Teacher, user=user)

            current_academic = academic_years.first()

            return self.queryset.filter(
                academic_year=current_academic, teacher=teacher)
        return []


class TeacherAssessmentStudentListView(generics.ListAPIView):
    serializer_class = StudentAssessmentSerializers
    queryset = StudentAssessment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [CustomFilterStudentAssessment]

    def get_queryset(self):
        section_id = self.request.GET.get('section_id', None)
        subject_id = self.request.GET.get('subject_id', None)

        academic_years = AcademicYear.objects.all()
        if academic_years.exists():
            user = self.request.user
            teacher = get_object_or_404(Teacher, user=user)
            schedules = Schedule.objects.filter(
                section__pk=section_id, teacher=teacher, subject__pk=subject_id)

            if schedules.exists():
                schedule = schedules.first()
                current_academic = academic_years.first()
                students = Registration.objects.filter(
                    section=schedule.section).values('student')

                return self.queryset.filter(
                    assessment__academic_year=current_academic,  assessment__teacher=teacher, student__in=students)
        return []


class StudentAssessmentUpdateOrCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract the IDs from the request data
        student_assessment_id = request.data.get('id')
        assessment_id = request.data.get('assessment_id')
        student_id = request.data.get('student_id')
        obtained_marks = request.data.get('obtained_marks')

        # Create the StudentAssessment instance
        student = Student.objects.get(pk=student_id)
        assessment = Assessment.objects.get(pk=assessment_id)

        if student_assessment_id == "-1":
            # CREATE ASSESSMET
            student_assessment = StudentAssessment.objects.create(
                student=student, assessment=assessment, obtained_marks=obtained_marks)
            serializer = StudentAssessmentSerializers(student_assessment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        student_assessments = StudentAssessment.objects.filter(
            pk=student_assessment_id,
            student=student, assessment=assessment)
        student_assessments.update(obtained_marks=obtained_marks)

        serializer = StudentAssessmentSerializers(
            student_assessments.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherAttendaceListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeOutAttendanceSerializers
    queryset = Registration.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
            schedule_id = self.request.GET.get('schedule_id', None)
            academic_year = academic_years.first()
            schedule = get_object_or_404(Schedule, pk=schedule_id)

            return self.queryset.filter(section=schedule.section, academic_year=academic_year)

        return []

    def get_serializer_context(self):
        """
        Add request to serializer context
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        student_ids = request.data.get('student_ids', None)
        schedule_id = request.GET.get('schedule_id', None)
        current_date = datetime.now()
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        is_created = True if student_ids else False

        time_out_students = []

        for student_id in student_ids:
            attendances = Attendance.objects.filter(
                student__pk=student_id, time_in__date=current_date, schedule=schedule)
            if attendances.exists():
                attendance = attendances.first()
                if not attendance.time_out and attendance.is_present:
                    attendance.time_out = current_date
                    attendance.save()
            else:
                student = get_object_or_404(Student, pk=student_id)
                Attendance.objects.create(
                    student=student, schedule=schedule, is_present=False, time_in=None)
            time_out_students.append(student_id)

        serializer = TimeOutAttendanceSerializers(Registration.objects.filter(
            student__pk__in=time_out_students), many=True, context={'request': request})

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED if is_created else status.HTTP_200_OK)
