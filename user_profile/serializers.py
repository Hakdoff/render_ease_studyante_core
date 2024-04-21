from rest_framework import serializers

from base.models import User
from .models import Teacher, Student, Parent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'username',
            'get_full_name',
            'is_new_user'
        )

        extra_kwargs = {
            'username': {
                'read_only': True
            },
        }


class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Parent
        fields = ('user', 'address',
                  'contact_number',
                  'age',
                  'gender',
                  'profile_photo',)


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'pk',
            'user',
            'address',
            'contact_number',
            'age',
            'gender',
            'profile_photo',
            'year_level',
            'qr_code_photo',
            'parent',
        )

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(StudentSerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        photo_url = data.profile_photo.url
        return request.build_absolute_uri(photo_url)

    def get_parent(self, instance):
        parents = Parent.objects.filter(students__pk=instance.pk)
        if parents.exists():
            parent_serializer = ParentSerializer(parents.first())
            return parent_serializer.data
        else:
            return None


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = (
            'pk',
            'user',
            'department',
            'profile_photo',
        )

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(TeacherSerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        photo_url = data.profile_photo.url
        return request.build_absolute_uri(photo_url)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email_address = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email_address']


class StudentOnlySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = (
            'pk',
            'user',
            'address',
            'contact_number',
            'age',
            'gender',
            'profile_photo',
            'year_level',
            'qr_code_photo',
        )

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(StudentOnlySerializer, self).__init__(*args, **kwargs)

    def get_profile_photo(self, data):
        request = self.context.get('request')
        photo_url = data.profile_photo.url
        return request.build_absolute_uri(photo_url)
