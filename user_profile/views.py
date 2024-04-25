from rest_framework import generics, permissions, response, status

from academic_record.models import AcademicYear
from base.models import User
from class_information.models import GradeEncode
from user_profile.email import Util

from .serializers import ChangePasswordSerializer, ParentSerializer, ResetPasswordEmailRequestSerializer, StudentOnlySerializer, StudentSerializer, TeacherSerializer
from .models import Parent, Teacher, Student
from registration.models import Registration
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.sites.shortcuts import get_current_site
import re


class StudentProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = Student.objects.filter(user=user)
        academic_years = AcademicYear.objects.all()

        if user_profiles.exists() and academic_years.exists():
            user_profile = user_profiles.first()
            register_users = Registration.objects.filter(
                student=user_profile, academic_year=academic_years.first())

            if register_users.exists():
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
                    "is_new_user": user_profile.user.is_new_user,

                }

                return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Student not found"
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
            academic_years = AcademicYear.objects.all()
            grade_encodes = GradeEncode.objects.all()

            grading_periods = []

            if academic_years.exists() and grade_encodes.exists():
                academic_year = academic_years.first()
                for grade_encode in grade_encodes:
                    if grade_encode.grading_period == "FIRST_GRADING":
                        period = {
                            "grading_deadline": academic_year.first_grading_dealine,
                            "is_override_encoding": grade_encode.is_enable,
                            "grading_period": grade_encode.grading_period
                        }
                    if grade_encode.grading_period == "SECOND_GRADING":
                        period = {
                            "grading_deadline": academic_year.second_grading_dealine,
                            "is_override_encoding": grade_encode.is_enable,
                            "grading_period": grade_encode.grading_period
                        }
                    if grade_encode.grading_period == "THIRD_GRADING":
                        period = {
                            "grading_deadline": academic_year.third_grading_dealine,
                            "is_override_encoding": grade_encode.is_enable,
                            "grading_period": grade_encode.grading_period
                        }
                    if grade_encode.grading_period == "FOURTH_GRADING":
                        period = {
                            "grading_deadline": academic_year.fourth_grading_dealine,
                            "is_override_encoding": grade_encode.is_enable,
                            "grading_period": grade_encode.grading_period
                        }

                    grading_periods.append(period)

            data = {
                "pk": str(user.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "department": user_profile.department.name,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,
                "is_new_user": user_profile.user.is_new_user,
                "grading_periods": grading_periods,
            }

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Teacher not found"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)


class ParentProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ParentSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = Parent.objects.filter(user=user)

        if user_profiles.exists():
            user_profile = user_profiles.first()

            data = {
                "pk": str(user.pk),
                "profilePk": str(user_profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,
                "is_new_user": user_profile.user.is_new_user,
            }

            students_serializer = StudentOnlySerializer(
                user_profile.students, many=True)
            data["students"] = students_serializer.data

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Parent not "
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return response.Response({"error_message": "Wrong old password."}, status=status.HTTP_400_BAD_REQUEST)
            new_password_entry = serializer.data.get("new_password")
            reg = "[^\w\d]*(([0-9]+.*[A-Za-z]+.*)|[A-Za-z]+.*([0-9]+.*))"
            pat = re.compile(reg)

            if 8 <= len(new_password_entry) <= 16:
                password_validation = re.search(pat, new_password_entry)
                if password_validation:
                    self.object.set_password(
                        serializer.data.get("new_password"))
                    self.object.is_new_user = False
                else:
                    return response.Response({"error_message":
                                              "Password must contain a combination of letters and numbers"},
                                             status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response({"error_message":
                                          "Password must contain at least 8 to 16 characters"},
                                         status=status.HTTP_400_BAD_REQUEST)

            self.object.save()
            data = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return response.Response(data)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmail(generics.CreateAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = []

    def post(self, request):
        email_address = request.data.get('email_address', '')
        check_identity = User.objects.filter(email__exact=email_address)
        if check_identity.exists():
            identity = check_identity.first()
            uidb64 = urlsafe_base64_encode(smart_bytes(identity.id))
            token = PasswordResetTokenGenerator().make_token(identity)

            relative_link = reverse(
                'api:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            current_site = get_current_site(
                request=request).domain
            abs_url: str = f"https://{current_site}{relative_link}"

            context_email = {
                "url": abs_url,
                "full_name": f"{identity.first_name} {identity.last_name}"
            }
            message = get_template(
                'forgot_password/index.html').render(context_email)

            context = {
                'email_body': message,
                'to_email': identity.email,
                'email_subject': 'Password Reset Confirmation'
            }

            Util.send_email(context)
        else:
            return response.Response({'error_message': 'Email not found!'}, status=status.HTTP_404_NOT_FOUND)

        return response.Response(
            {'success': 'We have sent you a link to reset your password'},
            status=status.HTTP_200_OK
        )
