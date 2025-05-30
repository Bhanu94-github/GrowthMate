from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db, get_all_questions, ALL_SKILLS # Import utilities and skills
from core.serializers import AssessmentStartSerializer, QuestionSerializer, AssessmentAnswerSerializer
import spacy
import uuid
import datetime
import random

# Initialize spaCy model once
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Error loading spaCy model: {e}. AI Assessment features may be limited.")
    nlp = None # Set to None if loading fails

class AIAssessmentView(APIView):
    # This view handles starting an assessment and providing initial skills/difficulties
    def get(self, request):
        # Return available skills and difficulty levels
        return Response({
            'skills': ALL_SKILLS,
            'difficulties': ["easy", "medium", "hard"]
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # This endpoint is for starting the assessment with selected skill and difficulty
        serializer = AssessmentStartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        skill = serializer.validated_data['skill']
        difficulty = serializer.validated_data['difficulty']
        username = request.session.get('student_username') # Get student username from session

        if not username:
            return Response({'error': 'Authentication required to start assessment.'}, status=status.HTTP_401_UNAUTHORIZED)

        all_questions = get_all_questions(skill, difficulty)
        if len(all_questions) < 15: # Ensure enough questions
            return Response({'error': 'Insufficient questions for this skill and difficulty level.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Randomly select 15 questions and shuffle them
        selected_questions = random.sample(all_questions, 15)
        random.shuffle(selected_questions)

        # Store assessment state in session
        request.session['ai_assessment_state'] = {
            'session_id': str(uuid.uuid4()),
            'username': username,
            'skill': skill,
            'difficulty': difficulty,
            'questions': QuestionSerializer(selected_questions, many=True).data, # Store serialized questions
            'current_question_index': 0,
            'score': 0,
            'responses': [],
            'start_time': datetime.datetime.utcnow().isoformat() # Store start time
        }
        request.session.save()

        # Return the first question
        first_question = selected_questions[0]
        return Response({
            'message': 'Assessment started.',
            'session_id': request.session['ai_assessment_state']['session_id'],
            'current_question': QuestionSerializer(first_question).data,
            'current_question_index': 0,
            'total_questions': len(selected_questions),
            'all_skills': ALL_SKILLS # Send all skills for UI to display
        }, status=status.HTTP_200_OK)


class AIAssessmentQuestionView(APIView):
    # This view handles fetching the next/previous question
    def get(self, request):
        ai_state = request.session.get('ai_assessment_state')
        if not ai_state:
            return Response({'error': 'No active assessment found. Please start one.'}, status=status.HTTP_400_BAD_REQUEST)

        current_index = ai_state.get('current_question_index', 0)
        questions = ai_state.get('questions', [])

        if current_index < 0 or current_index >= len(questions):
            return Response({'error': 'Question index out of bounds.'}, status=status.HTTP_400_BAD_REQUEST)

        current_question = questions[current_index]
        return Response({
            'current_question': current_question,
            'current_question_index': current_index,
            'total_questions': len(questions),
            'responses_so_far': ai_state.get('responses', []) # Send responses so far for UI to pre-fill
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # This endpoint handles submitting an answer for the current question
        ai_state = request.session.get('ai_assessment_state')
        if not ai_state:
            return Response({'error': 'No active assessment found. Please start one.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AssessmentAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question_id = serializer.validated_data['question_id']
        selected_answer = serializer.validated_data['selected_answer']

        current_index = ai_state['current_question_index']
        questions = ai_state['questions']
        responses = ai_state['responses']

        # Find the question by ID (important for robustness)
        current_question_data = None
        for q in questions:
            if q['id'] == question_id:
                current_question_data = q
                break

        if not current_question_data:
            return Response({'error': 'Question not found in active assessment.'}, status=status.HTTP_404_NOT_FOUND)

        # Update or append response
        response_entry = {
            "question_id": question_id,
            "question": current_question_data.get("question"),
            "type": current_question_data.get("type"),
            "selected": selected_answer,
            "correct": current_question_data.get("answer"), # The correct answer is stored in the question data
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # If we are revisiting a question, update the existing response
        if len(responses) > current_index and responses[current_index].get('question_id') == question_id:
            responses[current_index] = response_entry
        else: # Otherwise, append (should only happen for new questions)
            responses.append(response_entry)

        ai_state['responses'] = responses
        request.session['ai_assessment_state'] = ai_state
        request.session.save()

        return Response({'message': 'Answer recorded.'}, status=status.HTTP_200_OK)


class AIAssessmentSubmitView(APIView):
    def post(self, request):
        username = request.session.get('student_username')
        ai_state = request.session.get('ai_assessment_state')

        if not username or not ai_state:
            return Response({'error': 'No active assessment or user not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

        final_score = 0
        invalid_questions_count = 0
        total_questions = len(ai_state['questions'])

        for resp in ai_state['responses']:
            # Find the original question data to get the correct answer
            original_question = next((q for q in ai_state['questions'] if q['id'] == resp['question_id']), None)

            if original_question:
                correct_answer = original_question.get('answer')
                selected_answer = resp.get('selected')

                if selected_answer is not None and correct_answer is not None:
                    # Convert to string and lower for robust comparison
                    if str(selected_answer).strip().lower() == str(correct_answer).strip().lower():
                        final_score += 1
                else:
                    invalid_questions_count += 1
            else:
                invalid_questions_count += 1 # Question not found in original list

        # Save results to MongoDB
        db["results"].insert_one({
            "session_id": ai_state['session_id'],
            "username": username,
            "score": final_score,
            "skill": ai_state['skill'],
            "difficulty": ai_state['difficulty'],
            "total": total_questions,
            "responses": ai_state['responses'],
            "start_time": ai_state['start_time'],
            "submission_time": datetime.datetime.utcnow().isoformat()
        })

        # Clear assessment state from session
        if 'ai_assessment_state' in request.session:
            del request.session['ai_assessment_state']
        request.session.save()

        return Response({
            'message': 'Assessment completed and submitted successfully!',
            'score': final_score,
            'total': total_questions,
            'invalid_questions': invalid_questions_count
        }, status=status.HTTP_200_OK)