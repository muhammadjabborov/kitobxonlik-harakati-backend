from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.book.api_endpoints.book.BookDetail.serializers import BookDetailSerializer
from apps.book.models import Book


class BookDetailView(generics.RetrieveAPIView):
    serializer_class = BookDetailSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return (
            Book.objects.filter(is_active=True)
            .prefetch_related("authors", "categories")
            .select_related("language")
            .annotate(
                audio_duration_total=Sum("audio_files__duration"),
                audio_book_count=Count("audio_files"),
            )
        )

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        identifier = self.kwargs.get("book_identifier")
        if identifier.isdigit():
            return get_object_or_404(queryset, pk=identifier)
        return get_object_or_404(queryset, slug=identifier)


__all__ = ["BookDetailView"]
