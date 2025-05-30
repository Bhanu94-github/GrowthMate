from pymongo import MongoClient
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
import bcrypt
import pymongo
from random import sample
from datetime import datetime

# MongoDB connection
# Ensure your MongoDB server is running and accessible
client = MongoClient("mongodb://localhost:27017/")
db = client["instructor"]  # Your primary DB name
skill_db = client["skill_based"] # Your skill-based questions DB

# Gmail SMTP credentials (replace with environment variables in production)
GMAIL_ADDRESS = "palivelabhanuprakash99@gmail.com" # Placeholder - USE ENVIRONMENT VARIABLES!
GMAIL_APP_PASSWORD = "ywgvvgplhdgwwewc" # Placeholder - USE ENVIRONMENT VARIABLES!

# Common passwords to block
COMMON_PASSWORDS = [
    "password123", "qwerty123", "admin123", "12345678", "welcome123",
    "password1", "abc123", "letmein", "test123", "changeme"
]

ALL_SKILLS = ["python", "sql", "java", "javascript", "html", "css", "c++", "mongodb"]

def validate_password(password, username, email):
    """
    Validates password complexity and common patterns.
    Returns a list of error messages, or empty list if valid.
    """
    errors = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must include at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        errors.append("Password must include at least one lowercase letter.")
    if not re.search(r'\d', password):
        errors.append("Password must include at least one digit.")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Password must include at least one special character.")
    if username.lower() in password.lower() or email.lower() in password.lower():
        errors.append("Password cannot contain your username or email.")
    if password.lower() in [p.lower() for p in COMMON_PASSWORDS]:
        errors.append("Password is too common and not allowed.")
    return errors

def send_email_verification_code(to_email, otp):
    """
    Sends an OTP to the specified email address.
    Returns True on success, False on failure.
    """
    try:
        message = MIMEMultipart()
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = "Email Verification OTP"
        body = f"Your OTP for registration is {otp}"
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}") # Log the error
        return False

def get_all_questions(skill, difficulty):
    """
    Retrieves questions: 8 MCQs, 2 coding, 5 blanks for the given skill and difficulty.
    """
    collection = skill_db[skill] # Use skill_db here

    # Fetch questions by type and difficulty
    mcqs = list(collection.find({"difficulty": difficulty, "type": "mcqs"}))
    coding = list(collection.find({"difficulty": difficulty, "type": "coding"}))
    blanks = list(collection.find({"difficulty": difficulty, "type": "blanks"}))

    # Sample from each group
    selected_mcqs = sample(mcqs, min(8, len(mcqs)))
    selected_coding = sample(coding, min(2, len(coding)))
    selected_blanks = sample(blanks, min(5, len(blanks)))

    # Combine and shuffle
    questions = selected_mcqs + selected_coding + selected_blanks
    return sample(questions, len(questions))

# Logging function (from instructor_panel.py)
def log_token_history(student_username, actor_username, action, tokens_changed, module="general"):
    """
    Logs token changes for students.
    actor_username can be 'system' for automated deductions.
    """
    db["token_logs"].insert_one({
        "student": student_username,
        "actor": actor_username, # Renamed from 'instructor' to 'actor' for broader use
        "action": action,
        "module": module,
        "tokens_changed": tokens_changed,
        "timestamp": datetime.utcnow()
    })