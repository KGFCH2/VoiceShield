# AI Voice Detection API - Instructions & Documentation

This project is a REST API built with FastAPI that uses heuristic-based audio signal processing to distinguish between human voices and AI-generated speech. It specifically supports Tamil, English, Hindi, Malayalam, and Telugu.

## 🚀 Setup and Execution

1.  **Dependencies**:
    Ensure you have Python 3.10+ and FFmpeg installed. Navigate to the `backend` directory first.
    ```powershell
    cd backend
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Configure your API keys in the `backend/.env` file:
    ```env
    API_KEYS=sk_test_123456789,sk_prod_987654321
    ```

3.  **Running the Server**:
    Run from the `backend` directory.
    ```powershell
    cd backend
    # Try port 8000 (default) or 8001 if 8000 is in use
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
    ```

4.  **Testing**:
    Use the provided test script from the `backend` directory:
    ```powershell
    cd backend
    python run_and_test.py --audio your_audio_file.mp3 --language Tamil
    ```

---

## 🎨 Frontend Dashboard (Project Demo)

A modern, web-based dashboard is provided in the `frontend/` directory. You can access the live version here:
**[https://voice-shield.vercel.app/](https://voice-shield.vercel.app/)**

### **How to use the Dashboard:**
1.  Ensure your API server is running (`port 8001`).
2.  Open **[frontend/index.html](frontend/index.html)** directly in your web browser (Chrome/Edge recommended).
3.  **Upload** an MP3 file (drag and drop or click).
4.  Select the **Language**.
5.  Click **Run Detection**.

---

## 🧪 API Testing Guide

### **Standard Request Format (JSON)**
When testing via Swagger ([http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)) or external testers:

**Headers:**
*   `x-api-key`: `sk_test_123456789`
*   `Content-Type`: `application/json`

**Body:**
```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "PASTE_YOUR_FULL_BASE64_STRING_HERE"
}
```

### **Common Troubleshooting**
*   **FFmpeg Not Found**: If you see a `RuntimeWarning: Couldn't find ffmpeg`, ensure FFmpeg is installed and added to your system's PATH. On Windows, you can download it from `gyan.dev` and add the `bin` folder to your Environment Variables.
*   **400 Bad Request**: Ensure your `audioBase64` string does not contain spaces or newlines.
*   **401 Unauthorized**: Check that the `x-api-key` header is present and exactly matches the key in your `.env`.
*   **Method Not Allowed**: Ensure you are using **POST**, not GET, for the `/voice-detection` endpoint.
*   **Connection Error**: If using an external portal (like a competition website), you must deploy your API to a public URL (e.g., via Render or ngrok) as they cannot reach `127.0.0.1`.

---

## ⚖️ License
This software is shared under the **MIT License**. You are free to use, modify, and distribute it. See the [LICENSE](LICENSE) file for the full legal text.

---

## 📁 Project Structure & File Functions

### 1. `backend/app/` (Core Application)
*   **[backend/app/main.py](backend/app/main.py)**: The entry point of the API.
*   **[backend/app/routes.py](backend/app/routes.py)**: Defines the API endpoints.
*   **[backend/app/config.py](backend/app/config.py)**: Central configuration file.
*   **[backend/app/schemas.py](backend/app/schemas.py)**: Pydantic models for validation.

### 2. `backend/app/models/` (Logic Layer)
*   **[backend/app/models/voice_detector.py](backend/app/models/voice_detector.py)**: The "brain" of the project. Analysis logic.

### 3. `backend/app/utils/` (Heuristics & Processing)
*   **[backend/app/utils/audio_processor.py](backend/app/utils/audio_processor.py)**: Low-level audio processing and feature extraction.

### 4. Backend Utilities
*   **[backend/run_and_test.py](backend/run_and_test.py)**: Diagnostic CLI tool for end-to-end testing.
*   **[backend/debug_test.py](backend/debug_test.py)**: Raw feature score viewer for debugging.
*   **[backend/requirements.txt](backend/requirements.txt)**: Lists all backend dependencies.
*   **[backend/.env](backend/.env)**: Environment configuration.


---

## 🔍 How Detection Works

The API uses an **Enhanced Heuristic Model** rather than a simple black-box ML model. It looks for:
*   **AI Indicators**: Low pitch variance, "too perfect" harmonic structures, and robotic micro-variations.
*   **Human Indicators**: High pitch range (especially in singing), natural breathing pauses, and rich spectral dynamics.

Each characteristic is weighted, and the final score (0.0 to 1.0) determines the classification.

---

## 📄 License

This software is shared under the **MIT License**. You are free to use, modify, and distribute it. See the [LICENSE](LICENSE) file for the full legal text.
