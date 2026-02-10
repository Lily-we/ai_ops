from rest_framework import serializers

class AnalyzeRequestSerializer(serializers.Serializer):
    notes_text = serializers.CharField(allow_blank=False, max_length=20000)