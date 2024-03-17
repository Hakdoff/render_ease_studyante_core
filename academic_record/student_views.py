from rest_framework import generics, permissions, response, status, viewsets

from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (StudentScheduleSerialzers, AttendanceSerializers)
from .models import Schedule, AcademicYear, Attendance
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

        error = {
            "error_message": "Student not found"
        }

        return response.Response(error, status=status.HTTP_404_NOT_FOUND)


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
                return Attendance.objects.filter(student=register_user.student.pk).order_by('date')

        error = {
            "error_message": "Student not found"
        }

        return response.Response(error, status=status.HTTP_404_NOT_FOUND)


class StudentAttendanceRetrieveView(generics.RetrieveAPIView):
    serializer_class = AttendanceSerializers
    queryset = Attendance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
