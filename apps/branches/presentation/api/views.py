from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.branches.application.dto.branch_data import CreateBranchInput, UpdateBranchInput
from apps.branches.presentation.api.serializers import (
    BranchOutputSerializer,
    CreateBranchSerializer,
    UpdateBranchSerializer,
)
from config.dependencies import build_branch_service


class BranchAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        result = build_branch_service().list_all()
        return Response(BranchOutputSerializer(result, many=True).data)

    def post(self, request):
        serializer = CreateBranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = build_branch_service().create(
            CreateBranchInput(**serializer.validated_data)
        )
        return Response(
            BranchOutputSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class BranchUpdateAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def put(self, request, branch_id):
        return self._update(request, branch_id, partial=False)

    def patch(self, request, branch_id):
        return self._update(request, branch_id, partial=True)

    def _update(self, request, branch_id, *, partial):
        serializer = UpdateBranchSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        result = build_branch_service().update(
            branch_id, UpdateBranchInput(**serializer.validated_data)
        )
        return Response(BranchOutputSerializer(result).data)
