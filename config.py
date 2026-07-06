"""
CommunityPulse AI — Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'communitypulse-ai-secret-2024')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'communitypulse.db')
    DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # AI Configuration
    GEMINI_MODEL = 'gemini-2.0-flash'
    AI_ENABLED = bool(GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here')
    
    # App metadata
    APP_NAME = 'CommunityPulse AI'
    APP_VERSION = '1.0.0'
