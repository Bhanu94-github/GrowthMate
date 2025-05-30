from rest_framework import serializers

# --- User/Auth Related Serializers ---

class StudentLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class StudentRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True) # Assuming optional
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class StudentForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

class UserDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    tokens = serializers.IntegerField(required=False)
    ai_tokens = serializers.JSONField(required=False) # For nested dicts like {"Text_to_Text": 15}
    exam_attempts = serializers.IntegerField(required=False)
    progress = serializers.ListField(required=False)
    submitted_essays = serializers.ListField(required=False)
    feedbacks = serializers.ListField(required=False)
    notifications = serializers.ListField(required=False)


class InstructorLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class InstructorSerializer(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.CharField(required=False)
    # Add other instructor fields as needed

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

# --- Data Related Serializers ---

class TokenLogSerializer(serializers.Serializer):
    student = serializers.CharField()
    instructor = serializers.CharField()
    action = serializers.CharField()
    module = serializers.CharField()
    tokens_changed = serializers.IntegerField()
    timestamp = serializers.DateTimeField()

class AssessmentResultSerializer(serializers.Serializer):
    username = serializers.CharField()
    score = serializers.IntegerField()
    skill = serializers.CharField()
    difficulty = serializers.CharField()
    total = serializers.IntegerField()
    responses = serializers.ListField() # List of dicts for individual question responses
    session_id = serializers.CharField()
    # Add other fields like timestamp if present in DB

class CourseSerializer(serializers.Serializer):
    _id = serializers.CharField() # MongoDB ObjectId as string
    title = serializers.CharField()
    instructor = serializers.CharField()
    description = serializers.CharField(required=False)
    status = serializers.CharField() # e.g., "pending", "approved", "rejected"

class StudentRegistrationSerializer(serializers.Serializer):
    _id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    username = serializers.CharField()
    # No password here, as it's sensitive and not for direct serialization in this context

class InstructorLogSerializer(serializers.Serializer):
    username = serializers.CharField()
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()

# --- AI Assessment Specific Serializers ---
class QuestionSerializer(serializers.Serializer):
    id = serializers.CharField() # MongoDB ObjectId as string
    question = serializers.CharField()
    type = serializers.CharField() # "mcqs", "coding", "blanks"
    options = serializers.ListField(child=serializers.CharField(), required=False)
    constraints = serializers.CharField(required=False)
    input = serializers.CharField(required=False)
    output = serializers.CharField(required=False)
    explanation = serializers.CharField(required=False)
    answer = serializers.CharField(required=False) # Only for internal use/admin, not to send to frontend directly

class AssessmentStartSerializer(serializers.Serializer):
    skill = serializers.CharField(required=True)
    difficulty = serializers.CharField(required=True)

class AssessmentAnswerSerializer(serializers.Serializer):
    question_id = serializers.CharField(required=True)
    selected_answer = serializers.CharField(required=True, allow_blank=True) # Can be blank for coding/text areas

class AssessmentFinishSerializer(serializers.Serializer):
    # No specific fields needed, as it uses session data
    pass

# --- Voice Specific Serializers ---
class AudioTranscriptionSerializer(serializers.Serializer):
    audio = serializers.CharField(required=True) # Base64 encoded audio

class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)

class ChatPromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
    skill = serializers.CharField(required=False, allow_blank=True)
    resume_text = serializers.CharField(required=False, allow_blank=True)
    is_question = serializers.BooleanField(required=False, default=True)