from django.urls import path, include

urlpatterns = [
    path("", include("pdf_render.app.urls")),
]
