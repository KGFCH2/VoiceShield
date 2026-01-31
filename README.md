# VoiceShield AI - Voice Detection System

[![Live Demo](https://img.shields.io/badge/Demo-Live_Website-sky?style=for-the-badge&logo=vercel)](https://voice-shield.vercel.app/)
[![API Backend](https://img.shields.io/badge/Backend-Render-blue?style=for-the-badge&logo=render)](https://voiceshield-tz3i.onrender.com)

A high-performance FastAPI-based system that uses heuristic audio signal processing to distinguish between human voices and AI-generated speech. Specifically optimized for Tamil, English, Hindi, Malayalam, and Telugu.

## 🌟 Key Features
- **🎯 AI vs Human voice detection**: High-precision heuristic engine.
- **🌍 Multi-lingual support**: Tamil, English, Hindi, Malayalam, Telugu.
- **🎨 Modern Dashboard**: Interactive web interface ([Live Demo](https://voice-shield.vercel.app/)).
- **📊 Confidence Scoring**: Detailed explanations for every classification.
- **📖 OpenAPI documentation**: Fully documented at `/docs`.

## 🎙️ Audio Support & Limitations
To ensure the highest accuracy, please follow these guidelines:
- **Speech Focus**: Optimized for clear human speech and singing. Heavy background noise or pure instrumental music may reduce accuracy.
- **Format**: Currently supports **MP3** files only.
- **File Size**: Maximum limit of **10MB** per request.
- **Duration**: Minimum recommended length of **0.5 seconds**.
- **Languages**: You must select one of the 5 supported languages (**Tamil, English, Hindi, Malayalam, or Telugu**) in the request.

## 📁 Project Structure

```
Voice/
├── backend/
│   ├── app/                 # FastAPI application logic
│   ├── tests/               # Unit and integration tests
│   ├── requirements.txt     # Backend dependencies
│   ├── .env                 # API Keys and Config
│   └── run_and_test.py      # CLI diagnostic tool
├── frontend/
│   └── index.html           # Modern Web Dashboard
└── README.md
```

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg**: Required for MP3 processing. (Ensures system can decode audio bytes).

### 2. Installation
```powershell
cd Voice/backend
pip install -r requirements.txt
```

### 3. Start the Server
```powershell
# Run from the backend directory
cd Voice/backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Open the Interface
Open **[frontend/index.html](frontend/index.html)** in your browser to start testing visually. Or visit **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** for the API documentation.

---

## 🛠️ API & Testing

### Endpoint: `POST /api/voice-detection`
**Headers:**
- `x-api-key`: `sk_test_123456789`
- `Content-Type`: `application/json`

**Sample CLI Test:**
```powershell
cd backend
python run_and_test.py --audio audio_test.mp3 --language Hindi
```

---

## 🔍 How it Works
The system uses **Digital Signal Processing (DSP)** via Librosa to analyze audio at a consistent sample rate of **22,050 Hz**. It extracts 8 distinct acoustic dimensions:
1. **Pitch Consistency**: Modern TTS often has "too perfect" pitch stability.
2. **Spectral Flatness**: Robotic voices exhibit different noise floor patterns.
3. **Harmonic Structure**: Detects unnatural layering in generated audio.
4. **Breath Patterns**: Identifies the presence of natural, organic pauses.
5. **Micro-variations**: Small natural variations present in human voice that AI lacks.
6. **MFCC Patterns**: Analyzing the frequency spectrum for "robotic" textures.
7. **Prosodic Features**: Rhythm and intonation patterns.
8. **Spectral Dynamics**: How frequency components change over time.

---
© 2026 VoiceShield AI | Built with FastAPI & Librosa | Licensed under [MIT](LICENSE)

## API Documentation

Once the server is running, access the documentation at:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## API Usage

### Endpoint

```
POST /api/voice-detection
```

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | application/json |
| x-api-key | Yes | Your API key |

### Request Body

```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU2LjM2LjEwMAAAAAAA..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| language | string | One of: Tamil, English, Hindi, Malayalam, Telugu |
| audioFormat | string | Must be "mp3" |
| audioBase64 | string | Base64-encoded MP3 audio |

### Response (Success)

```json
{
  "status": "success",
  "language": "Tamil",
  "classification": "AI_GENERATED",
  "confidenceScore": 0.91,
  "explanation": "Unnatural pitch consistency and robotic speech patterns detected"
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" or "error" |
| language | string | Language of the audio |
| classification | string | "AI_GENERATED" or "HUMAN" |
| confidenceScore | float | Value between 0.0 and 1.0 |
| explanation | string | Reason for the classification |

### Response (Error)

```json
{
  "status": "error",
  "message": "Invalid API key or malformed request"
}
```

### cURL Example

```bash
curl -X POST http://127.0.0.1:8001/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_test_123456789" \
  -d '{
    "language": "English",
    "audioFormat": "mp3",
    "audioBase64": "YOUR_BASE64_AUDIO_HERE"
  }'
```

### Python Example

```python
import requests
import base64

# Read and encode audio file
with open("sample.mp3", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

# Make API request
response = requests.post(
    "http://127.0.0.1:8001/api/voice-detection",
    headers={
        "Content-Type": "application/json",
        "x-api-key": "sk_test_123456789"
    },
    json={
        "language": "English",
        "audioFormat": "mp3",
        "audioBase64": audio_base64
    }
)

print(response.json())
```

## Other Endpoints

### Health Check
```
GET /api/health
```

### Supported Languages
```
GET /api/languages
```

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

## Detection Methodology

The API analyzes multiple audio features to determine if a voice is AI-generated:

1. **Pitch Analysis** - AI voices often have unnaturally consistent pitch
2. **Spectral Characteristics** - Analyzes frequency distribution patterns
3. **Harmonic Structure** - Natural voices have complex harmonic patterns
4. **MFCC Patterns** - Mel-frequency cepstral coefficients analysis
5. **Prosodic Features** - Rhythm, stress, and intonation patterns
6. **Micro-variations** - Small natural variations present in human voice

## Configuration

Environment variables in `backend/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| API_KEYS | Comma-separated list of valid API keys | sk_test_123456789 |
| PORT | Server port | 8001 |

## Deployment

The API can be deployed to any cloud platform that supports Python (e.g., Render, Railway, or AWS).

### Production Checklist

- [ ] Set secure API keys
- [ ] Enable HTTPS
- [ ] Configure CORS for your domain
- [ ] Ensure FFmpeg is installed on the host

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
