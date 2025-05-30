from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db, validate_password, send_email_verification_code # Import utilities
from core.serializers import StudentLoginSerializer, StudentRegisterSerializer, StudentForgotPasswordSerializer, UserDataSerializer
import bcrypt
import datetime
import random
from email_validator import validate_email, EmailNotValidError

class StudentLoginView(APIView):
    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = db["access_students"].find_one({"username": username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Set session variable for authentication (for Django's session-based auth)
            request.session['student_username'] = username
            request.session.save() # Ensure session is saved

            # Update last login and is_logged_in status
            db["access_students"].update_one(
                {"username": username},
                {"$set": {"last_login": datetime.datetime.utcnow(), "is_logged_in": True}}
            )
            # Return serialized user data (without sensitive info like password hash)
            user_data_for_response = {k: v for k, v in user.items() if k != 'password'}
            return Response(UserDataSerializer(user_data_for_response).data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials or user not approved.'}, status=status.HTTP_401_UNAUTHORIZED)


class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = serializer.validated_data['name']
        email = serializer.validated_data['email']
        phone = serializer.validated_data.get('phone', '')
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        confirm_password = serializer.validated_data['confirm_password']

        if password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password complexity
        password_errors = validate_password(password, username, email)
        if password_errors:
            return Response({'errors': password_errors}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email or username already exists in registrations or access
        if db["student_registrations"].find_one({"email": email}) or \
           db["access_students"].find_one({"email": email}):
            return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        if db["student_registrations"].find_one({"username": username}) or \
           db["access_students"].find_one({"username": username}):
            return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format and deliverability
        try:
            valid = validate_email(email, check_deliverability=False) # Set to True for real check
            email = valid.normalized
        except EmailNotValidError as e:
            return Response({'error': f'Invalid email format: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP and send email (simulate for now if SMTP not fully configured)
        otp = str(random.randint(100000, 999999))
        # In a real app, you'd store this OTP with an expiry and verify it later.
        # For this example, we'll simulate success.
        if send_email_verification_code(email, otp): # This will try to send actual email
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Store registration data in a temporary collection or session until OTP is verified
            # For this example, we'll directly insert into pending registrations
            new_student_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "username": username,
                "password": hashed_password,
                "role": "student",
                "status": "pending", # Status for admin approval
                "registration_date": datetime.datetime.utcnow(),
                "otp_code": otp, # Store OTP for verification
                "otp_attempts": 0,
                "ai_tokens": {"Text_to_Text": 15, "Voice_to_Voice": 15, "Face_to_Face": 15}, # Initial tokens
                "tokens": 15, # General tokens
                "exam_attempts": 0,
            }
            db["student_registrations"].insert_one(new_student_data)
            return Response({'message': 'Registration successful! Please check your email for OTP verification and await admin approval.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Failed to send OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentForgotPasswordView(APIView):
    def post(self, request):
        serializer = StudentForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        new_password = serializer.validated_data['new_password']
        confirm_new = serializer.validated_data['confirm_new_password']

        if new_password != confirm_new:
            return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user = db["access_students"].find_one({"username": username})
        if not user:
            return Response({'error': 'Username not found or not approved.'}, status=status.HTTP_404_NOT_FOUND)

        # Optional: Apply password validation
        # password_errors = validate_password(new_password, username, user.get("email", ""))
        # if password_errors:
        #     return Response({'errors': password_errors}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db["access_students"].update_one(
            {"username": username},
            {"$set": {"password": hashed_password}}
        )
        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)