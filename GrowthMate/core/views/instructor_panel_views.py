from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db, log_token_history
from core.serializers import InstructorLoginSerializer, UserDataSerializer, TokenLogSerializer, AssessmentResultSerializer
import bcrypt
import datetime
import pandas as pd
from collections import defaultdict

class InstructorLoginView(APIView):
    def post(self, request):
        serializer = InstructorLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Assuming instructors also have hashed passwords in 'instructors' collection
        instructor = db["instructors"].find_one({"username": username})

        if instructor and bcrypt.checkpw(password.encode('utf-8'), instructor['password'].encode('utf-8')):
            request.session['instructor_username'] = username
            request.session.save()
            return Response({'message': f'Welcome, {username}!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class InstructorDashboardView(APIView):
    def get(self, request):
        instructor_username = request.session.get('instructor_username')
        if not instructor_username:
            return Response({'error': 'Not authenticated as instructor.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch all students and their token data
        students_data = list(db["access_students"].find({}, {"_id": 0, "username": 1, "name": 1, "tokens": 1, "ai_tokens": 1, "exam_attempts": 1}))
        serializer = UserDataSerializer(students_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TokenManagementView(APIView):
    def post(self, request):
        instructor_username = request.session.get('instructor_username')
        if not instructor_username:
            return Response({'error': 'Not authenticated as instructor.'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')
        student_username = request.data.get('student_username')
        tokens_changed = request.data.get('tokens_changed') # For increment/decrement
        module = request.data.get('module') # For module-specific tokens

        if not student_username:
            return Response({'error': 'Student username is required.'}, status=status.HTTP_400_BAD_REQUEST)

        student = db["access_students"].find_one({"username": student_username})
        if not student:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'increment_general_token':
            db["access_students"].update_one({"username": student_username}, {"$inc": {"tokens": 1}})
            log_token_history(student_username, instructor_username, "Token Increment", 1)
            return Response({'message': f'{student_username}: +1 general token'}, status=status.HTTP_200_OK)
        elif action == 'decrement_general_token':
            if student.get("tokens", 0) > 0:
                db["access_students"].update_one({"username": student_username}, {"$inc": {"tokens": -1}})
                log_token_history(student_username, instructor_username, "Token Decrement", -1)
                return Response({'message': f'{student_username}: -1 general token'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'General tokens already at 0.'}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'reset_all_tokens':
            db["access_students"].update_one(
                {"username": student_username},
                {"$set": {
                    "tokens": 15,
                    "ai_tokens": {
                        "Text_to_Text": 15,
                        "Voice_to_Voice": 15,
                        "Face_to_Face": 15
                    }
                },
                 "$inc": {"exam_attempts": 1}
                }
            )
            log_token_history(student_username, instructor_username, "Reset to 15", 15)
            return Response({'message': f'{student_username}: All tokens reset to 15 and exam attempt incremented.'}, status=status.HTTP_200_OK)
        elif action == 'increment_module_token' and module:
            db["access_students"].update_one(
                {"username": student_username},
                {"$inc": {f"ai_tokens.{module}": 1}}
            )
            log_token_history(student_username, instructor_username, "Module Token Increment", 1, module)
            return Response({'message': f'{student_username}: +1 {module} token'}, status=status.HTTP_200_OK)
        elif action == 'decrement_module_token' and module:
            if student.get("ai_tokens", {}).get(module, 0) > 0:
                db["access_students"].update_one(
                    {"username": student_username},
                    {"$inc": {f"ai_tokens.{module}": -1}}
                )
                log_token_history(student_username, instructor_username, "Module Token Decrement", -1, module)
                return Response({'message': f'{student_username}: -1 {module} token'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': f'{module} tokens already at 0.'}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'reset_module_token' and module:
            db["access_students"].update_one(
                {"username": student_username},
                {"$set": {f"ai_tokens.{module}": 15}}
            )
            log_token_history(student_username, instructor_username, "Module Reset to 15", 15, module)
            return Response({'message': f'{student_username}: {module} tokens reset to 15.'}, status=status.HTTP_200_OK)
        elif action == 'bulk_reset_all_tokens':
            # This action would typically apply to a filtered list of students
            # For simplicity, let's assume it resets all currently fetched students
            # In a real app, you'd send a list of student_usernames to reset
            students_to_reset = request.data.get('student_usernames', [])
            if not students_to_reset:
                return Response({'error': 'No students provided for bulk reset.'}, status=status.HTTP_400_BAD_REQUEST)

            for s_username in students_to_reset:
                db["access_students"].update_one(
                    {"username": s_username},
                    {
                        "$set": {
                            "tokens": 15,
                            "ai_tokens": {
                                "Text_to_Text": 15,
                                "Voice_to_Voice": 15,
                                "Face_to_Face": 15
                            }
                        },
                        "$inc": {"exam_attempts": 1}
                    }
                )
                log_token_history(s_username, instructor_username, "Bulk Reset to 15", 15)
            return Response({'message': 'All specified students reset to 15 tokens.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action or missing module for module-specific action.'}, status=status.HTTP_400_BAD_REQUEST)


class InstructorAnalyticsView(APIView):
    def get(self, request):
        instructor_username = request.session.get('instructor_username')
        if not instructor_username:
            return Response({'error': 'Not authenticated as instructor.'}, status=status.HTTP_401_UNAUTHORIZED)

        results_col = db["results"]
        all_results = list(results_col.find({}))
        token_logs_col = db["token_logs"]
        all_token_logs = list(token_logs_col.find({"actor": instructor_username}).sort("timestamp", -1))

        response_data = {}

        # Token Logs
        if all_token_logs:
            response_data['token_logs'] = TokenLogSerializer(all_token_logs, many=True).data
        else:
            response_data['token_logs'] = []

        # Assessment Analytics
        if all_results:
            score_data = []
            for r in all_results:
                score_data.append({
                    "username": r.get("username", "unknown"),
                    "score": r.get("score", 0),
                    "timestamp": r.get("timestamp", datetime.datetime.utcnow()),
                    "skill": r.get("skill", "Unknown Skill"),
                    "difficulty": r.get("difficulty", "Unknown Difficulty")
                })
            score_df = pd.DataFrame(score_data)
            score_df["timestamp"] = pd.to_datetime(score_df["timestamp"])

            # Overall Performance
            response_data['overall_performance'] = {
                "average_score": score_df["score"].mean() if not score_df.empty else 0
            }

            # Skill-based Analysis
            if not score_df.empty:
                skill_avg = score_df.groupby("skill")["score"].mean().reset_index()
                response_data['skill_average_scores'] = skill_avg.to_dict(orient="records")

                # Difficulty Analysis
                difficulty_avg = score_df.groupby("difficulty")["score"].mean().reset_index()
                response_data['difficulty_average_scores'] = difficulty_avg.to_dict(orient="records")

                # Student Ranking
                summary_df = score_df.groupby("username").agg(
                    Attempts=('score', 'count'),
                    Average_Score=('score', 'mean'),
                    Max_Score=('score', 'max')
                ).reset_index()
                summary_df = summary_df.sort_values(by="Average_Score", ascending=False)
                response_data['student_ranking'] = summary_df.to_dict(orient="records")

                # Per-Student Skill Breakdown (for all students, React can filter)
                student_skill_breakdown = defaultdict(dict)
                for username in score_df["username"].unique():
                    student_df = score_df[score_df["username"] == username]
                    skill_summary = student_df.groupby("skill")["score"].mean().reset_index()
                    student_skill_breakdown[username] = skill_summary.to_dict(orient="records")
                response_data['student_skill_breakdown'] = dict(student_skill_breakdown)

                # Comparison Data (React will request specific comparison)
                # For now, just send all unique students for comparison selection
                response_data['unique_students_for_comparison'] = score_df["username"].unique().tolist()

            else:
                response_data['assessment_message'] = "No assessment results found in the database."
        else:
            response_data['assessment_message'] = "No assessment results found in the database."

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        instructor_username = request.session.get('instructor_username')
        if not instructor_username:
            return Response({'error': 'Not authenticated as instructor.'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')

        if action == 'get_comparison_data':
            student1 = request.data.get('student1')
            student2 = request.data.get('student2')

            if not student1 or not student2:
                return Response({'error': 'Both student1 and student2 are required for comparison.'}, status=status.HTTP_400_BAD_REQUEST)

            results_col = db["results"]
            comp_results = list(results_col.find({"username": {"$in": [student1, student2]}}))

            if comp_results:
                comp_df = pd.DataFrame(comp_results)
                comp_data = comp_df.groupby(['username', 'skill'])['score'].mean().reset_index().to_dict(orient="records")
                return Response({'comparison_data': comp_data}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No data found for comparison.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action for analytics.'}, status=status.HTTP_400_BAD_REQUEST)