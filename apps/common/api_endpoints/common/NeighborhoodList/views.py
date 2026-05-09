from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import Neighborhood
from apps.common.api_endpoints.common.NeighborhoodList.serializers import NeighborhoodSerializer


class NeighborhoodListView(ListAPIView):
    serializer_class = NeighborhoodSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        qs = Neighborhood.objects.order_by("name")
        region_id = self.request.query_params.get("region_id")
        district_id = self.request.query_params.get("district_id")
        if region_id:
            qs = qs.filter(district__region_id=region_id)
        if district_id:
            qs = qs.filter(district_id=district_id)
        return qs


__all__ = ["NeighborhoodListView"]
