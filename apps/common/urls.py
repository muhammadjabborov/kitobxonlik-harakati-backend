from django.urls import path

from apps.common.views import health_check_celery, health_check_redis

from .api_endpoints import DistrictListView, FrontendTranslationView, NeighborhoodListView, RegionListView, VersionHistoryView

app_name = "common"

urlpatterns = [
    path(
        "FrontendTranslations/",
        FrontendTranslationView.as_view(),
        name="frontend-translations",
    ),
    path("VersionHistory/", VersionHistoryView.as_view(), name="version-history"),
    path("RegionList/", RegionListView.as_view(), name="region-list"),
    path("DistrictList/", DistrictListView.as_view(), name="district-list"),
    path("NeighborhoodList/", NeighborhoodListView.as_view(), name="neighborhood-list"),
    path("health-check/redis/", health_check_redis, name="health-check-redis"),
    path("health-check/celery/", health_check_celery, name="health-check-celery"),
]
