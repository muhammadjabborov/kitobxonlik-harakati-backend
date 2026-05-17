from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.book.api_endpoints.book.AudioBookList.serializers import AudioFileListSerializer, AudioFileSerializer
from apps.book.models import Book


class AudioBookListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, book_identifier):
        qs = Book.objects.filter(is_active=True).prefetch_related("audio_files")
        if book_identifier.isdigit():
            book = get_object_or_404(qs, pk=book_identifier)
        else:
            book = get_object_or_404(qs, slug=book_identifier)

        data = {
            "book_info": book,
            "audio_files": book.audio_files.order_by("order"),
        }
        serializer = AudioFileListSerializer(data, context={"request": request})
        return Response(serializer.data)


__all__ = ["AudioBookListView"]
