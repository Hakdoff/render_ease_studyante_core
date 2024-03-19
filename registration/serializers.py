from rest_framework import serializers

from user_profile.serializers import StudentSerializer
from .models import Registration


class RegisterSerializers(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = Registration
        fields = ['student']
