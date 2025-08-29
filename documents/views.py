import os

from django.shortcuts import render

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from documents.function.extract import extract_text
from documents.models.document import Document
from documents.serializers.document_serializer import DocumentSerializer


# Create your views here.
class DocumentView(GenericViewSet):
    queryset = Document.objects.all().order_by('-creation_date')
    serializer_class = DocumentSerializer

    # GET /documents/ → Get all
    def list(self, request, *args, **kwargs):
        documents = self.get_queryset()

        # Check if "search" is provided in query params
        search_query = request.query_params.get("search", None)
        if search_query:
            documents = documents.filter(data__icontains=search_query)

        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # GET /documents/{id}/ → Get by ID
    def retrieve(self, request, pk=None):
        document = get_object_or_404(Document, pk=pk)
        serializer = self.get_serializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE /documents/{id}/ → Delete by ID
    def destroy(self, request, pk=None):
        document = get_object_or_404(Document, pk=pk)
        document.delete()
        return Response({"message": "Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    # POST /documents/ → Add document
    def create(self, request):
        file = request.FILES['file']
        filename = file.name  # "report.pdf"
        name, ext = os.path.splitext(filename)
        if ext == '.pdf':
            textData, dictList, titre, bytePdf = extract_text(request.data)
            serializer = DocumentSerializer(
                data={'file': ContentFile(bytePdf, name=filename), 'data': textData, 'titre': titre,
                      'keywords': dictList}, partial=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
