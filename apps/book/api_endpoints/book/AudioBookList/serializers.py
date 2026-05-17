from rest_framework import serializers

from apps.book.models import AudioFile
from apps.book.serializers import BookShortSerializer


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ("id", "title", "file", "duration", "order")


class AudioFileListSerializer(serializers.Serializer):
    book_info = BookShortSerializer()
    audio_files = AudioFileSerializer(many=True)
