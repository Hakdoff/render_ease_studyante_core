from django.urls import path

from class_information.views import DepartmentListCreateView
from user_profile.views import StudentProfileView, TeacherProfileView, ParentProfileView
from academic_record.views import TeacherScheduleListView

app_name = 'api'


urlpatterns = [
    # DEPARTMENT
    path('department-list/<pk>', DepartmentListCreateView.as_view(),
         name='department-list'),


    # Student Profile
    path('student-profile', StudentProfileView.as_view(),
         name='student-profile'),

    # Teacher
    path('teacher-profile', TeacherProfileView.as_view(),
         name='teacher-profile'),
    path('teacher/schedules', TeacherScheduleListView.as_view(),
         name='teacher-schedules'),


    # Parent Profile
    path('parent-profile', ParentProfileView.as_view(),
         name='parent-profile'),
]
