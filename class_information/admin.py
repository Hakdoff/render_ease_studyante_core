from django.contrib import admin
from .models import Subject, Department, Section

admin.site.register(Department)
admin.site.register(Section)
admin.site.register(Subject)
