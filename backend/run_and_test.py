"""
Run the Voice Detection API server and test it
"""
import subprocess
import sys
import time
import requests
import base64
import os
import threading

def run_server():
    """Run the uvicorn server"""
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ])

def test_api(audio_file: str, language: str):
    """Test the API with an audio file"""
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Check if server is ready
    max_retries = 10
    for i in range(max_retries):
        try:
            r = requests.get("http://127.0.0.1:8000/api/health")
            if r.status_code == 200:
                print("Server is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("Server failed to start")
        return
    
    # Read and encode audio
    print(f"\nTesting with: {audio_file}")
    print(f"Language: {language}")
    print("-" * 50)
    
    with open(audio_file, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    
    # Make request
    response = requests.post(
        "http://127.0.0.1:8000/api/voice-detection",
        headers={
            "Content-Type": "application/json",
            "x-api-key": "sk_test_123456789"
        },
        json={
            "language": language,
            "audioFormat": "mp3",
            "audioBase64": audio_base64
        }
    )
    
    result = response.json()
    
    if result.get("status") == "success":
        print(f"✅ Status: {result['status']}")
        print(f"🎯 Classification: {result['classification']}")
        print(f"📊 Confidence Score: {result['confidenceScore']:.2f}")
        print(f"🌍 Language: {result['language']}")
        print(f"📝 Explanation: {result['explanation']}")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", default="samples/audio_test.mp3")
    parser.add_argument("--language", required=True, help="Language of the audio (Tamil, English, Hindi, Malayalam, Telugu)")
    parser.add_argument("--server-only", action="store_true", help="Only run the server")
    args = parser.parse_args()
    
    if args.server_only:
        print("Starting server only...")
        run_server()
    else:
        # Start server in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Run test
        try:
            test_api(args.audio, args.language)
        except KeyboardInterrupt:
            pass
        
        print("\nPress Ctrl+C to stop the server, or it will stop automatically.")
        input("Press Enter to exit...")
