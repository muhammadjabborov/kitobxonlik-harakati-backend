from rest_framework import serializers

from apps.book.models import Book
from apps.book.serializers import AuthorSerializer, GenreSerializer


class HomeBookListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "published_year",
            "authors",
            "genres",
            "page_count",
            "grades",
            "featured_date",
            "is_active",
            "order",
        )
