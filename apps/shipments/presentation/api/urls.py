from django.urls import path

from apps.shipments.presentation.api.views import ShipmentAPIView, ShipmentDetailAPIView


urlpatterns = [
    path("shipments/", ShipmentAPIView.as_view(), name="shipment-create"),
    path("shipments/<uuid:shipment_id>/", ShipmentDetailAPIView.as_view(), name="shipment-detail"),
]
