from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from django.utils import timezone

from apps.book.api_endpoints.book.HomeBookList.serializers import HomeBookListSerializer
from apps.book.models import Book


class HomeBookListView(ListAPIView):
    serializer_class = HomeBookListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        print(now)
        qs = Book.objects.filter(
            is_active=True,
            featured_date__isnull=False,
            featured_date__year=now.year,
            featured_date__month=now.month,
        ).prefetch_related("authors", "genres")
        print(qs.count())
        user = self.request.user
        if user.is_authenticated and user.grade:
            qs = qs.filter(grades=user.grade)

        return qs.order_by("?")[:4]


__all__ = ["HomeBookListView"]
