from django.urls import path
from core.views.student_panel_views import StudentLoginView, StudentRegisterView, StudentForgotPasswordView
from core.views.student_dashboard_views import StudentDashboardView
from core.views.instructor_panel_views import InstructorLoginView, InstructorDashboardView, InstructorAnalyticsView, TokenManagementView
from core.views.admin_panel_views import AdminLoginView, AdminPanelView
from core.views.ai_assessment_views import AIAssessmentView, AIAssessmentQuestionView, AIAssessmentSubmitView
from core.views.voice_views import VoiceTranscriptionView, VoiceSpeechGenerationView, VoiceChatResponseView

urlpatterns = [
    # Student Panel APIs
    path('student/login/', StudentLoginView.as_view(), name='api-student-login'),
    path('student/register/', StudentRegisterView.as_view(), name='api-student-register'),
    path('student/forgot-password/', StudentForgotPasswordView.as_view(), name='api-student-forgot-password'),

    # Student Dashboard APIs
    path('student/dashboard/', StudentDashboardView.as_view(), name='api-student-dashboard'),

    # Instructor Panel APIs
    path('instructor/login/', InstructorLoginView.as_view(), name='api-instructor-login'),
    path('instructor/dashboard/', InstructorDashboardView.as_view(), name='api-instructor-dashboard'),
    path('instructor/analytics/', InstructorAnalyticsView.as_view(), name='api-instructor-analytics'),
    path('instructor/token-management/', TokenManagementView.as_view(), name='api-instructor-token-management'),


    # Admin Panel APIs
    path('admin/login/', AdminLoginView.as_view(), name='api-admin-login'),
    path('admin/panel/', AdminPanelView.as_view(), name='api-admin-panel'),

    # AI Assessment APIs
    path('ai-assessment/start/', AIAssessmentView.as_view(), name='api-ai-assessment-start'),
    path('ai-assessment/question/', AIAssessmentQuestionView.as_view(), name='api-ai-assessment-question'),
    path('ai-assessment/submit/', AIAssessmentSubmitView.as_view(), name='api-ai-assessment-submit'),

    # Voice APIs
    path('voice/transcribe/', VoiceTranscriptionView.as_view(), name='api-voice-transcribe'),
    path('voice/generate-speech/', VoiceSpeechGenerationView.as_view(), name='api-voice-generate-speech'),
    path('voice/chat-response/', VoiceChatResponseView.as_view(), name='api-voice-chat-response'),

    # Add more API endpoints as needed (e.g., for course management, feedback, etc.)
]