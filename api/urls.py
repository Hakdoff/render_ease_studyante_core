from django.urls import path
from rest_framework.routers import DefaultRouter

from class_information.views import DepartmentListCreateView
from user_profile.views import StudentProfileView, TeacherProfileView, ParentProfileView
from academic_record.views import (
    TeacherScheduleListView, AttendanceTeacherViewSet)
from academic_record.student_views import (
    StudentScheduleListView, StudentAttendanceListView, StudentAttendanceRetrieveView)
from registration.views import RegisteredStudentListView

app_name = 'api'

router = DefaultRouter()
router.register(r'teacher/students/attendance', AttendanceTeacherViewSet,
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



    # Teacher
    path('teacher/profile', TeacherProfileView.as_view(),
         name='teacher-profile'),
    path('teacher/schedules', TeacherScheduleListView.as_view(),
         name='teacher-schedules'),
    path('teacher/registered/students', RegisteredStudentListView.as_view(),
         name='teacher-registered-students'),



    # Parent Profile
    path('parent/profile', ParentProfileView.as_view(),
         name='parent-profile'),
]
