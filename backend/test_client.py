"""
Test Client Script for Voice Detection API
This script demonstrates how to use the API with a real audio file.
"""
import requests
import base64
import sys
import argparse
from pathlib import Path


def encode_audio_file(file_path: str) -> str:
    """Read and encode an audio file to base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def detect_voice(
    api_url: str,
    api_key: str,
    audio_file: str,
    language: str = "English"
) -> dict:
    """
    Send a voice detection request to the API
    
    Args:
        api_url: Base URL of the API
        api_key: API key for authentication
        audio_file: Path to the MP3 audio file
        language: Language of the audio
        
    Returns:
        API response as dictionary
    """
    # Encode the audio file
    audio_base64 = encode_audio_file(audio_file)
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    
    payload = {
        "language": language,
        "audioFormat": "mp3",
        "audioBase64": audio_base64
    }
    
    # Send the request
    endpoint = f"{api_url.rstrip('/')}/api/voice-detection"
    response = requests.post(endpoint, headers=headers, json=payload)
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Test client for Voice Detection API"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--api-key",
        default="sk_test_123456789",
        help="API key for authentication"
    )
    parser.add_argument(
        "--audio",
        required=True,
        help="Path to the MP3 audio file"
    )
    parser.add_argument(
        "--language",
        choices=["Tamil", "English", "Hindi", "Malayalam", "Telugu", "Bengali"],
        default="English",
        help="Language of the audio (default: English)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.audio).exists():
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)
    
    # Check file extension
    if not args.audio.lower().endswith('.mp3'):
        print("Warning: File does not have .mp3 extension")
    
    print(f"Sending audio file: {args.audio}")
    print(f"Language: {args.language}")
    print(f"API URL: {args.url}")
    print("-" * 50)
    
    try:
        result = detect_voice(
            api_url=args.url,
            api_key=args.api_key,
            audio_file=args.audio,
            language=args.language
        )
        
        if result.get("status") == "success":
            print(f"✅ Status: {result['status']}")
            print(f"🎯 Classification: {result['classification']}")
            print(f"📊 Confidence Score: {result['confidenceScore']:.2f}")
            print(f"🌍 Language: {result['language']}")
            print(f"📝 Explanation: {result['explanation']}")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
