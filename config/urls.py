from django.contrib import admin
from django.urls import include, path

from config.api_docs import api_docs, openapi_schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/docs/", api_docs, name="api-docs"),
    path("api/schema/", openapi_schema, name="openapi-schema"),
    path("api/", include("apps.branches.presentation.api.urls")),
    path("api/", include("apps.shipments.presentation.api.urls")),
]
