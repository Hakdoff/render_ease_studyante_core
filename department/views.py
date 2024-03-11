from rest_framework import generics, permissions
from .serializers import DepartmentSerializers
from .models import Department


class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializers
    queryset = Department.objects.all()
    permission_classes = []
