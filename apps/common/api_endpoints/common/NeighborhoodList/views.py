from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import Region
from apps.common.api_endpoints.common.NeighborhoodList.serializers import NeighborhoodSerializer


class NeighborhoodListView(ListAPIView):
    serializer_class = NeighborhoodSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "district_id",
                openapi.IN_QUERY,
                description="Filter neighborhoods by district ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "region_id",
                openapi.IN_QUERY,
                description="Filter neighborhoods by region ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Region.objects.filter(level=2).order_by("name")
        district_id = self.request.query_params.get("district_id")
        region_id = self.request.query_params.get("region_id")
        if district_id:
            qs = qs.filter(parent_id=district_id)
        if region_id:
            qs = qs.filter(parent__parent_id=region_id)
        return qs


__all__ = ["NeighborhoodListView"]
