from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.common.models import Region
from apps.common.api_endpoints.common.DistrictList.serializers import DistrictSerializer


class DistrictListView(ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "region_id",
                openapi.IN_QUERY,
                description="Filter districts by region ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Region.objects.filter(level=1).order_by("name")
        region_id = self.request.query_params.get("region_id")
        if region_id:
            qs = qs.filter(parent_id=region_id)
        return qs


__all__ = ["DistrictListView"]
