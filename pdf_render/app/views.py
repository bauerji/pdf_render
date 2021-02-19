from wsgiref.util import FileWrapper

from django.http import FileResponse
from rest_framework import generics, parsers, viewsets

from . import models, serializers, tasks


class ImageViewSet(generics.RetrieveAPIView):
    queryset = models.Image.objects.all()
    lookup_field = "page_num"
    lookup_url_kwarg = "page_num"

    def filter_queryset(self, queryset):
        doc_id = self.kwargs["doc_id"]
        return queryset.filter(document_id=doc_id)

    def retrieve(self, request, *args, **kwargs):
        image: models.Image = self.get_object()
        return FileResponse(
            FileWrapper(image.image.open()),
            content_type="image/png",
        )


class DocumentViewSet(
    viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView
):
    parser_classes = [parsers.FileUploadParser]
    queryset = models.Document.objects.all()

    def get_serializer_class(self):
        return {
            "POST": serializers.CreateDocumentSerializer,
            "GET": serializers.RetrieveImageSerializer,
        }[self.request.method]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        payload = tasks.PdfToPngPayload(
            file=self.request.data["file"], doc_id=serializer.instance.id
        )
        tasks.pdf_to_png.send(payload)
