from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import Region
from apps.common.api_endpoints.common.RegionList.serializers import RegionSerializer


class RegionListView(ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Region.objects.prefetch_related("districts").order_by("name")


__all__ = ["RegionListView"]
