from rest_framework import serializers

from apps.book.models import Book
from apps.book.serializers import CategorySerializer, AuthorSerializer



class BookListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    categories = CategorySerializer(many=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "slug",
            "image",
            "published_year",
            "authors",
            "categories",
            "page_count",
            "grades",
            "featured_date",
            "is_active",
            "order"
        )
