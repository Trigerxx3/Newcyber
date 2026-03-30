"""
ML-based Risk Scoring Engine
Uses RandomForestRegressor or GradientBoostingRegressor to calculate risk scores (0-100)
"""
import os
import joblib
import logging
from typing import Dict, Optional, List
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import re

logger = logging.getLogger(__name__)

class RiskScoringEngine:
    """
    ML-based risk scoring engine for content analysis
    
    Risk Score Range: 0-100
    Risk Levels:
        - 0-40: Low
        - 41-70: Medium
        - 71-100: High
    """
    
    def __init__(self, model_dir: Optional[str] = None, use_gradient_boosting: bool = False):
        """
        Initialize the risk scoring engine
        
        Args:
            model_dir: Directory to load/save model artifacts (default: flask_backend/ml_models/)
            use_gradient_boosting: If True, use GradientBoostingRegressor; else use RandomForestRegressor
        """
        if model_dir is None:
            base_dir = Path(__file__).parent
            model_dir = str(base_dir)
        
        self.model_dir = model_dir
        self.use_gradient_boosting = use_gradient_boosting
        model_name = 'risk_scoring_gb.pkl' if use_gradient_boosting else 'risk_scoring_rf.pkl'
        self.model_path = os.path.join(model_dir, model_name)
        self.label_encoder_path = os.path.join(model_dir, 'platform_encoder.pkl')
        
        self.model: Optional[RandomForestRegressor | GradientBoostingRegressor] = None
        self.platform_encoder: Optional[LabelEncoder] = None
        self.is_loaded = False
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model and encoder from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.label_encoder_path):
                self.model = joblib.load(self.model_path)
                self.platform_encoder = joblib.load(self.label_encoder_path)
                self.is_loaded = True
                logger.info(f"Loaded risk scoring engine from {self.model_dir}")
            else:
                logger.warning(f"Model files not found. Train the model first.")
                self.is_loaded = False
        except Exception as e:
            logger.error(f"Failed to load risk scoring engine: {str(e)}")
            self.is_loaded = False
    
    def _extract_features(self, 
                         text: str,
                         keyword_count: int,
                         ml_confidence: float,
                         post_frequency: float = 0.0,
                         platform: str = "Unknown") -> np.ndarray:
        """
        Extract features for risk scoring
        
        Args:
            text: Content text
            keyword_count: Number of matched keywords
            ml_confidence: ML prediction confidence (0-1)
            post_frequency: Post frequency (posts per day, default: 0.0)
            platform: Platform name (Telegram, Instagram, WhatsApp, etc.)
            
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # 1. Keyword count (normalized)
        features.append(min(keyword_count / 10.0, 1.0))  # Cap at 1.0
        
        # 2. ML confidence
        features.append(float(ml_confidence))
        
        # 3. Post frequency (normalized, assuming max 10 posts/day)
        features.append(min(post_frequency / 10.0, 1.0))
        
        # 4. Platform encoding (numeric)
        if self.platform_encoder:
            try:
                platform_encoded = self.platform_encoder.transform([platform])[0]
            except (ValueError, AttributeError):
                # Unknown platform, use default
                platform_encoded = 0
        else:
            # Default encoding if encoder not loaded
            platform_map = {
                "Telegram": 3,
                "Instagram": 2,
                "WhatsApp": 4,
                "Facebook": 1,
                "Twitter": 1,
                "TikTok": 1,
                "Unknown": 0
            }
            platform_encoded = platform_map.get(platform, 0)
        
        # Normalize platform encoding (assuming max 4)
        features.append(platform_encoded / 4.0)
        
        # 5. Text length (normalized, assuming max 1000 chars)
        text_length = len(text) if text else 0
        features.append(min(text_length / 1000.0, 1.0))
        
        # 6. Number of suspicious words/phrases
        suspicious_patterns = [
            r'\b(dm|pm|message|contact)\b',
            r'\b(price|cost|cheap|affordable)\b',
            r'\b(delivery|ship|send)\b',
            r'\b(quality|pure|tested)\b',
            r'\b(available|in stock|ready)\b'
        ]
        suspicious_count = sum(1 for pattern in suspicious_patterns if re.search(pattern, text.lower()))
        features.append(min(suspicious_count / 5.0, 1.0))
        
        # 7. Presence of emojis (drug-related indicators)
        drug_emojis = ['💊', '💉', '🌿', '🍃', '💰', '💵', '💸']
        emoji_count = sum(1 for emoji in drug_emojis if emoji in text)
        features.append(min(emoji_count / 3.0, 1.0))
        
        return np.array(features).reshape(1, -1)
    
    def calculate_risk_score(self,
                            text: str,
                            keyword_count: int,
                            ml_confidence: float,
                            post_frequency: float = 0.0,
                            platform: str = "Unknown") -> Dict[str, any]:
        """
        Calculate risk score for content
        
        Args:
            text: Content text
            keyword_count: Number of matched keywords
            ml_confidence: ML prediction confidence (0-1)
            post_frequency: Post frequency (posts per day, default: 0.0)
            platform: Platform name
            
        Returns:
            Dictionary with risk score and level:
            {
                "risk_score": int (0-100),
                "risk_level": "High" | "Medium" | "Low"
            }
        """
        if not self.is_loaded or self.model is None:
            # Fallback: calculate basic risk score
            logger.warning("Model not loaded. Using fallback risk calculation.")
            return self._calculate_fallback_risk(keyword_count, ml_confidence, platform)
        
        try:
            # Extract features
            features = self._extract_features(
                text=text,
                keyword_count=keyword_count,
                ml_confidence=ml_confidence,
                post_frequency=post_frequency,
                platform=platform
            )
            
            # Predict risk score
            risk_score = self.model.predict(features)[0]
            
            # Clamp to 0-100 range
            risk_score = max(0, min(100, int(round(risk_score))))
            
            # Determine risk level
            if risk_score >= 71:
                risk_level = "High"
            elif risk_score >= 41:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                "risk_score": risk_score,
                "risk_level": risk_level
            }
            
        except Exception as e:
            logger.error(f"Error during risk scoring: {str(e)}")
            return self._calculate_fallback_risk(keyword_count, ml_confidence, platform)
    
    def _calculate_fallback_risk(self, keyword_count: int, ml_confidence: float, platform: str) -> Dict[str, any]:
        """
        Fallback risk calculation when ML model is not available
        
        Args:
            keyword_count: Number of matched keywords
            ml_confidence: ML prediction confidence
            platform: Platform name
            
        Returns:
            Dictionary with risk score and level
        """
        # Base score from keyword count
        keyword_score = min(keyword_count * 15, 60)
        
        # Add ML confidence contribution
        ml_score = ml_confidence * 30
        
        # Platform risk multiplier
        platform_risk = {
            "Telegram": 1.2,
            "WhatsApp": 1.1,
            "Instagram": 1.0,
            "Facebook": 0.9,
            "Twitter": 0.9,
            "TikTok": 0.9,
            "Unknown": 1.0
        }
        multiplier = platform_risk.get(platform, 1.0)
        
        # Calculate final score
        risk_score = int(round((keyword_score + ml_score) * multiplier))
        risk_score = max(0, min(100, risk_score))
        
        # Determine risk level
        if risk_score >= 71:
            risk_level = "High"
        elif risk_score >= 41:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level
        }
    
    def train(self,
             texts: List[str],
             keyword_counts: List[int],
             ml_confidences: List[float],
             post_frequencies: List[float],
             platforms: List[str],
             risk_scores: List[int],
             test_size: float = 0.2,
             random_state: int = 42):
        """
        Train the risk scoring model
        
        Args:
            texts: List of text samples
            keyword_counts: List of keyword counts
            ml_confidences: List of ML confidences
            post_frequencies: List of post frequencies
            platforms: List of platform names
            risk_scores: List of target risk scores (0-100)
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
        """
        try:
            # Encode platforms
            self.platform_encoder = LabelEncoder()
            platforms_encoded = self.platform_encoder.fit_transform(platforms)
            
            # Extract features for all samples
            features_list = []
            for i in range(len(texts)):
                features = self._extract_features(
                    text=texts[i],
                    keyword_count=keyword_counts[i],
                    ml_confidence=ml_confidences[i],
                    post_frequency=post_frequencies[i],
                    platform=platforms[i]
                )
                features_list.append(features[0])
            
            X = np.array(features_list)
            y = np.array(risk_scores)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Create and train model
            if self.use_gradient_boosting:
                self.model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=random_state
                )
            else:
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=random_state,
                    n_jobs=-1
                )
            
            logger.info(f"Training risk scoring model on {len(X_train)} samples...")
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            logger.info(f"Training R² score: {train_score:.4f}")
            logger.info(f"Test R² score: {test_score:.4f}")
            
            # Save model
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.platform_encoder, self.label_encoder_path)
            
            self.is_loaded = True
            logger.info(f"Model saved to {self.model_dir}")
            
            return {
                "train_r2": train_score,
                "test_r2": test_score,
                "model_path": self.model_path
            }
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
