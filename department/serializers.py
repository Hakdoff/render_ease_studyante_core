from rest_framework import serializers
from .models import Department


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['pk', 'name', 'acronym']
