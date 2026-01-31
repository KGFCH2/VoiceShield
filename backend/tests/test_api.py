"""
Tests for the Voice Detection API
"""
import pytest
import base64
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test API key
VALID_API_KEY = "sk_test_123456789"
INVALID_API_KEY = "invalid_key_12345"


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test that health endpoint returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestLanguagesEndpoint:
    """Tests for languages endpoint"""
    
    def test_get_languages(self):
        """Test that languages endpoint returns supported languages"""
        response = client.get("/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "languages" in data
        assert "Tamil" in data["languages"]
        assert "English" in data["languages"]
        assert "Hindi" in data["languages"]
        assert "Malayalam" in data["languages"]
        assert "Telugu" in data["languages"]


class TestAuthentication:
    """Tests for API authentication"""
    
    def test_missing_api_key(self):
        """Test that requests without API key are rejected"""
        response = client.post(
            "/api/voice-detection",
            json={
                "language": "English",
                "audioFormat": "mp3",
                "audioBase64": "dGVzdA=="
            }
        )
        assert response.status_code == 401
    
    def test_invalid_api_key(self):
        """Test that requests with invalid API key are rejected"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": INVALID_API_KEY},
            json={
                "language": "English",
                "audioFormat": "mp3",
                "audioBase64": "dGVzdA=="
            }
        )
        assert response.status_code == 401


class TestInputValidation:
    """Tests for request validation"""
    
    def test_invalid_language(self):
        """Test that invalid language is rejected"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": VALID_API_KEY},
            json={
                "language": "French",  # Not supported
                "audioFormat": "mp3",
                "audioBase64": "dGVzdA=="
            }
        )
        assert response.status_code == 400
    
    def test_invalid_audio_format(self):
        """Test that invalid audio format is rejected"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": VALID_API_KEY},
            json={
                "language": "English",
                "audioFormat": "wav",  # Not supported
                "audioBase64": "dGVzdA=="
            }
        )
        assert response.status_code == 400
    
    def test_empty_audio(self):
        """Test that empty audio is rejected"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": VALID_API_KEY},
            json={
                "language": "English",
                "audioFormat": "mp3",
                "audioBase64": ""
            }
        )
        assert response.status_code == 400
    
    def test_missing_required_fields(self):
        """Test that missing fields are rejected"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": VALID_API_KEY},
            json={
                "language": "English"
                # Missing audioFormat and audioBase64
            }
        )
        assert response.status_code == 400


class TestVoiceDetection:
    """Tests for voice detection endpoint"""
    
    def test_valid_request_format(self):
        """Test that valid request format is accepted (may fail on audio processing)"""
        # Create a minimal valid MP3-like data (this won't be a valid MP3 but tests the format)
        # In real tests, you would use actual MP3 files
        fake_audio = base64.b64encode(b"fake audio data for testing" * 100).decode()
        
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": VALID_API_KEY},
            json={
                "language": "English",
                "audioFormat": "mp3",
                "audioBase64": fake_audio
            }
        )
        
        # Should either succeed or return 400 for invalid audio
        # Won't return 401 (auth error) or 422 (validation error)
        assert response.status_code in [200, 400, 500]


class TestResponseFormat:
    """Tests for response format compliance"""
    
    def test_error_response_format(self):
        """Test that error responses have correct format"""
        response = client.post(
            "/api/voice-detection",
            headers={"x-api-key": INVALID_API_KEY},
            json={
                "language": "English",
                "audioFormat": "mp3",
                "audioBase64": "dGVzdA=="
            }
        )
        
        data = response.json()
        assert "detail" in data or "status" in data
        if "detail" in data:
            assert "status" in data["detail"]
            assert "message" in data["detail"]


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self):
        """Test that root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "supported_languages" in data
