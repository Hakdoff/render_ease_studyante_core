from django.shortcuts import render

from academic_record.models import AcademicYear, Attendance, Schedule
from base.models import User
from user_profile.models import Student
from registration.models import Registration

from django.db.models import Count
from django.db.models.functions import ExtractMonth
import json

def dashboard_view(request):
    academic_years = AcademicYear.objects.all()
    students_users = Student.objects.all()
    # students_users = Registration.objects.filter(academic_year=academic_years.first())
    teachers_users = Schedule.objects.all()
    male_students = Student.objects.filter(gender='M')
    female_students = Student.objects.filter(gender='F')
    year_levels_counts = {
        'GRADE 7': Student.objects.filter(year_level='GRADE 7').count(),
        'GRADE 8': Student.objects.filter(year_level='GRADE 8').count(),
        'GRADE 9': Student.objects.filter(year_level='GRADE 9').count(),
        'GRADE 10': Student.objects.filter(year_level='GRADE 10').count()
    }

    # For Students to retrieve Latest Attendance 
    students_data = Student.objects.all()
    students_with_attendance = []

    for student in students_data:
        latest_attendance = Attendance.objects.filter(student=student).order_by('-attendance_date').first()
        if latest_attendance:
            students_with_attendance.append({
                'student': student,
                'latest_attendance_date': latest_attendance.attendance_date,
                'student_time_in': latest_attendance.time_in,
                'student_time_out':  latest_attendance.time_out,
                'is_present': latest_attendance.is_present
            })


    # Determine all users stored in system
    user_count = User.objects.all()

    # Student Genders
    student_genders = ['M', 'F']
    gender_num = [male_students, female_students]

    # Student Grade Levels
    student_year_levels = ['GRADE 7', 'GRADE 8', 'GRADE 9', 'GRADE 10']
    
    # Determine no. of Accounts
    month_lists = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    user_counts = User.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')

    months = []
    counts = []

    month_counts = {month: 0 for month in month_lists}

    for user_count in user_counts:
        month_name = month_lists[user_count['month'] - 1]
        month_counts[month_name] = user_count['count']

    months = list(month_counts.keys())
    counts = list(month_counts.values())

    context = {
        'students_users': students_users,
        'teachers_users': teachers_users,
        'male_students': male_students,
        'female_students': female_students,
        'student_genders': student_genders,
        'gender_num': gender_num,
        'student_year_levels': student_year_levels,
        'year_levels_counts': year_levels_counts,
        'user_count': user_count,
        'students_with_attendance': students_with_attendance,
        'month_lists': month_lists,
        'months': json.dumps(months),
        'counts': json.dumps(counts),
    }


    return render(request, 'dashboard/dashboard.html', context)

def dashboard_detail_view(request):
    academic_years = AcademicYear.objects.all()
    all_students = Registration.objects.filter(academic_year=academic_years.first())
    teachers_users = Schedule.objects.all()

    context = {
        'all_students': all_students,
        'teachers_users': teachers_users
    }

    return render(request, 'dashboard/dashboard_detail_view.html', context)
    

    

# def dashboard_detail_view(request, pk):
#     attendance_data = Attendance.objects.filter(student__pk = pk).order_by('created_at')
#     dashboard_instance = Dashboard.objects.first()
#     attendance_data = None

#     if dashboard_instance:
#         attendance_data = dashboard_instance.get_attendance_data()
#     context = {
#         'attendance_data' : attendance_data
#     }

#     return render(request, 'dashboard/dashboard_detail_view.html', context)
