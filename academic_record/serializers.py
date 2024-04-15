
from rest_framework import serializers

from class_information.serializers import SectionSerializers, SubjectSerializers
from user_profile.serializers import StudentSerializer, TeacherSerializer
from .models import AcademicYear, Schedule, Attendance, Assessment, StudentAssessment
from registration.models import Registration


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


class AssessmentSerializers(serializers.ModelSerializer):
    academic_year = AcademicYearSerializers()
    teacher = TeacherSerializer()
    subject = SubjectSerializers()

    class Meta:
        model = Assessment
        exclude = ['updated_at']


class StudentAssessmentSerializers(serializers.ModelSerializer):
    assessment = AssessmentSerializers()
    student = StudentSerializer()

    class Meta:
        model = StudentAssessment
        fields = ['pk', 'assessment',
                  'obtained_marks', 'student', 'created_at']

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(StudentAssessmentSerializers, self).__init__(*args, **kwargs)


class TeacherChatSerialzers(serializers.ModelSerializer):
    teacher = TeacherSerializer()

    class Meta:
        model = Schedule
        fields = ['teacher',]

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(TeacherChatSerialzers, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        data = super(TeacherChatSerialzers,
                     self).to_representation(instance)

        department_id = data['teacher']['department']
        data['teacher']['department'] = str(department_id)
        return data


class StudentRegisterSerializers(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ['student',]
