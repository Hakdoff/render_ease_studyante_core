from datetime import datetime
from rest_framework import generics, permissions,  status, viewsets

from academic_record.gpa_caluclate import gpa_calculate
from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (StudentAssessmentSerializers,
                          TeacherScheduleSerialzers, AttendanceSerializers)
from .models import Schedule, AcademicYear, Attendance, StudentAssessment
from registration.models import Registration
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


class AttendanceTeacherViewSet(viewsets.ViewSet):
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
        ]
    )
    def list(self, request):
        academic_years = AcademicYear.objects.all()
        student = request.query_params.get('student_id', None)
        attendance = []
        user = self.request.user

        if academic_years.exists():
            register_students = Registration.objects.filter(
                student__user__pk=student, academic_year=academic_years.first())
            if register_students.exists():
                if student:
                    attendance = Attendance.objects.filter(
                        schedule__teacher__user__pk=user.pk, student=register_students.first().student).order_by('-attendance_date', '-time_in')
            else:
                attendance = Attendance.objects.filter(
                    schedule__teacher__user__pk=user.pk).order_by('-attendance_date', '-time_in')

        serializer = AttendanceSerializers(attendance, many=True)

        return Response(serializer.data)

    def create(self, request):
        student = request.data.get('student', None)
        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
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
            "error_message": "Student not found",
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
