from rest_framework import serializers

from apps.book.models import Author, Book, Category, Language


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title")


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "name", "code")


class BookShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "slug")
