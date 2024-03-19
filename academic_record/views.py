from datetime import datetime
from rest_framework import generics, permissions, response, status, viewsets

from core.paginate import ExtraSmallResultsSetPagination
from user_profile.models import Teacher
from .serializers import (TeacherScheduleSerialzers, AttendanceSerializers)
from .models import Schedule, AcademicYear, Attendance
from registration.models import Registration
from rest_framework.response import Response


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

    def list(self, request):
        user = self.request.user
        attendance = Attendance.objects.filter(
            schedule__teacher__user__pk=user.pk)
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
                student__pk=register_student.student.pk, date_attend__date=current_date)

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
