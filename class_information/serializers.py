from rest_framework import serializers
from .models import Department, Section, Subject


class DepartmentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('__all__')


class SectionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Section
        exclude = ['created_at', 'updated_at']


class SubjectSerializers(serializers.ModelSerializer):
    department = DepartmentSerializers()

    class Meta:
        model = Subject
        exclude = ['created_at', 'updated_at']
