"""
Enhanced Voice Detection Model
Uses improved heuristics and additional features to detect AI-generated voices
"""
import numpy as np
from typing import Dict, Any, Tuple
import os

from app.utils.audio_processor import (
    decode_base64_audio,
    load_audio_from_bytes,
    extract_audio_features,
    features_to_vector
)


class EnhancedVoiceDetector:
    """
    Enhanced Voice Detector with improved detection of modern AI voices.
    
    Key improvements:
    - Tighter thresholds for modern TTS systems
    - Additional breath/pause analysis
    - Formant transition analysis
    - Speaking rate consistency check
    """
    
    def __init__(self):
        """Initialize the enhanced voice detector"""
        self.is_initialized = True
        
        # Adjusted weights for better AI detection
        self.feature_weights = {
            'pitch_consistency': 0.15,
            'spectral_flatness': 0.10,
            'harmonic_structure': 0.12,
            'mfcc_variance': 0.15,
            'prosodic_naturalness': 0.18, # Increased: catch natural energy/rhythm
            'spectral_dynamics': 0.06,
            'micro_variations': 0.12, # Increased: detect human 'jitter'
            'breath_patterns': 0.12  # Increased: natural pauses
        }
    
    def analyze_pitch_consistency(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Analyze pitch consistency with tighter thresholds for modern TTS
        """
        pitch_std = features.get('pitch_std', 0)
        pitch_range = features.get('pitch_range', 0)
        pitch_mean = features.get('pitch_mean', 0)
        voiced_ratio = features.get('voiced_ratio', 0)
        
        if pitch_mean > 0:
            pitch_cv = pitch_std / pitch_mean
        else:
            pitch_cv = 0
        
        ai_score = 0.5
        explanations = []
        
        # Modern AI voices often have pitch CV between 0.15-0.25 (mimicking natural)
        # But they lack the micro-fluctuations in pitch
        if pitch_cv < 0.08:
            ai_score = 0.90
            explanations.append("very stable pitch")
        elif pitch_cv < 0.15:
            ai_score = 0.75
            explanations.append("consistent pitch pattern")
        elif pitch_cv < 0.22:
            # If energy variation is high, this CV range is more likely human
            if features.get('rms_std', 0) / features.get('rms_mean', 1) > 0.6:
                ai_score = 0.45
                explanations.append("controlled but dynamic pitch")
            else:
                ai_score = 0.55
                explanations.append("clean pitch pattern")
        elif pitch_cv < 0.30:
            ai_score = 0.40
            explanations.append("moderate pitch variation")
        else:
            ai_score = 0.20
            explanations.append("high pitch variability")
        
        # Check voiced ratio - AI tends to have higher voiced ratio (less silence/breath)
        if voiced_ratio > 0.85:
            # If pitch range is high, it might be singing or very expressive human
            if pitch_range > 200:
                ai_score -= 0.15
                explanations.append("expressive vocal patterns")
            else:
                ai_score += 0.15
                explanations.append("high voiced ratio")
        elif voiced_ratio > 0.70:
            ai_score += 0.08
            explanations.append("moderate voiced ratio")
        elif voiced_ratio < 0.50:
            ai_score -= 0.10
            explanations.append("many natural pauses")
        
        # Check pitch range relative to mean
        if pitch_mean > 0:
            range_ratio = pitch_range / pitch_mean
            if range_ratio < 0.5:
                ai_score += 0.10
                explanations.append("limited pitch range")
            elif range_ratio > 1.0:
                ai_score -= 0.15
                explanations.append("dynamic pitch range")
        
        return np.clip(ai_score, 0, 1), "; ".join(explanations) if explanations else "Normal pitch"
    
    def analyze_spectral_characteristics(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Enhanced spectral analysis
        """
        flatness_mean = features.get('spectral_flatness_mean', 0)
        flatness_std = features.get('spectral_flatness_std', 0)
        bandwidth_std = features.get('spectral_bandwidth_std', 0)
        centroid_std = features.get('spectral_centroid_std', 0)
        rolloff_std = features.get('spectral_rolloff_std', 0)
        
        ai_score = 0.5
        explanations = []
        
        # AI voices often have very consistent spectral characteristics
        # Check for "too perfect" spectral consistency
        if flatness_std < 0.03:
            # If the voice has high harmonic ratio and range, it might be singing
            if features.get('harmonic_ratio', 0) > 0.7 and features.get('pitch_range', 0) > 80:
                ai_score += 0.15 # Reduced boost for melodic voices
                explanations.append("melodic spectral stability")
            else:
                ai_score += 0.25
                explanations.append("very uniform spectrum")
        elif flatness_std < 0.08:
            # If pitch range is very high, this stability might be human singing
            if features.get('pitch_range', 0) > 250:
                ai_score -= 0.10
                explanations.append("controlled vocal timbre")
            else:
                ai_score += 0.20
                explanations.append("consistent spectral pattern")
        elif flatness_std > 0.15:
            ai_score -= 0.10
            explanations.append("natural spectral variation")
        
        # Spectral centroid variation
        if centroid_std < 800:
            ai_score += 0.15
            explanations.append("stable spectral centroid")
        elif centroid_std > 1800:
            ai_score -= 0.15
            explanations.append("dynamic spectral content")
        
        # Combined spectral dynamics score
        spectral_dynamics = (bandwidth_std + centroid_std + rolloff_std) / 3
        if spectral_dynamics < 1000:
            # If bandwidth varies enough, it might be human
            if bandwidth_std > 500:
                ai_score -= 0.05
            else:
                ai_score += 0.10
                explanations.append("limited spectral dynamics")
        elif spectral_dynamics > 2500:
            ai_score -= 0.15
            explanations.append("rich spectral variety")
        
        return np.clip(ai_score, 0, 1), "; ".join(explanations) if explanations else "Normal spectrum"
    
    def analyze_harmonic_structure(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Enhanced harmonic analysis - AI voices often have cleaner harmonics
        """
        harmonic_ratio = features.get('harmonic_ratio', 0.5)
        pitch_range = features.get('pitch_range', 0)
        
        ai_score = 0.5
        explanations = []
        
        # AI voices tend to have cleaner harmonic structure
        if harmonic_ratio > 0.90:
            if pitch_range > 150:
                ai_score = 0.55 # Probably singing
                explanations.append("strong harmonic presence")
            else:
                ai_score = 0.85
                explanations.append("very clean harmonics")
        elif harmonic_ratio > 0.75:
            if pitch_range > 80: # Lowered threshold for singing
                ai_score = 0.45 
                explanations.append("melodic harmonic structure")
            else:
                ai_score = 0.65
                explanations.append("clean harmonic structure")
        elif harmonic_ratio > 0.55:
            ai_score = 0.50
            explanations.append("balanced harmonics")
        elif harmonic_ratio > 0.35:
            ai_score = 0.30
            explanations.append("natural harmonic-noise mix")
        else:
            ai_score = 0.25
            explanations.append("natural voice texture")
        
        return ai_score, "; ".join(explanations) if explanations else "Normal harmonics"
    
    def analyze_mfcc_patterns(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Enhanced MFCC analysis
        """
        mfcc_std = features.get('mfcc_std', np.zeros(20))
        mfcc_delta = features.get('mfcc_delta_mean', np.zeros(20))
        mfcc_mean = features.get('mfcc_mean', np.zeros(20))
        
        mfcc_variability = np.mean(mfcc_std)
        delta_activity = np.mean(np.abs(mfcc_delta))
        
        # Check variance across different MFCC coefficients
        mfcc_std_variation = np.std(mfcc_std)
        
        ai_score = 0.5
        explanations = []
        
        # AI voices often have more uniform MFCC patterns
        if mfcc_variability < 10:
            ai_score += 0.25
            explanations.append("low MFCC variability")
        elif mfcc_variability < 15:
            if features.get('pitch_range', 0) > 250:
                ai_score -= 0.10
                explanations.append("expressive MFCC dynamics")
            else:
                ai_score += 0.10
                explanations.append("moderate MFCC variation")
        elif mfcc_variability > 25:
            ai_score -= 0.15
            explanations.append("rich MFCC dynamics")
        
        # Delta (temporal) changes
        if delta_activity < 0.5:
            # Singing often has smooth transitions but high energy variation
            if features.get('rms_std', 0) / features.get('rms_mean', 1) > 0.6:
                ai_score += 0.05
                explanations.append("controlled transitions")
            else:
                ai_score += 0.20
                explanations.append("limited temporal changes")
        elif delta_activity < 1.0:
            ai_score += 0.10
            explanations.append("smooth transitions")
        elif delta_activity > 2.0:
            ai_score -= 0.15
            explanations.append("natural temporal dynamics")
        
        # Check if MFCC std is too uniform across coefficients
        if mfcc_std_variation < 3:
            ai_score += 0.10
            explanations.append("uniform coefficient variance")
        
        return np.clip(ai_score, 0, 1), "; ".join(explanations) if explanations else "Normal MFCC"
    
    def analyze_prosodic_features(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Enhanced prosodic analysis
        """
        rms_std = features.get('rms_std', 0)
        rms_mean = features.get('rms_mean', 0)
        zcr_std = features.get('zcr_std', 0)
        zcr_mean = features.get('zcr_mean', 0)
        
        ai_score = 0.5
        explanations = []
        
        # Energy coefficient of variation
        if rms_mean > 0:
            energy_cv = rms_std / rms_mean
            if energy_cv < 0.3:
                ai_score += 0.20
                explanations.append("stable energy levels")
            elif energy_cv < 0.5:
                ai_score += 0.10
                explanations.append("moderate energy variation")
            elif energy_cv > 0.8:
                ai_score -= 0.15
                explanations.append("dynamic energy")
        
        # Zero-crossing rate variation (articulation)
        if zcr_mean > 0:
            zcr_cv = zcr_std / zcr_mean
            if zcr_cv < 0.3:
                ai_score += 0.15
                explanations.append("consistent articulation")
            elif zcr_cv > 0.8:
                ai_score -= 0.10
                explanations.append("varied articulation")
        
        return np.clip(ai_score, 0, 1), "; ".join(explanations) if explanations else "Normal prosody"
    
    def analyze_micro_variations(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Analyze micro-level variations - key differentiator for modern TTS
        """
        spectral_centroid_std = features.get('spectral_centroid_std', 0)
        spectral_rolloff_std = features.get('spectral_rolloff_std', 0)
        spectral_bandwidth_std = features.get('spectral_bandwidth_std', 0)
        
        # Combined micro-variation score
        micro_var_score = (spectral_centroid_std + spectral_rolloff_std + spectral_bandwidth_std) / 3
        
        ai_score = 0.5
        explanations = []
        
        if micro_var_score < 600:
            ai_score = 0.85
            explanations.append("lacks micro-variations")
        elif micro_var_score < 1200:
            ai_score = 0.65
            explanations.append("limited micro-variations")
        elif micro_var_score < 1800:
            ai_score = 0.50
            explanations.append("moderate variations")
        elif micro_var_score < 2500:
            ai_score = 0.35
            explanations.append("good micro-variations")
        else:
            ai_score = 0.20
            explanations.append("rich natural variations")
        
        return ai_score, "; ".join(explanations) if explanations else "Normal variations"
    
    def analyze_breath_patterns(self, features: Dict[str, Any]) -> Tuple[float, str]:
        """
        Analyze breath and pause patterns - AI often lacks natural breathing
        """
        rms_mean = features.get('rms_mean', 0)
        rms_std = features.get('rms_std', 0)
        voiced_ratio = features.get('voiced_ratio', 0)
        
        ai_score = 0.5
        explanations = []
        
        # AI voices often have less silence/breath pauses
        if voiced_ratio > 0.80:
            # High voiced ratio is common in singing/human speech if pitch varies widely
            if features.get('pitch_range', 0) > 200:
                ai_score -= 0.15
                explanations.append("natural vocal flow")
            else:
                ai_score += 0.25
                explanations.append("minimal pauses")
        elif voiced_ratio > 0.65:
            ai_score += 0.15
            explanations.append("few pauses")
        elif voiced_ratio < 0.50:
            ai_score -= 0.15
            explanations.append("natural breathing pauses")
        
        # Check for abrupt energy transitions (natural = gradual)
        if rms_mean > 0:
            transition_ratio = rms_std / rms_mean
            if transition_ratio < 0.4:
                ai_score += 0.15
                explanations.append("smooth energy transitions")
            elif transition_ratio > 0.7:
                ai_score -= 0.10
                explanations.append("natural energy dynamics")
        
        return np.clip(ai_score, 0, 1), "; ".join(explanations) if explanations else "Normal breathing"
    
    def predict(self, audio_base64: str, audio_format: str = "mp3", language: str = None) -> Dict[str, Any]:
        """
        Predict whether the voice is AI-generated or human
        """
        try:
            # Decode and load audio
            audio_bytes = decode_base64_audio(audio_base64)
            audio, sr = load_audio_from_bytes(audio_bytes, audio_format)
            
            # Extract features
            features = extract_audio_features(audio, sr)
            
            # Analyze different aspects
            pitch_score, pitch_exp = self.analyze_pitch_consistency(features)
            spectral_score, spectral_exp = self.analyze_spectral_characteristics(features)
            harmonic_score, harmonic_exp = self.analyze_harmonic_structure(features)
            mfcc_score, mfcc_exp = self.analyze_mfcc_patterns(features)
            prosodic_score, prosodic_exp = self.analyze_prosodic_features(features)
            micro_score, micro_exp = self.analyze_micro_variations(features)
            breath_score, breath_exp = self.analyze_breath_patterns(features)
            
            # Weighted combination
            weights = self.feature_weights
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
            
            ai_probability = np.clip(ai_probability, 0, 1)
            
            # Determine classification
            if ai_probability >= 0.50:
                classification = "AI_GENERATED"
                confidence = ai_probability
            else:
                classification = "HUMAN"
                confidence = 1 - ai_probability
            
            # Generate explanation
            all_scores = [
                (pitch_score, pitch_exp, "Pitch"),
                (spectral_score, spectral_exp, "Spectral"),
                (harmonic_score, harmonic_exp, "Harmonic"),
                (mfcc_score, mfcc_exp, "MFCC"),
                (prosodic_score, prosodic_exp, "Prosodic"),
                (micro_score, micro_exp, "Micro-variations"),
                (breath_score, breath_exp, "Breath patterns")
            ]
            
            # Get top contributing factors
            all_scores.sort(key=lambda x: abs(x[0] - 0.5), reverse=True)
            
            if classification == "AI_GENERATED":
                top_factors = [f"{name}: {exp}" for score, exp, name in all_scores if score > 0.5][:2]
            else:
                top_factors = [f"{name}: {exp}" for score, exp, name in all_scores if score < 0.5][:2]
            
            explanation = "; ".join(top_factors) if top_factors else "Analysis inconclusive"
            
            return {
                "classification": classification,
                "confidence_score": round(float(confidence), 2),
                "explanation": explanation,
                "language": language,
                "analysis_details": {
                    "pitch_analysis": {"score": round(pitch_score, 2), "detail": pitch_exp},
                    "spectral_analysis": {"score": round(spectral_score, 2), "detail": spectral_exp},
                    "harmonic_analysis": {"score": round(harmonic_score, 2), "detail": harmonic_exp},
                    "mfcc_analysis": {"score": round(mfcc_score, 2), "detail": mfcc_exp},
                    "prosodic_analysis": {"score": round(prosodic_score, 2), "detail": prosodic_exp},
                    "micro_variation_analysis": {"score": round(micro_score, 2), "detail": micro_exp},
                    "breath_analysis": {"score": round(breath_score, 2), "detail": breath_exp}
                }
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error analyzing audio: {str(e)}")


# Replace the default detector with enhanced version
voice_detector = EnhancedVoiceDetector()


def detect_voice(audio_base64: str, audio_format: str = "mp3", language: str = None) -> Dict[str, Any]:
    """
    Convenience function to detect if voice is AI-generated
    """
    return voice_detector.predict(audio_base64, audio_format, language)
