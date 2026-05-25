from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny

from apps.book.api_endpoints.book.BookList.filters import BookListFilter
from apps.book.api_endpoints.book.BookList.serializers import BookListSerializer
from apps.book.models import Book


class BookListView(generics.ListAPIView):
    serializer_class = BookListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter, BookListFilter)
    search_fields = ("title", "slug")

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_QUERY,
                description="Filter books by month. Format: YYYY-MM (e.g. 2026-06). Only applies for authenticated users with a grade.",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "grades",
                openapi.IN_QUERY,
                description="Filter books by grade. Only applies for unauthenticated users.",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Book.objects.filter(is_active=True)
            .prefetch_related("authors", "genres")
            .order_by("order", "-id")
        )


__all__ = ["BookListView"]
