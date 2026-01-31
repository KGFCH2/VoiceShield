"""
Debug script to show detailed analysis of voice detection
"""
import sys
import base64
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.audio_processor import (
    decode_base64_audio,
    load_audio_from_bytes,
    extract_audio_features
)
from app.models.voice_detector import EnhancedVoiceDetector


def debug_analyze(audio_file: str, language: str = "English"):
    """Analyze an audio file with detailed debug output"""
    
    print(f"\n{'='*60}")
    print(f"DEBUG ANALYSIS: {audio_file}")
    print(f"{'='*60}\n")
    
    # Read and encode audio
    with open(audio_file, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    
    # Decode and load
    audio_bytes = decode_base64_audio(audio_base64)
    audio, sr = load_audio_from_bytes(audio_bytes, "mp3")
    
    print(f"Audio duration: {len(audio)/sr:.2f} seconds")
    print(f"Sample rate: {sr} Hz")
    
    # Extract features
    features = extract_audio_features(audio, sr)
    
    print(f"\n{'='*60}")
    print("EXTRACTED FEATURES:")
    print(f"{'='*60}")
    
    # Print key features
    print(f"\n📊 Pitch Features:")
    print(f"   - Pitch Mean: {features.get('pitch_mean', 0):.2f} Hz")
    print(f"   - Pitch Std: {features.get('pitch_std', 0):.2f}")
    print(f"   - Pitch Range: {features.get('pitch_range', 0):.2f}")
    print(f"   - Voiced Ratio: {features.get('voiced_ratio', 0):.2%}")
    
    # Calculate pitch CV
    pitch_mean = features.get('pitch_mean', 0)
    pitch_std = features.get('pitch_std', 0)
    pitch_cv = pitch_std / pitch_mean if pitch_mean > 0 else 0
    print(f"   - Pitch CV (coefficient of variation): {pitch_cv:.4f}")
    
    print(f"\n🎵 Spectral Features:")
    print(f"   - Spectral Flatness Mean: {features.get('spectral_flatness_mean', 0):.4f}")
    print(f"   - Spectral Flatness Std: {features.get('spectral_flatness_std', 0):.4f}")
    print(f"   - Spectral Bandwidth Std: {features.get('spectral_bandwidth_std', 0):.2f}")
    print(f"   - Spectral Centroid Std: {features.get('spectral_centroid_std', 0):.2f}")
    print(f"   - Spectral Rolloff Std: {features.get('spectral_rolloff_std', 0):.2f}")
    
    print(f"\n🎼 Harmonic Features:")
    print(f"   - Harmonic Ratio: {features.get('harmonic_ratio', 0):.4f}")
    print(f"   - Harmonic Mean: {features.get('harmonic_mean', 0):.6f}")
    
    print(f"\n📈 Energy Features:")
    print(f"   - RMS Mean: {features.get('rms_mean', 0):.6f}")
    print(f"   - RMS Std: {features.get('rms_std', 0):.6f}")
    print(f"   - ZCR Mean: {features.get('zcr_mean', 0):.4f}")
    print(f"   - ZCR Std: {features.get('zcr_std', 0):.4f}")
    
    # Now run through detector
    detector = EnhancedVoiceDetector()
    
    print(f"\n{'='*60}")
    print("ANALYSIS SCORES (Higher = More likely AI):")
    print(f"{'='*60}")
    
    pitch_score, pitch_exp = detector.analyze_pitch_consistency(features)
    spectral_score, spectral_exp = detector.analyze_spectral_characteristics(features)
    harmonic_score, harmonic_exp = detector.analyze_harmonic_structure(features)
    mfcc_score, mfcc_exp = detector.analyze_mfcc_patterns(features)
    prosodic_score, prosodic_exp = detector.analyze_prosodic_features(features)
    micro_score, micro_exp = detector.analyze_micro_variations(features)
    breath_score, breath_exp = detector.analyze_breath_patterns(features)
    
    print(f"\n1. Pitch Consistency:    {pitch_score:.2f} - {pitch_exp}")
    print(f"2. Spectral Analysis:    {spectral_score:.2f} - {spectral_exp}")
    print(f"3. Harmonic Structure:   {harmonic_score:.2f} - {harmonic_exp}")
    print(f"4. MFCC Patterns:        {mfcc_score:.2f} - {mfcc_exp}")
    print(f"5. Prosodic Features:    {prosodic_score:.2f} - {prosodic_exp}")
    print(f"6. Micro Variations:     {micro_score:.2f} - {micro_exp}")
    print(f"7. Breath Patterns:      {breath_score:.2f} - {breath_exp}")
    
    # Calculate weighted score
    weights = detector.feature_weights
    ai_probability = (
        weights['pitch_consistency'] * pitch_score +
        weights['spectral_flatness'] * spectral_score +
        weights['harmonic_structure'] * harmonic_score +
        weights['mfcc_variance'] * mfcc_score +
        weights['prosodic_naturalness'] * prosodic_score +
        weights['spectral_dynamics'] * spectral_score +
        weights['micro_variations'] * micro_score +
        weights['breath_patterns'] * breath_score
    )
    
    print(f"\n{'='*60}")
    print("FINAL RESULT:")
    print(f"{'='*60}")
    print(f"\n🎯 AI Probability Score: {ai_probability:.4f}")
    print(f"   (Threshold for AI_GENERATED: >= 0.50)")
    
    if ai_probability >= 0.5:
        print(f"\n✅ Classification: AI_GENERATED")
        print(f"   Confidence: {ai_probability:.2%}")
    else:
        print(f"\n✅ Classification: HUMAN")
        print(f"   Confidence: {1-ai_probability:.2%}")
    
    print(f"\n{'='*60}")
    print("INTERPRETATION:")
    print(f"{'='*60}")
    print("""
Scores closer to 1.0 = More AI-like characteristics
Scores closer to 0.0 = More Human-like characteristics

Key indicators for AI-generated voice:
- Very consistent pitch (low variation)
- Uniform spectral distribution
- Clean harmonic structure (too perfect)
- Low MFCC variability
- Monotonous energy levels
- Lack of micro-variations
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug voice analysis")
    parser.add_argument("--audio", required=True, help="Path to MP3 file")
    parser.add_argument("--language", default="English", help="Language")
    
    args = parser.parse_args()
    
    if not Path(args.audio).exists():
        print(f"Error: File not found: {args.audio}")
        sys.exit(1)
    
    debug_analyze(args.audio, args.language)
