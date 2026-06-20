from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.book.api_endpoints.book.HomeBookList.serializers import HomeBookListSerializer
from apps.book.models import Book


class HomeBookListView(ListAPIView):
    serializer_class = HomeBookListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        qs = Book.objects.filter(is_active=True).prefetch_related("authors", "genres")
        return qs.order_by("id")[:4]


__all__ = ["HomeBookListView"]
