"""
Configuration settings for the Voice Detection API
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_KEYS = os.getenv("API_KEYS", "sk_test_123456789,sk_prod_987654321").split(",")

# Supported Languages
SUPPORTED_LANGUAGES = ["Tamil", "English", "Hindi", "Malayalam", "Telugu", "Bengali"]

# Audio Configuration
SUPPORTED_AUDIO_FORMATS = ["mp3"]
MAX_AUDIO_SIZE_MB = 10
SAMPLE_RATE = 22050

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", "models/voice_detector.pkl")
CONFIDENCE_THRESHOLD = 0.5
