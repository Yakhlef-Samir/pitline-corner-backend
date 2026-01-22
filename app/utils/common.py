# Common utility functions
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> dict:
    """Validate password strength and return feedback"""
    feedback = {
        "is_valid": True,
        "errors": [],
        "score": 0
    }
    
    if len(password) < 8:
        feedback["errors"].append("Password must be at least 8 characters long")
        feedback["is_valid"] = False
    else:
        feedback["score"] += 1
    
    if not re.search(r'[A-Z]', password):
        feedback["errors"].append("Password must contain at least one uppercase letter")
        feedback["is_valid"] = False
    else:
        feedback["score"] += 1
    
    if not re.search(r'[a-z]', password):
        feedback["errors"].append("Password must contain at least one lowercase letter")
        feedback["is_valid"] = False
    else:
        feedback["score"] += 1
    
    if not re.search(r'\d', password):
        feedback["errors"].append("Password must contain at least one number")
        feedback["is_valid"] = False
    else:
        feedback["score"] += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        feedback["errors"].append("Password must contain at least one special character")
    else:
        feedback["score"] += 1
    
    return feedback


def format_display_name(first_name: Optional[str], last_name: Optional[str]) -> str:
    """Format display name from first and last name"""
    if first_name and last_name:
        return f"{first_name.strip()} {last_name.strip()}"
    elif first_name:
        return first_name.strip()
    elif last_name:
        return last_name.strip()
    else:
        return "Anonymous"
