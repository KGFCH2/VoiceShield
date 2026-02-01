"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal, Dict, Any
from app.config import SUPPORTED_LANGUAGES


class VoiceDetectionRequest(BaseModel):
    """Request schema for voice detection API"""
    
    language: str = Field(
        ...,
        description="Language of the audio (Tamil, English, Hindi, Malayalam, Telugu, Bengali)"
    )
    audioFormat: str = Field(
        ...,
        description="Audio format (must be 'mp3')"
    )
    audioBase64: str = Field(
        ...,
        description="Base64-encoded MP3 audio data",
        min_length=1,  # Relaxed for initial testing
        examples=["SUQzBAAAAAECBVRTU0UAAAAOAAADTGF2ZjYwLjE2LjEwMEdFT0IAAQFjAAADYXBwbGljYXRpb24ve..."]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "language": "Tamil",
                "audioFormat": "mp3",
                "audioBase64": "SUQzBAAAAAECBVRTU0UAAAAOAAADTGF2ZjYwLjE2LjEwMEdFT0IAAQFjAAADYXBwbGljYXRpb24veC1jMnBhLW1hbmlmZXN0LXN0b3JlAGMycGEAYzJwYSBtYW5pZmVzdCBzdG9yZQAAAECnanVtYgAAAB5qdW1kYzJwYQARABCAAACqADibcQNjMnBhAAAAQIFqdW1iAAAAR2p1bWRjMm1hABEAEIAAAKoAOJtxA3VybjpjMnBhOjkxNTY2OTZkLTVlNjktNDA3ZS1iY2FiLWYwNzYwZGY4OThiOAAAAAJ7anVtYgAAAClqdW1kYzJhcwARABCAAACqADibcQNjMnBhLmFzc2VydGlvbnMAAAAAy2p1bWIAAAApanVtZGNib3IAEQAQgAAAqgA4m3EDYzJwYS5hY3Rpb25zLnYyAAAAAJpjYm9yoWdhY3Rpb25zgaNmYWN0aW9ubGMycGEuY3JlYXRlZG1zb2Z0d2FyZUFnZW50akVs"
            }
        }
    )
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        # Normalize to title case for comparison
        normalized = v.strip().title()
        if normalized not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)}")
        return normalized
    
    @field_validator('audioFormat')
    @classmethod
    def validate_audio_format(cls, v: str) -> str:
        if v.lower() != 'mp3':
            raise ValueError("Only 'mp3' format is supported")
        return v.lower()
    
    @field_validator('audioBase64')
    @classmethod
    def validate_audio_base64(cls, v: str) -> str:
        # Basic validation - check if it looks like base64
        v = v.strip()
        if not v:
            raise ValueError("Audio data cannot be empty")
        return v


class AnalysisDetail(BaseModel):
    """Detail of individual analysis component"""
    score: float
    detail: str


class AnalysisDetails(BaseModel):
    """Complete analysis details"""
    pitch_analysis: AnalysisDetail
    spectral_analysis: AnalysisDetail
    harmonic_analysis: AnalysisDetail
    mfcc_analysis: AnalysisDetail
    prosodic_analysis: AnalysisDetail
    micro_variation_analysis: AnalysisDetail


class VoiceDetectionResponse(BaseModel):
    """Response schema for successful voice detection"""
    
    status: Literal["success"] = "success"
    language: str = Field(
        ...,
        description="Language of the analyzed audio"
    )
    classification: Literal["AI_GENERATED", "HUMAN"] = Field(
        ...,
        description="Classification result"
    )
    confidenceScore: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    explanation: str = Field(
        ...,
        description="Short explanation for the classification decision"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "language": "Tamil",
                "classification": "AI_GENERATED",
                "confidenceScore": 0.91,
                "explanation": "Unnatural pitch consistency and robotic speech patterns detected"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    
    status: Literal["error"] = "error"
    message: str = Field(
        ...,
        description="Error message describing what went wrong"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Invalid API key or malformed request"
            }
        }
    )
