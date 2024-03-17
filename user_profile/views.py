from django.shortcuts import render
from rest_framework import generics, permissions, response, status

from .serializers import StudentSerializer, TeacherSerializer
from .models import Parent, Teacher, Student


class StudentProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = Student.objects.filter(user=user)

        if user_profiles.exists():
            user_profile = user_profiles.first()

            data = {
                "pk": str(user.pk),
                "profilePk": str(user_profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "address": user_profile.address,
                "contactNumber": user_profile.contact_number,
                "gender": user_profile.gender,
                "age": user_profile.age,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,

            }

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Please setup your profile"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)


class TeacherProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeacherSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = Teacher.objects.filter(user=user)

        if user_profiles.exists():
            user_profile = user_profiles.first()

            data = {
                "pk": str(user.pk),
                "profilePk": str(user_profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "department": user_profile.department.name,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,

            }

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Please setup your profile"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)


class ParentProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = Teacher.objects.filter(user=user)

        if user_profiles.exists():
            user_profile = user_profiles.first()

            data = {
                "pk": str(user.pk),
                "profilePk": str(user_profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "department": user_profile.department.name,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,

            }

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Please setup your profile"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)
