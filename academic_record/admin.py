from django.contrib import admin
from .models import Assessment, Attendance, Schedule, StudentAssessment, Grade


admin.site.register(Assessment)
admin.site.register(Attendance)
admin.site.register(Schedule)
admin.site.register(StudentAssessment)
admin.site.register(Grade)
