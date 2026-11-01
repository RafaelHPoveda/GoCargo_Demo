from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shipments.application.dto.shipment_data import CreateShipmentInput
from apps.shipments.presentation.api.serializers import (
    CreateShipmentSerializer,
    ShipmentOutputSerializer,
)
from config.dependencies import build_shipment_service


class ShipmentAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        result = build_shipment_service().list_all()
        return Response(ShipmentOutputSerializer(result, many=True).data)

    def post(self, request):
        serializer = CreateShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = build_shipment_service().create(
            CreateShipmentInput(**serializer.validated_data)
        )
        return Response(
            ShipmentOutputSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class ShipmentDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, shipment_id):
        result = build_shipment_service().get_by_id(shipment_id)
        return Response(ShipmentOutputSerializer(result).data)
