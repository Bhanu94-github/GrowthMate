from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import db
from core.serializers import AdminLoginSerializer, StudentRegistrationSerializer, UserDataSerializer, CourseSerializer, InstructorLogSerializer
from bson.objectid import ObjectId
import datetime

class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Hardcoded admin credentials (CHANGE IN PRODUCTION!)
        if username == "admin" and password == "admin123":
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = username
            request.session.save()
            return Response({'message': 'Logged in as Admin'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid admin credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class AdminPanelView(APIView):
    def get(self, request):
        if not request.session.get('admin_logged_in'):
            return Response({'error': 'Not authenticated as admin.'}, status=status.HTTP_401_UNAUTHORIZED)

        reg_col = db["student_registrations"]
        access_col = db["access_students"]
        not_access_col = db["not_access_students"]
        course_col = db["courses"]
        logs_col = db["instructor_logs"] # Assuming this is where instructor logs are stored

        pending_registrations = list(reg_col.find({"status": "pending"}))
        approved_students = list(access_col.find())
        rejected_students = list(not_access_col.find()) # Assuming 'not_access_students' holds rejected ones
        pending_courses = list(course_col.find({"status": "pending"}))
        approved_courses = list(course_col.find({"status": "approved"}))
        rejected_courses = list(course_col.find({"status": "rejected"}))
        instructor_logs = list(logs_col.find().sort("timestamp", -1).limit(50)) # Limit for performance

        response_data = {
            "summary": {
                "pending_students_count": len(pending_registrations),
                "approved_students_count": len(approved_students),
                "rejected_students_count": len(rejected_students),
            },
            "pending_registrations": StudentRegistrationSerializer(pending_registrations, many=True).data,
            "approved_students": UserDataSerializer(approved_students, many=True).data,
            "rejected_students": UserDataSerializer(rejected_students, many=True).data,
            "pending_courses": CourseSerializer(pending_courses, many=True).data,
            "approved_courses": CourseSerializer(approved_courses, many=True).data,
            "rejected_courses": CourseSerializer(rejected_courses, many=True).data,
            "instructor_logs": InstructorLogSerializer(instructor_logs, many=True).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.session.get('admin_logged_in'):
            return Response({'error': 'Not authenticated as admin.'}, status=status.HTTP_401_UNAUTHORIZED)

        action = request.data.get('action')
        item_id = request.data.get('item_id') # Can be student_id or course_id

        if not action or not item_id:
            return Response({'error': 'Action and item_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            object_id = ObjectId(item_id)
        except Exception:
            return Response({'error': 'Invalid item ID format.'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'approve_student':
            student_data = db["student_registrations"].find_one({"_id": object_id})
            if not student_data:
                return Response({'error': 'Student registration not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Insert into access_students (remove OTP and status fields)
            student_data_for_access = {k: v for k, v in student_data.items() if k not in ['otp_code', 'otp_attempts', 'status']}
            db["access_students"].insert_one(student_data_for_access)
            db["student_registrations"].delete_one({"_id": object_id})
            return Response({'message': f'Student {student_data.get("username")} approved.'}, status=status.HTTP_200_OK)

        elif action == 'reject_student':
            student_data = db["student_registrations"].find_one({"_id": object_id})
            if not student_data:
                return Response({'error': 'Student registration not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Insert into not_access_students
            db["not_access_students"].insert_one(student_data)
            db["student_registrations"].delete_one({"_id": object_id})
            return Response({'message': f'Student {student_data.get("username")} rejected.'}, status=status.HTTP_200_OK)

        elif action == 'approve_course':
            result = db["courses"].update_one({"_id": object_id}, {"$set": {"status": "approved"}})
            if result.modified_count == 1:
                return Response({'message': 'Course approved.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Course not found or already approved.'}, status=status.HTTP_404_NOT_FOUND)

        elif action == 'reject_course':
            result = db["courses"].update_one({"_id": object_id}, {"$set": {"status": "rejected"}})
            if result.modified_count == 1:
                return Response({'message': 'Course rejected.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Course not found or already rejected.'}, status=status.HTTP_404_NOT_FOUND)

        elif action == 'update_student_registration':
            # This action would be for updating details of a pending registration
            updated_data = request.data.get('updated_data', {})
            if not updated_data:
                return Response({'error': 'No update data provided.'}, status=status.HTTP_400_BAD_REQUEST)

            result = db["student_registrations"].update_one(
                {"_id": object_id},
                {"$set": updated_data}
            )
            if result.modified_count == 1:
                return Response({'message': 'Student registration updated successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Student registration not found or no changes made.'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)