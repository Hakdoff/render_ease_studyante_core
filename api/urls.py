from django.urls import path

from class_information.views import DepartmentListCreateView

app_name = 'api'


urlpatterns = [
    path('department-list/<pk>', DepartmentListCreateView.as_view(),
         name='department-list'),
]
