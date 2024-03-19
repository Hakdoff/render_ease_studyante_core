
from rest_framework import serializers

from class_information.serializers import SectionSerializers, SubjectSerializers
from user_profile.serializers import StudentSerializer, TeacherSerializer
from .models import AcademicYear, Schedule, Attendance


class AcademicYearSerializers(serializers.Serializer):
    class Meta:
        model = AcademicYear
        exclude = ['created_at', 'updated_at']


class TeacherScheduleSerialzers(serializers.ModelSerializer):
    subject = SubjectSerializers()
    academic_year = AcademicYearSerializers()
    section = SectionSerializers()

    class Meta:
        model = Schedule
        exclude = ['created_at', 'updated_at']


class StudentScheduleSerialzers(serializers.ModelSerializer):
    subject = SubjectSerializers()
    academic_year = AcademicYearSerializers()
    teacher = TeacherSerializer()
    section = SectionSerializers()

    class Meta:
        model = Schedule
        exclude = ['created_at', 'updated_at']


class AttendanceSerializers(serializers.ModelSerializer):
    schedule = StudentScheduleSerialzers(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Attendance
        exclude = ['created_at', 'updated_at']
