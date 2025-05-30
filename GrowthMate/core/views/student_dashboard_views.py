from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db, log_token_history # Import utilities
from core.serializers import UserDataSerializer
import uuid
import datetime

class StudentDashboardView(APIView):
    def get(self, request):
        username = request.session.get('student_username')
        if not username:
            return Response({'error': 'Not authenticated. Please log in.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = db["access_students"].find_one({"username": username})
        if not user:
            # Clear session if user not found in DB (e.g., deleted by admin)
            if 'student_username' in request.session:
                del request.session['student_username']
            return Response({'error': 'User not found. Please log in again.'}, status=status.HTTP_404_NOT_FOUND)

        # Return serialized user data
        user_data_for_response = {k: v for k, v in user.items() if k != 'password'}
        serializer = UserDataSerializer(user_data_for_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Handles actions from the student dashboard, e.g., ending an exam due to tab switch.
        """
        username = request.session.get('student_username')
        if not username:
            return Response({'error': 'Not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')

        if action == "end_exam":
            # Logic to end the exam, clear relevant session state
            # This mimics the Streamlit 'tab switch' detection
            request.session['exam_active'] = False
            request.session['selected_module'] = None
            # Clear AI assessment specific session states
            for key in ["page", "selected_skill", "difficulty", "questions", "index", "score", "responses", "session_id"]:
                if key in request.session:
                    del request.session[key]
            request.session['session_id'] = str(uuid.uuid4()) # Reset session ID for next exam
            return Response({'message': 'Exam ended due to external interruption.'}, status=status.HTTP_200_OK)
        elif action == "start_module_exam":
            module_name = request.data.get('module_name')
            if not module_name:
                return Response({'error': 'Module name is required to start exam.'}, status=status.HTTP_400_BAD_REQUEST)

            user = db["access_students"].find_one({"username": username})
            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            token_key = module_name.replace("-", "_") # Convert "Text-to-Text" to "Text_to_Text"
            tokens_left = user.get("ai_tokens", {}).get(token_key, 0)

            if tokens_left > 0:
                result = db["access_students"].update_one(
                    {"username": username, f"ai_tokens.{token_key}": {"$gt": 0}},
                    {"$inc": {f"ai_tokens.{token_key}": -1}}
                )
                if result.modified_count == 1:
                    log_token_history(username, "system", "module_token_deduction", -1, module_name)
                    request.session['exam_active'] = True
                    request.session['selected_module'] = token_key
                    request.session['session_id'] = str(uuid.uuid4())
                    # Reset AI assessment specific session states for a new exam
                    for key in ["page", "selected_skill", "difficulty", "questions", "index", "score", "responses"]:
                        if key in request.session:
                            del request.session[key]
                    return Response({'message': f'Launched {module_name} exam! Tokens left: {tokens_left - 1}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Token deduction failed or no tokens left.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': f'You have no {module_name} tokens left.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)