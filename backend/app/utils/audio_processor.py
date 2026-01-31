"""
Audio Processing Utilities
Handles base64 decoding, audio loading, and feature extraction
"""
import base64
import io
import tempfile
import os
import numpy as np
import librosa
from pydub import AudioSegment
from typing import Tuple, Dict, Any

from app.config import SAMPLE_RATE


def decode_base64_audio(audio_base64: str) -> bytes:
    """
    Decode base64-encoded audio string to bytes
    
    Args:
        audio_base64: Base64-encoded audio string
        
    Returns:
        Decoded audio bytes
        
    Raises:
        ValueError: If base64 decoding fails
    """
    try:
        # Remove any whitespace or newlines
        audio_base64 = audio_base64.strip().replace('\n', '').replace('\r', '')
        
        # Handle data URL format if present
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
            
        return base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 audio: {str(e)}")


def load_audio_from_bytes(audio_bytes: bytes, audio_format: str = "mp3") -> Tuple[np.ndarray, int]:
    """
    Load audio from bytes into numpy array
    
    Args:
        audio_bytes: Raw audio bytes
        audio_format: Audio format (mp3)
        
    Returns:
        Tuple of (audio_array, sample_rate)
    """
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Load using librosa
            audio_array, sr = librosa.load(temp_path, sr=SAMPLE_RATE, mono=True)
            return audio_array, sr
        except Exception as inner_e:
            # Check if this is likely an FFmpeg issue
            if "audioread" in str(inner_e).lower() or "ffmpeg" in str(inner_e).lower():
                raise ValueError("FFmpeg not found. MP3 decoding requires FFmpeg to be installed and in the system PATH.")
            raise ValueError(f"Failed to load audio: {str(inner_e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise ValueError(f"Failed to load audio: {str(e)}")


def extract_audio_features(audio: np.ndarray, sr: int) -> Dict[str, Any]:
    """
    Extract comprehensive audio features for AI detection
    
    Features extracted:
    - MFCCs (Mel-frequency cepstral coefficients)
    - Spectral features (centroid, bandwidth, rolloff, flatness)
    - Pitch features (fundamental frequency statistics)
    - Temporal features (zero-crossing rate, RMS energy)
    - Prosodic features
    
    Args:
        audio: Audio signal as numpy array
        sr: Sample rate
        
    Returns:
        Dictionary containing all extracted features
    """
    features = {}
    
    # 🏎️ PERFORMANCE OPTIMIZATION: Limit audio to first 8 seconds for faster analysis
    # Most AI detection patterns are visible within the first few seconds.
    max_samples = sr * 8
    if len(audio) > max_samples:
        audio = audio[:max_samples]
    
    # Ensure minimum audio length
    if len(audio) < sr * 0.5:  # At least 0.5 seconds
        # Pad with zeros if too short
        audio = np.pad(audio, (0, int(sr * 0.5) - len(audio)), mode='constant')
    
    # 1. MFCCs - crucial for voice quality analysis
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
    features['mfcc_mean'] = np.mean(mfccs, axis=1)
    features['mfcc_std'] = np.std(mfccs, axis=1)
    features['mfcc_delta_mean'] = np.mean(librosa.feature.delta(mfccs), axis=1)
    
    # 2. Spectral Centroid - "brightness" of sound
    spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    features['spectral_centroid_mean'] = np.mean(spectral_centroids)
    features['spectral_centroid_std'] = np.std(spectral_centroids)
    
    # 3. Spectral Bandwidth
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
    features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
    features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
    
    # 4. Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
    features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
    features['spectral_rolloff_std'] = np.std(spectral_rolloff)
    
    # 5. Spectral Flatness - measure of "noisiness"
    spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
    features['spectral_flatness_mean'] = np.mean(spectral_flatness)
    features['spectral_flatness_std'] = np.std(spectral_flatness)
    
    # 6. Zero-Crossing Rate - texture of sound
    zcr = librosa.feature.zero_crossing_rate(audio)[0]
    features['zcr_mean'] = np.mean(zcr)
    features['zcr_std'] = np.std(zcr)
    
    # 7. RMS Energy
    rms = librosa.feature.rms(y=audio)[0]
    features['rms_mean'] = np.mean(rms)
    features['rms_std'] = np.std(rms)
    
    # 8. Pitch/F0 Analysis - ⚡ Optimized hop_length for speed
    try:
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, 
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            hop_length=1024  # Increased from default 512 for 2x speedup
        )
        f0_valid = f0[~np.isnan(f0)]
        if len(f0_valid) > 0:
            features['pitch_mean'] = np.mean(f0_valid)
            features['pitch_std'] = np.std(f0_valid)
            features['pitch_range'] = np.max(f0_valid) - np.min(f0_valid)
            features['voiced_ratio'] = np.sum(~np.isnan(f0)) / len(f0)
        else:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
            features['pitch_range'] = 0
            features['voiced_ratio'] = 0
    except:
        features['pitch_mean'] = 0
        features['pitch_std'] = 0
        features['pitch_range'] = 0
        features['voiced_ratio'] = 0
    
    # 9. Tempo and rhythm features
    try:
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
        # Handle numpy array tempo (newer librosa versions)
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
        features['tempo'] = tempo
        features['beat_count'] = len(beats)
    except:
        features['tempo'] = 0
        features['beat_count'] = 0
    
    # 10. Harmonic-to-noise ratio approximation
    harmonic, percussive = librosa.effects.hpss(audio)
    features['harmonic_mean'] = np.mean(np.abs(harmonic))
    features['percussive_mean'] = np.mean(np.abs(percussive))
    if features['percussive_mean'] > 0:
        features['harmonic_ratio'] = features['harmonic_mean'] / (features['harmonic_mean'] + features['percussive_mean'])
    else:
        features['harmonic_ratio'] = 1.0
    
    # 11. Chroma features (pitch class)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    features['chroma_mean'] = np.mean(chroma, axis=1)
    features['chroma_std'] = np.std(chroma)
    
    # 12. Spectral Contrast
    contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    features['spectral_contrast_mean'] = np.mean(contrast, axis=1)
    
    return features


def features_to_vector(features: Dict[str, Any]) -> np.ndarray:
    """
    Convert feature dictionary to a flat numpy array for model input
    
    Args:
        features: Dictionary of extracted features
        
    Returns:
        Flattened feature vector
    """
    vector_parts = []
    
    # Add scalar features
    scalar_keys = [
        'spectral_centroid_mean', 'spectral_centroid_std',
        'spectral_bandwidth_mean', 'spectral_bandwidth_std',
        'spectral_rolloff_mean', 'spectral_rolloff_std',
        'spectral_flatness_mean', 'spectral_flatness_std',
        'zcr_mean', 'zcr_std',
        'rms_mean', 'rms_std',
        'pitch_mean', 'pitch_std', 'pitch_range', 'voiced_ratio',
        'tempo', 'beat_count',
        'harmonic_mean', 'percussive_mean', 'harmonic_ratio',
        'chroma_std'
    ]
    
    for key in scalar_keys:
        if key in features:
            vector_parts.append(float(features[key]))
        else:
            vector_parts.append(0.0)
    
    # Add array features
    array_keys = ['mfcc_mean', 'mfcc_std', 'mfcc_delta_mean', 'chroma_mean', 'spectral_contrast_mean']
    for key in array_keys:
        if key in features:
            vector_parts.extend(features[key].flatten().tolist())
    
    return np.array(vector_parts, dtype=np.float32)
