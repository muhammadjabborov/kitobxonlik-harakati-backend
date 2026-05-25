from rest_framework.filters import BaseFilterBackend

from django.utils import timezone


class BookListFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user

        if user.is_authenticated:
            if user.grade:
                date = request.query_params.get("date")  # format: 2026-06
                if date:
                    year, month = date.split("-")
                else:
                    now = timezone.now()
                    year, month = now.year, now.month
                return queryset.filter(
                    grades=user.grade,
                    featured_date__isnull=False,
                    featured_date__year=year,
                    featured_date__month=month,
                )
        else:
            grade = request.query_params.get("grades")
            if grade:
                return queryset.filter(grades=grade)

        return queryset
