from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import District
from apps.common.api_endpoints.common.DistrictList.serializers import DistrictSerializer


class DistrictListView(ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        qs = District.objects.order_by("name")
        region_id = self.request.query_params.get("region_id")
        if region_id:
            qs = qs.filter(region_id=region_id)
        return qs


__all__ = ["DistrictListView"]
