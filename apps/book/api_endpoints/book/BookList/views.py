from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.book.api_endpoints.book.BookList.serializers import BookListSerializer
from apps.book.models import Book


class BookListView(generics.ListAPIView):
    serializer_class = BookListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title", "slug")

    def get_queryset(self):
        qs = (
            Book.objects.filter(is_active=True)
            .prefetch_related("authors", "genres")
            .order_by("order", "-id")
        )

        user = self.request.user

        if user.is_authenticated:
            if user.grade:
                qs = qs.filter(grades=user.grade)
        else:
            grade = self.request.query_params.get("grades")
            if grade:
                qs = qs.filter(grades=grade)

        return qs


__all__ = ["BookListView"]
