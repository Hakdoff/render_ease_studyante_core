from django.urls import path
from rest_framework.routers import DefaultRouter

from class_information.views import DepartmentListCreateView
from user_profile.views import ChangePasswordView, RequestPasswordResetEmail, StudentProfileView, TeacherProfileView, ParentProfileView
from academic_record.views import (
    TeacherScheduleListView, AttendanceTeacherViewSet, TeacherStudentAssessmentListView,
    AttendanceTeacherListView, TeacherStudentOverAllGPAView, TeacherSearchStudentChatListView,
    TeacherAssessmentListView, TeacherAssessmentStudentListView, StudentAssessmentUpdateOrCreateView,
    TeacherAttendaceListCreateView)
from academic_record.student_views import (
    StudentScheduleListView, StudentAttendanceListView, StudentAttendanceRetrieveView, StudentAssessmentListView, StudentOverAllGPAView,
    StudentChatTeacherListView)
from registration.views import RegisteredStudentListView
from django.contrib.auth import views as auth_views

app_name = 'api'

router = DefaultRouter()
router.register(r'qr_code', AttendanceTeacherViewSet,
                basename='student-attendance')

urlpatterns = router.urls

urlpatterns += [
    path('change-password', ChangePasswordView.as_view(), name='change-password'),

    path('forgot-password', RequestPasswordResetEmail.as_view(),
         name='forgot-password '),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),


    # DEPARTMENT
    path('department/list/<pk>', DepartmentListCreateView.as_view(),
         name='department'),

    # Student
    path('student/profile', StudentProfileView.as_view(),
         name='student-profile'),
    path('student/schedule', StudentScheduleListView.as_view(),
         name='student-schedule'),
    path('student/attendance', StudentAttendanceListView.as_view(),
         name='student-attendance'),
    path('student/attendance/<pk>', StudentAttendanceRetrieveView.as_view(),
         name='student-attendance-detail'),
    path('student/assessments', StudentAssessmentListView.as_view(),
         name='student-assessments'),
    path('student/over-all', StudentOverAllGPAView.as_view(),
         name='student-gpa'),
    path('student/chat-list', StudentChatTeacherListView.as_view(),
         name='student-chat-list'),



    # Teacher
    path('teacher/profile', TeacherProfileView.as_view(),
         name='teacher-profile'),
    path('teacher/schedules', TeacherScheduleListView.as_view(),
         name='teacher-schedules'),
    path('teacher/registered/students', RegisteredStudentListView.as_view(),
         name='teacher-registered-students'),
    path('teacher/assessments', TeacherStudentAssessmentListView.as_view(),
         name='teacher-assessments'),
    path('teacher/student/assessments', TeacherAssessmentStudentListView.as_view(),
         name='teacher-assessments-student'),
    path('teacher/web/assessments', TeacherAssessmentListView.as_view(),
         name='teacher-web-assessments'),
    path('teacher/attendance/timeout', TeacherAttendaceListCreateView.as_view(),
         name='teacher-attendance-timeout'),
    path('teacher/students/attendance', AttendanceTeacherListView.as_view(),
         name='teacher-students-attendance'),
    path('teacher/student/over-all-gpa', TeacherStudentOverAllGPAView.as_view(),
         name='teacher-student-gpa'),
    path('teacher/chat-list', TeacherSearchStudentChatListView.as_view(),
         name='teacher-chat-list'),
    path('teacher/update-create-student-assessment', StudentAssessmentUpdateOrCreateView.as_view(),
         name='update-create-student-assessment'),



    # Parent
    path('parent/profile', ParentProfileView.as_view(),
         name='parent-profile'),
]
