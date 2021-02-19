from rest_framework import serializers

from . import enums
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj: Document):
        return enums.DocumentStatus(obj.status).name.lower()

    class Meta:
        model = Document


class CreateDocumentSerializer(DocumentSerializer):
    class Meta:
        fields = ("id",)
        model = Document


class RetrieveImageSerializer(DocumentSerializer):
    class Meta:
        model = Document
        fields = ("status", "n_pages")
