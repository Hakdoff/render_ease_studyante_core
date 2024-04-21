
from rest_framework import generics, permissions, response, status, exceptions

from core.paginate import ExtraSmallResultsSetPagination
from .serializers import ParentStudentListSerializers
from .models import Schedule, AcademicYear
from registration.models import Registration


class ParentStudentListView(generics.RetrieveAPIView):
    serializer_class = ParentStudentListSerializers
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
