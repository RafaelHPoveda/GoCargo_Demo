import json
from pathlib import Path

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe


SCHEMA_PATH = Path(__file__).with_name("openapi.json")


@require_safe
def openapi_schema(request: HttpRequest) -> JsonResponse:
    """Publica el contrato local sin consultar datos ni servicios externos."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return JsonResponse(schema, json_dumps_params={"ensure_ascii": False})


@require_safe
def api_docs(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "api_docs.html",
        {"schema_url": reverse("openapi-schema")},
    )
