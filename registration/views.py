from rest_framework import generics, permissions, filters
from .serializers import RegisterSerializers
from .models import Registration


class RegisteredStudentListView(generics.ListAPIView):
    serializer_class = RegisterSerializers
    queryset = Registration.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__user__first_name', 'student__user__last_name',]

    def get_queryset(self):
        section = self.request.GET.get('section', None)
        if section:
            return self.queryset.filter(section__pk=section).order_by('student__user__lastname')
        return super().get_queryset()
