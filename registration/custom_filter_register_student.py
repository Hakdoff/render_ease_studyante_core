from rest_framework import filters
from django.db.models import Q, F


class CustomFilterRegisterStudent(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_fields = request.query_params.get('search_fields')
        name = request.query_params.get('name', None)

        if search_fields:
            search_fields = search_fields.split(',')
            or_query = Q()
            for field in search_fields:
                field_value = request.query_params.get(field)
                if field_value:
                    or_query &= Q(**{f'{field}': field_value})
            queryset = queryset.filter(
                or_query).distinct()

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.order_by('-created_at')
