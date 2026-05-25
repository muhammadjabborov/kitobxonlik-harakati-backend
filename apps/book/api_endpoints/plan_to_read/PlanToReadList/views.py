from rest_framework import generics, permissions

from django.db.models import DecimalField, F, Value
from django.db.models.functions import Coalesce

from .serializers import PlanToReadListSerializer

from apps.book.models import PlanToRead


class PlanToReadListAPIView(generics.ListAPIView):
    serializer_class = PlanToReadListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    search_fields = ["book__title", "book__authors__name"]

    def get_queryset(self):
        return (
            PlanToRead.objects.filter(user=self.request.user)
            .select_related("book")
            .prefetch_related("book__authors")
        )
