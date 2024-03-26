from rest_framework import generics, permissions
from .serializers import RegisterSerializers
from .models import Registration


class RegisteredStudentListView(generics.ListAPIView):
    serializer_class = RegisterSerializers
    queryset = Registration.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        section = self.request.GET.get('section', None)
        if section:
            return Registration.objects.filter(section__pk=section).order_by('student__user__lastname')
        return super().get_queryset()
