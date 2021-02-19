from django.urls import path
from rest_framework import routers

from .views import DocumentViewSet, ImageViewSet

documents_router = routers.DefaultRouter()
documents_router.register("documents", DocumentViewSet, basename="documents")

urlpatterns = documents_router.urls + [
    path("documents/<int:doc_id>/pages/<int:page_num>/", ImageViewSet.as_view())
]
