from django.urls import path
from rest_framework.routers import DefaultRouter

from class_information.views import DepartmentListCreateView
from user_profile.views import StudentProfileView, TeacherProfileView, ParentProfileView
from academic_record.views import (
    TeacherScheduleListView, AttendanceTeacherViewSet, TeacherAssessmentListView, AttendanceTeacherListView)
from academic_record.student_views import (
    StudentScheduleListView, StudentAttendanceListView, StudentAttendanceRetrieveView, StudentAssessmentListView, StudentOverAllGPAView)
from registration.views import RegisteredStudentListView

app_name = 'api'

router = DefaultRouter()
router.register(r'qr_code', AttendanceTeacherViewSet,
                basename='student-attendance')

urlpatterns = router.urls

urlpatterns += [
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



    # Teacher
    path('teacher/profile', TeacherProfileView.as_view(),
         name='teacher-profile'),
    path('teacher/schedules', TeacherScheduleListView.as_view(),
         name='teacher-schedules'),
    path('teacher/registered/students', RegisteredStudentListView.as_view(),
         name='teacher-registered-students'),
    path('teacher/assessments', TeacherAssessmentListView.as_view(),
         name='teacher-assessments'),
    path('teacher/students/attendance', AttendanceTeacherListView.as_view(),
         name='teacher-students-attendance'),


    # Parent Profile
    path('parent/profile', ParentProfileView.as_view(),
         name='parent-profile'),
]
