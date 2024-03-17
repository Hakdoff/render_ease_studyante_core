from rest_framework import generics, permissions
from .serializers import ScheduleSerialzers
from .models import Schedule, AcademicYear


class TeacherScheduleListView(generics.ListAPIView):
    serializer_class = ScheduleSerialzers
    queryset = Schedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = []

        academic_years = AcademicYear.objects.all()

        if academic_years.exists():
            user = self.request.user
            current_academic = academic_years.first()
            return Schedule.objects.filter(academic_year=current_academic, teacher__user__pk=user.pk)

        return queryset
