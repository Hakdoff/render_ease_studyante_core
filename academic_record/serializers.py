from datetime import datetime
from rest_framework import serializers

from class_information.serializers import SectionSerializers, SubjectSerializers
from user_profile.models import Parent
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


class TimeOutSerializers(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = ['pk', 'time_in', 'time_out',
                  'is_present', 'attendance_date',]


class TimeOutAttendanceSerializers(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_ids = serializers.ListField(write_only=True)

    class Meta:
        model = Registration
        fields = ['student', 'student_ids',]

        extra_kwargs = {
            'student_ids': {'required': True, 'write_only': True},
            'schedule_id': {'required': True, 'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(TimeOutAttendanceSerializers, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        data = super(TimeOutAttendanceSerializers,
                     self).to_representation(instance)
        if self.request:
            schedule_id = ''

            if self.request.GET:
                # get params from GET method
                schedule_id = self.request.GET.get('schedule_id', None)

            if self.request.POST:
                # get params from POST method
                schedule_id = self.request.query_params('schedule_id', None)

            schedule = Schedule.objects.get(pk=schedule_id)

            if "student" in data:
                student = data['student']
                current_date = datetime.now()
                attendances = Attendance.objects.filter(
                    student__pk=student['pk'], attendance_date=current_date, schedule=schedule,)

                attendace = None

                if attendances.exists():
                    serializer = TimeOutSerializers(attendances.first())
                    attendace = serializer.data
                data['attendance'] = attendace
        return data


class ParentStudentListSerializers(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = ['__all__']
