from django.urls import path

from apps.branches.presentation.api.views import BranchAPIView, BranchUpdateAPIView


urlpatterns = [
    path("branches/", BranchAPIView.as_view(), name="branch-list-create"),
    path("branches/<uuid:branch_id>/", BranchUpdateAPIView.as_view(), name="branch-update"),
]
