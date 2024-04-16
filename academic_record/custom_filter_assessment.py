from rest_framework import filters
from django.db.models import Q, F


class CustomFilterAssessment(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_fields = request.query_params.get('search_fields')
        search_values = request.query_params.get('search_values')
        name = request.query_params.get('name', None)

        if search_fields:
            search_fields = search_fields.split(',')
            search_values = search_values.split(',')
            if len(search_fields) == len(search_values):
                and_query = Q()
                for field, value in zip(search_fields, search_values):
                    if value and value != 'ALL':
                        and_query &= Q(**{f'{field}': value})
                queryset = queryset.filter(
                    and_query).distinct()

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('-created_at')


class CustomFilterStudentAssessment(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_fields = request.query_params.get('search_fields')
        student_name = request.query_params.get('student_name', None)

        if search_fields:
            search_fields = search_fields.split(',')
            or_query = Q()
            for field in search_fields:
                field_value = request.query_params.get(field)
                if field_value:
                    or_query &= Q(**{f'{field}': field_value})
            queryset = queryset.filter(
                or_query).distinct()

        if student_name:
            queryset = queryset.filter(
                Q(student__user__first_name__icontains=student_name) | Q(student__user__last_name__icontains=student_name))

        return queryset.order_by('-created_at')
