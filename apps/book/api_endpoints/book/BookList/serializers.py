from rest_framework import serializers

from apps.book.models import Book
from apps.book.serializers import AuthorSerializer, GenreSerializer


class BookListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "authors",
            "genres",
        )
