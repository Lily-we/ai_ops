from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AnalyzeRequestSerializer

from .services.nova_client import NovaClient
from .services.extractor import extract_ops


class AnalyzeView(APIView):
    def post(self, request):
        s = AnalyzeRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        notes_text = s.validated_data["notes_text"]

        client = NovaClient(timeout_seconds=15)
        result = extract_ops(notes_text, client)

        return Response(result, status=status.HTTP_200_OK)
