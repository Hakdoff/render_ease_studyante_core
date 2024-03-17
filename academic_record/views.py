from rest_framework import generics, permissions, response, status, viewsets

from core.paginate import ExtraSmallResultsSetPagination
from .serializers import (TeacherScheduleSerialzers, AttendanceSerializers)
from .models import Schedule, AcademicYear, Attendance
from registration.models import Registration


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
                serializer = UserSerializer(queryset, many=True)
                return Response(serializer.data)

        return []
