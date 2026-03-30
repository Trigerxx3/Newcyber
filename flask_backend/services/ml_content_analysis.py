"""
Enhanced Content Analysis Service with ML Integration
Combines keyword-based analysis with ML classification and risk scoring
"""
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from services.content_analysis import analyze_content, AnalysisResult
from ml_models.content_classifier import ContentClassifier
from ml_models.risk_scoring import RiskScoringEngine

logger = logging.getLogger(__name__)

@dataclass
class EnhancedAnalysisResult:
    """Enhanced analysis result with ML predictions"""
    # Original analysis results
    matched_keywords: list
    suspicion_score: int
    intent: str
    is_flagged: bool
    confidence: float
    analysis_data: dict
    processing_time: float
    
    # ML-based results
    ml_prediction: str  # "Drug-Related" | "Non-Drug-Related"
    ml_confidence: float  # 0-1
    risk_score: int  # 0-100
    risk_level: str  # "High" | "Medium" | "Low"

class EnhancedContentAnalysisService:
    """Enhanced content analysis service with ML integration"""
    
    def __init__(self):
        """Initialize the enhanced analysis service"""
        self.content_classifier = ContentClassifier()
        self.risk_scoring_engine = RiskScoringEngine()
        logger.info("Enhanced Content Analysis Service initialized")
    
    def analyze(self, 
                text: str,
                platform: str = "Unknown",
                username: str = "Unknown",
                post_frequency: float = 0.0) -> EnhancedAnalysisResult:
        """
        Perform enhanced content analysis with ML integration
        
        Args:
            text: Content text to analyze
            platform: Platform name (Telegram, Instagram, WhatsApp, etc.)
            username: Username of the content author
            post_frequency: Post frequency (posts per day, default: 0.0)
            
        Returns:
            EnhancedAnalysisResult with both keyword-based and ML-based analysis
        """
        start_time = datetime.now()
        
        # Step 1: Perform keyword-based analysis (existing pipeline)
        try:
            keyword_result = analyze_content(text)
        except Exception as e:
            logger.error(f"Keyword analysis failed: {str(e)}")
            # Create fallback result
            keyword_result = AnalysisResult(
                matched_keywords=[],
                suspicion_score=0,
                intent="Unknown",
                is_flagged=False,
                confidence=0.0,
                analysis_data={},
                processing_time=0.0
            )
        
        # Step 2: Perform ML-based classification
        ml_prediction_result = {
            "prediction": "Non-Drug-Related",
            "confidence": 0.5,
            "label": 0
        }
        
        try:
            ml_prediction_result = self.content_classifier.predict(text)
        except Exception as e:
            logger.warning(f"ML classification failed, using fallback: {str(e)}")
        
        # Step 3: Calculate ML-based risk score
        risk_result = {
            "risk_score": 0,
            "risk_level": "Low"
        }
        
        try:
            risk_result = self.risk_scoring_engine.calculate_risk_score(
                text=text,
                keyword_count=len(keyword_result.matched_keywords),
                ml_confidence=ml_prediction_result["confidence"],
                post_frequency=post_frequency,
                platform=platform
            )
        except Exception as e:
            logger.warning(f"Risk scoring failed, using fallback: {str(e)}")
            # Use fallback risk calculation
            risk_result = self._calculate_fallback_risk(
                keyword_count=len(keyword_result.matched_keywords),
                ml_confidence=ml_prediction_result["confidence"],
                platform=platform
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Combine results
        return EnhancedAnalysisResult(
            matched_keywords=keyword_result.matched_keywords,
            suspicion_score=keyword_result.suspicion_score,
            intent=keyword_result.intent,
            is_flagged=keyword_result.is_flagged,
            confidence=keyword_result.confidence,
            analysis_data=keyword_result.analysis_data,
            processing_time=processing_time,
            ml_prediction=ml_prediction_result["prediction"],
            ml_confidence=ml_prediction_result["confidence"],
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"]
        )
    
    def _calculate_fallback_risk(self, keyword_count: int, ml_confidence: float, platform: str) -> Dict:
        """Fallback risk calculation when ML model fails"""
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

# Global instance
enhanced_analyzer = EnhancedContentAnalysisService()

def analyze_content_enhanced(text: str, 
                            platform: str = "Unknown",
                            username: str = "Unknown",
                            post_frequency: float = 0.0) -> EnhancedAnalysisResult:
    """
    Analyze content with ML enhancement
    
    Args:
        text: Content text to analyze
        platform: Platform name
        username: Username
        post_frequency: Post frequency
        
    Returns:
        EnhancedAnalysisResult with ML predictions
    """
    return enhanced_analyzer.analyze(text, platform, username, post_frequency)
