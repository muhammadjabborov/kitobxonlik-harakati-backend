import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .schema import swagger_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/common/", include("apps.common.urls", namespace="common")),
    path("api/v1/users/", include("apps.users.urls", namespace="users")),
    path("api/v1/book/", include("apps.book.urls", namespace="book")),
    path("api/v1/assessment/", include("apps.assessment.urls", namespace="assessment")),
    path("admin_async_upload/", include("admin_async_upload.urls")),
]

urlpatterns += swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if os.environ.get("DJANGO_SETTINGS_MODULE") == "core.settings.develop":
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
