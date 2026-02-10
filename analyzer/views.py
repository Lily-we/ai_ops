from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AnalyzeView(APIView):
    def post(self, request):
        notes_text = request.data.get("notes_text", "")

        #dummy response (Phase A): stable schema for frontend
        dummy = {
            "priorities": [
                {
                    "title": "Stabilize API response schema",
                    "reason": "Frontend depends on consistent keys to render results.",
                    "urgency": "High"
                }
            ],
            "tasks": [
                {
                    "title": "Implement POST /api/analyze/ returning stable JSON",
                    "owner": "Owner",
                    "due": None,
                    "status": "pending",
                    "confidence": 0.9,
                },
                 {
                    "title": "Build results dashboard UI",
                    "owner": "Shokh",
                    "due": None,
                    "status": "todo",
                    "confidence": 0.8,
                },
            ],
             "blockers": [
                {
                    "title": "Nova integration not implemented yet",
                    "impacts": ["Task extraction", "Weekly report generation"],
                    "suggested_fix": "Ship dummy response first; add Nova calls in Phase B.",
                    "severity": "medium",
                }
            ],
            "weekly_report": {
                "done": ["Project scaffold created", "API route planned"],
                "next": ["Return stable JSON", "Connect UI to endpoint"],
                "risks": ["Schema drift between backend and frontend"],
                "asks": ["Confirm exact JSON contract with the team"],
            },
            "questions": [
                {
                    "question": "Do we want to support multiple languages in notes (RU/UZ/EN) for MVP?",
                    "why": "Affects prompt + UI language and evaluation samples.",
                }
            ],
            "meta": {
                "received_chars": len(notes_text),
                "mode": "dummy",
            },
        }

        return Response(dummy, status=status.HTTP_200_OK)