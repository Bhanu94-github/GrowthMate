from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db, log_token_history # Import utilities
from core.serializers import AudioTranscriptionSerializer, TextToSpeechSerializer, ChatPromptSerializer
import whisper
from groq import Groq
from gtts import gTTS
import tempfile
import os
import base64
import datetime
import gc
import PyPDF2
import docx
from io import BytesIO
import random # For extract_skills simulation

# Initialize models globally (or as class attributes if you prefer)
# This avoids reloading them on every request, but be mindful of memory.
whisper_model = None
groq_client = None

def load_models():
    global whisper_model, groq_client
    if not whisper_model:
        try:
            gc.collect()
            whisper_model = whisper.load_model("tiny")
        except RuntimeError as e:
            print(f"Failed to load Whisper model: {e}")
            whisper_model = None
    if not groq_client:
        # Replace with your actual Groq API Key (use environment variables in production!)
        groq_client = Groq(api_key="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")


# Helper functions (from original voice.py)
def extract_resume_text(resume_file_bytes, file_name):
    try:
        if file_name.endswith(".pdf"):
            with PyPDF2.PdfReader(BytesIO(resume_file_bytes)) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif file_name.endswith(".docx"):
            doc = docx.Document(BytesIO(resume_file_bytes))
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_name.endswith(".txt"):
            return resume_file_bytes.decode("utf-8")
    except Exception as e:
        print(f"Error parsing resume: {e}")
    return ""

def extract_skills_from_text(text):
    # This is a simplified version. In a real app, you'd use NLP for better extraction.
    # For now, simulate by picking some common skills if text is long enough.
    possible_skills = ["Python", "SQL", "Machine Learning", "Java", "JavaScript", "Cloud", "Data Science"]
    found_skills = []
    text_lower = text.lower()
    for skill in possible_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    # If no skills found, or text is short, return a default set
    if not found_skills and len(text) > 50: # Arbitrary length check
        return random.sample(possible_skills, min(3, len(possible_skills)))
    return found_skills if found_skills else ["General Programming"]


def calculate_performance_rating(responses):
    positive_keywords = ["good", "excellent", "well done", "correct", "strong", "accurate"]
    negative_keywords = ["needs improvement", "incorrect", "lacking", "weak", "incomplete"]
    total_score = 0
    feedback_summary = []
    for r in responses:
        feedback = r["feedback"].lower()
        score = 5  # Base score per response
        for word in positive_keywords:
            if word in feedback:
                score += 1
        for word in negative_keywords:
            if word in feedback:
                score -= 1
        score = max(0, min(10, score))  # Clamp score between 0 and 10
        total_score += score
        feedback_summary.append(f"Skill: {r['skill']}, Score: {score}/10")
    overall_score = round(total_score / len(responses), 1) if responses else 0
    stars = "⭐" * int(overall_score // 2) + ("½" if overall_score % 2 else "")
    return {
        "score": overall_score,
        "stars": stars,
        "summary": "\n".join(feedback_summary)
    }


class VoiceTranscriptionView(APIView):
    def post(self, request):
        load_models() # Ensure models are loaded
        serializer = AudioTranscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_data_base64 = serializer.validated_data['audio']
        if not audio_data_base64:
            return Response({'error': 'No audio data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not whisper_model:
            return Response({'error': 'Whisper model not loaded. Check server logs.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            audio_bytes = base64.b64decode(audio_data_base64)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                temp_audio_file.flush()
                transcription = whisper_model.transcribe(temp_audio_file.name)
            return Response({'transcription': transcription['text']}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Transcription failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoiceSpeechGenerationView(APIView):
    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data['text']
        if not text:
            return Response({'error': 'No text provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_audio_file:
                tts.save(temp_audio_file.name)
                with open(temp_audio_file.name, "rb") as f:
                    audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            return Response({'audio_base64': audio_base64}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Speech generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoiceChatResponseView(APIView):
    def post(self, request):
        load_models() # Ensure models are loaded
        serializer = ChatPromptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        prompt_text = serializer.validated_data['prompt']
        skill = serializer.validated_data.get('skill', 'general')
        resume_text = serializer.validated_data.get('resume_text', '')
        is_question = serializer.validated_data.get('is_question', True)

        if not groq_client:
            return Response({'error': 'Groq client not initialized. Check server logs.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            system_prompt_role = "You are an AI interviewer."
            if is_question:
                system_prompt_role += " Ask a professional interview question"
            else:
                system_prompt_role += " Give feedback for the following answer"

            system_prompt_skill = f" related to this skill: {skill}." if skill else "."
            system_prompt_resume = f" Resume context:\n{resume_text}" if resume_text else ""

            messages = [
                {"role": "system", "content": f"{system_prompt_role}{system_prompt_skill}{system_prompt_resume}"},
                {"role": "user", "content": prompt_text}
            ]

            chat_completion = groq_client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192", # Or another suitable Groq model
                temperature=0.7,
                max_tokens=500
            )
            response_content = chat_completion.choices[0].message.content
            return Response({'response': response_content}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'AI response generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoiceInterviewControlView(APIView):
    """
    This view handles the overall flow of the voice interview,
    including starting, getting next question, submitting answer, and finishing.
    """
    def post(self, request):
        username = request.session.get('student_username')
        if not username:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')

        if action == 'start_interview':
            resume_file_base64 = request.data.get('resume_file_base64')
            resume_file_name = request.data.get('resume_file_name')

            if not resume_file_base64 or not resume_file_name:
                return Response({'error': 'Resume file is required to start interview.'}, status=status.HTTP_400_BAD_REQUEST)

            resume_bytes = base64.b64decode(resume_file_base64)
            resume_text = extract_resume_text(resume_bytes, resume_file_name)

            if not resume_text:
                return Response({'error': 'Failed to process resume. Please upload a valid file.'}, status=status.HTTP_400_BAD_REQUEST)

            skills = extract_skills_from_text(resume_text)
            if not skills:
                return Response({'error': 'No relevant skills extracted from resume.'}, status=status.HTTP_400_BAD_REQUEST)

            # Store voice interview state in session
            request.session['voice_interview_state'] = {
                'session_id': str(uuid.uuid4()),
                'username': username,
                'resume_text': resume_text,
                'skills': skills,
                'current_skill_index': 0,
                'questions': [], # Questions generated for each skill
                'responses': [], # User responses and AI feedback
                'exam_started': True,
                'start_time': datetime.datetime.utcnow().isoformat()
            }
            request.session.save()

            # Generate first question
            first_skill = skills[0]
            try:
                load_models()
                first_question = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"You are an AI interviewer. Ask a professional interview question related to this skill: {first_skill}. Resume context:\n{resume_text}"},
                        {"role": "user", "content": "Generate the first question."}
                    ],
                    model="llama3-8b-8192",
                    temperature=0.7,
                    max_tokens=300
                ).choices[0].message.content
                request.session['voice_interview_state']['questions'].append(first_question)
                request.session.save()
            except Exception as e:
                return Response({'error': f'Failed to generate first question: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'Voice interview started.',
                'current_skill': first_skill,
                'current_question': first_question,
                'total_skills': len(skills),
                'current_skill_index': 0
            }, status=status.HTTP_200_OK)

        elif action == 'submit_answer_and_get_next':
            interview_state = request.session.get('voice_interview_state')
            if not interview_state or not interview_state.get('exam_started'):
                return Response({'error': 'No active voice interview.'}, status=status.HTTP_400_BAD_REQUEST)

            user_response_text = request.data.get('user_response_text')
            input_mode = request.data.get('input_mode') # "voice" or "code"
            current_question = request.data.get('current_question')
            current_skill = request.data.get('current_skill')

            if not user_response_text or not input_mode or not current_question or not current_skill:
                return Response({'error': 'Missing data for submitting answer.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                load_models()
                feedback = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"You are an AI interviewer. Give feedback for the following answer related to skill: {current_skill}. Resume context:\n{interview_state['resume_text']}"},
                        {"role": "user", "content": user_response_text}
                    ],
                    model="llama3-8b-8192",
                    temperature=0.7,
                    max_tokens=500
                ).choices[0].message.content

                response_data = {
                    "username": username,
                    "session_id": interview_state['session_id'],
                    "skill": current_skill,
                    "question": current_question,
                    "response_text": user_response_text,
                    "feedback": feedback,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "mode": input_mode
                }
                db["voice_responses"].insert_one(response_data)
                interview_state['responses'].append(response_data)

                next_skill_index = interview_state['current_skill_index'] + 1
                if next_skill_index < len(interview_state['skills']):
                    next_skill = interview_state['skills'][next_skill_index]
                    next_question = groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": f"You are an AI interviewer. Ask a professional interview question related to this skill: {next_skill}. Resume context:\n{interview_state['resume_text']}"},
                            {"role": "user", "content": "Generate the next question."}
                        ],
                        model="llama3-8b-8192",
                        temperature=0.7,
                        max_tokens=300
                    ).choices[0].message.content
                    interview_state['questions'].append(next_question)
                    interview_state['current_skill_index'] = next_skill_index
                    request.session['voice_interview_state'] = interview_state
                    request.session.save()

                    return Response({
                        'message': 'Answer submitted, next question generated.',
                        'feedback': feedback,
                        'next_skill': next_skill,
                        'next_question': next_question,
                        'current_skill_index': next_skill_index,
                        'total_skills': len(interview_state['skills'])
                    }, status=status.HTTP_200_OK)
                else:
                    # End of interview
                    rating = calculate_performance_rating(interview_state['responses'])
                    db["voice_responses"].update_one(
                        {"session_id": interview_state['session_id'], "username": username},
                        {"$set": {"performance_rating": rating}},
                        upsert=True
                    )
                    del request.session['voice_interview_state'] # Clear state
                    request.session.save()
                    return Response({
                        'message': 'Interview completed.',
                        'feedback': feedback, # Last feedback
                        'final_summary': rating
                    }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': f'Processing answer or generating next question failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif action == 'end_interview_early':
            if 'voice_interview_state' in request.session:
                del request.session['voice_interview_state']
                request.session.save()
            return Response({'message': 'Voice interview ended early.'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)