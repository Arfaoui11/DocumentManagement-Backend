from rest_framework import serializers

from documents.models.document import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('id', 'creation_date')  # id et date créés automatiquement