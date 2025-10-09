"""
Content Analysis Service using spaCy NLP
Analyzes social media content for drug-related keywords and intent detection
"""
import json
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import spacy
    from spacy.matcher import Matcher
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    Matcher = None
    Doc = None
    SPACY_AVAILABLE = False
    print("⚠️  spaCy not available. Using basic keyword matching only.")

@dataclass
class AnalysisResult:
    """Result of content analysis"""
    matched_keywords: List[str]
    suspicion_score: int
    intent: str
    is_flagged: bool
    confidence: float
    analysis_data: Dict
    processing_time: float

class ContentAnalysisService:
    """Service for analyzing social media content using NLP"""
    
    def __init__(self):
        self.drug_data = self._load_drug_data()
        self.nlp = None
        self.matcher = None
        self._initialize_spacy()
    
    def _load_drug_data(self) -> Dict:
        """Load drug keywords and slang from JSON file"""
        try:
            with open(os.path.join(os.path.dirname(__file__), '..', 'drugs.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: drugs.json not found, using empty drug data")
            return {"drugs": {}, "intent_keywords": {}, "payment_keywords": [], "location_keywords": [], "urgency_keywords": []}
    
    def _initialize_spacy(self):
        """Initialize spaCy model and matcher"""
        if not SPACY_AVAILABLE:
            print("ℹ️  spaCy not available. Using enhanced keyword matching.")
            return
        
        try:
            # Try to load the English model
            self.nlp = spacy.load("en_core_web_sm")
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_patterns()
        except OSError:
            print("Warning: spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            # Fallback to basic model
            try:
                self.nlp = spacy.blank("en")
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_patterns()
            except Exception as e:
                print(f"Error initializing spaCy: {e}")
                self.nlp = None
                self.matcher = None
    
    def _setup_patterns(self):
        """Setup spaCy patterns for drug detection"""
        if not self.matcher or not self.nlp:
            return
        
        # Pattern for drug names (case insensitive)
        drug_patterns = []
        for drug_category, drug_info in self.drug_data.get("drugs", {}).items():
            keywords = drug_info.get("keywords", []) + drug_info.get("slang", [])
            for keyword in keywords:
                # Create pattern for exact match (case insensitive)
                pattern = [{"LOWER": keyword.lower()}]
                drug_patterns.append(pattern)
        
        # Add patterns to matcher
        self.matcher.add("DRUG_KEYWORDS", drug_patterns)
        
        # Pattern for selling intent
        selling_patterns = []
        for keyword in self.drug_data.get("intent_keywords", {}).get("selling", []):
            pattern = [{"LOWER": keyword.lower()}]
            selling_patterns.append(pattern)
        self.matcher.add("SELLING_INTENT", selling_patterns)
        
        # Pattern for buying intent
        buying_patterns = []
        for keyword in self.drug_data.get("intent_keywords", {}).get("buying", []):
            pattern = [{"LOWER": keyword.lower()}]
            buying_patterns.append(pattern)
        self.matcher.add("BUYING_INTENT", buying_patterns)
        
        # Pattern for payment keywords
        payment_patterns = []
        for keyword in self.drug_data.get("payment_keywords", []):
            pattern = [{"LOWER": keyword.lower()}]
            payment_patterns.append(pattern)
        self.matcher.add("PAYMENT_KEYWORDS", payment_patterns)
        
        # Pattern for location keywords
        location_patterns = []
        for keyword in self.drug_data.get("location_keywords", []):
            pattern = [{"LOWER": keyword.lower()}]
            location_patterns.append(pattern)
        self.matcher.add("LOCATION_KEYWORDS", location_patterns)
    
    def analyze_text(self, text: str) -> AnalysisResult:
        """
        Analyze text content for drug-related keywords and intent
        
        Args:
            text: Text content to analyze
            
        Returns:
            AnalysisResult with matched keywords, suspicion score, intent, and flagged status
        """
        start_time = datetime.now()
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Initialize result variables
        matched_keywords = []
        suspicion_score = 0
        intent = "Unknown"
        confidence = 0.0
        analysis_data = {}
        
        if SPACY_AVAILABLE and self.nlp and self.matcher:
            # Use spaCy for advanced analysis
            result = self._analyze_with_spacy(cleaned_text)
        else:
            # Use enhanced keyword matching (no spaCy needed)
            result = self._analyze_enhanced(cleaned_text)
        
        matched_keywords = result["matched_keywords"]
        suspicion_score = result["suspicion_score"]
        intent = result["intent"]
        confidence = result["confidence"]
        analysis_data = result["analysis_data"]
        
        # Determine if content should be flagged (threshold: 50)
        is_flagged = suspicion_score >= 50
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResult(
            matched_keywords=matched_keywords,
            suspicion_score=suspicion_score,
            intent=intent,
            is_flagged=is_flagged,
            confidence=confidence,
            analysis_data=analysis_data,
            processing_time=processing_time
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'[\+]?[1-9]?[0-9]{7,15}', '', text)
        
        # Normalize common drug-related emojis and symbols
        emoji_map = {
            '💊': 'pills',
            '🍃': 'weed',
            '🌿': 'herb',
            '🔥': 'fire',
            '💨': 'smoke',
            '💰': 'money',
            '💵': 'cash',
            '📍': 'location',
            '🚚': 'delivery',
            '📱': 'message',
            '💬': 'dm'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        return text
    
    def _analyze_with_spacy(self, text: str) -> Dict:
        """Analyze text using spaCy NLP"""
        doc = self.nlp(text)
        
        # Find matches using matcher
        matches = self.matcher(doc)
        
        matched_keywords = []
        drug_matches = []
        selling_indicators = []
        buying_indicators = []
        payment_indicators = []
        location_indicators = []
        
        # Process matches
        for match_id, start, end in matches:
            span = doc[start:end]
            matched_text = span.text.lower()
            
            # Categorize matches
            if match_id == self.matcher.vocab.strings["DRUG_KEYWORDS"]:
                drug_matches.append(matched_text)
                matched_keywords.append(matched_text)
            elif match_id == self.matcher.vocab.strings["SELLING_INTENT"]:
                selling_indicators.append(matched_text)
            elif match_id == self.matcher.vocab.strings["BUYING_INTENT"]:
                buying_indicators.append(matched_text)
            elif match_id == self.matcher.vocab.strings["PAYMENT_KEYWORDS"]:
                payment_indicators.append(matched_text)
            elif match_id == self.matcher.vocab.strings["LOCATION_KEYWORDS"]:
                location_indicators.append(matched_text)
        
        # Calculate suspicion score
        suspicion_score = self._calculate_suspicion_score(
            drug_matches, selling_indicators, buying_indicators, 
            payment_indicators, location_indicators, text
        )
        
        # Determine intent
        intent = self._determine_intent(selling_indicators, buying_indicators, payment_indicators)
        
        # Calculate confidence
        confidence = self._calculate_confidence(drug_matches, selling_indicators, buying_indicators)
        
        # Named Entity Recognition
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Dependency analysis for intent detection
        intent_verbs = self._extract_intent_verbs(doc)
        
        analysis_data = {
            "drug_matches": drug_matches,
            "selling_indicators": selling_indicators,
            "buying_indicators": buying_indicators,
            "payment_indicators": payment_indicators,
            "location_indicators": location_indicators,
            "entities": entities,
            "intent_verbs": intent_verbs,
            "sentiment": self._analyze_sentiment(doc),
            "word_count": len(doc),
            "sentence_count": len(list(doc.sents))
        }
        
        return {
            "matched_keywords": matched_keywords,
            "suspicion_score": suspicion_score,
            "intent": intent,
            "confidence": confidence,
            "analysis_data": analysis_data
        }
    
    def _analyze_enhanced(self, text: str) -> Dict:
        """Enhanced analysis using advanced keyword matching (no spaCy required)"""
        text_lower = text.lower()
        
        matched_keywords = []
        drug_matches = []
        selling_indicators = []
        buying_indicators = []
        payment_indicators = []
        location_indicators = []
        
        # Check for drug keywords (whole word matching to avoid false positives)
        import re
        for drug_category, drug_info in self.drug_data.get("drugs", {}).items():
            keywords = drug_info.get("keywords", []) + drug_info.get("slang", [])
            for keyword in keywords:
                # Use word boundary regex to avoid partial matches
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    drug_matches.append(keyword.lower())
                    matched_keywords.append(keyword.lower())
        
        # Check for intent keywords
        for keyword in self.drug_data.get("intent_keywords", {}).get("selling", []):
            if keyword.lower() in text_lower:
                selling_indicators.append(keyword.lower())
        
        for keyword in self.drug_data.get("intent_keywords", {}).get("buying", []):
            if keyword.lower() in text_lower:
                buying_indicators.append(keyword.lower())
        
        # Check for payment keywords
        for keyword in self.drug_data.get("payment_keywords", []):
            if keyword.lower() in text_lower:
                payment_indicators.append(keyword.lower())
        
        # Check for location keywords
        for keyword in self.drug_data.get("location_keywords", []):
            if keyword.lower() in text_lower:
                location_indicators.append(keyword.lower())
        
        # Calculate suspicion score
        suspicion_score = self._calculate_suspicion_score(
            drug_matches, selling_indicators, buying_indicators,
            payment_indicators, location_indicators, text
        )
        
        # Determine intent
        intent = self._determine_intent(selling_indicators, buying_indicators, payment_indicators)
        
        # Calculate confidence
        confidence = self._calculate_confidence(drug_matches, selling_indicators, buying_indicators)
        
        analysis_data = {
            "drug_matches": drug_matches,
            "selling_indicators": selling_indicators,
            "buying_indicators": buying_indicators,
            "payment_indicators": payment_indicators,
            "location_indicators": location_indicators,
            "entities": [],
            "intent_verbs": [],
            "sentiment": "neutral",
            "word_count": len(text.split()),
            "sentence_count": len(text.split('.'))
        }
        
        return {
            "matched_keywords": matched_keywords,
            "suspicion_score": suspicion_score,
            "intent": intent,
            "confidence": confidence,
            "analysis_data": analysis_data
        }
    
    def _calculate_suspicion_score(self, drug_matches: List[str], selling_indicators: List[str],
                                 buying_indicators: List[str], payment_indicators: List[str],
                                 location_indicators: List[str], text: str) -> int:
        """Calculate suspicion score based on various factors"""
        score = 0
        
        # Base score from drug keywords
        for drug_match in drug_matches:
            # Find drug category and severity
            for drug_category, drug_info in self.drug_data.get("drugs", {}).items():
                keywords = drug_info.get("keywords", []) + drug_info.get("slang", [])
                if drug_match in [k.lower() for k in keywords]:
                    severity = drug_info.get("severity", 3)
                    score += severity * 3  # Reduced multiplier for more reasonable scoring
                    break
        
        # Intent indicators
        score += len(selling_indicators) * 8   # Selling intent is very suspicious
        score += len(buying_indicators) * 3    # Buying intent is moderately suspicious
        
        # Transaction indicators
        score += len(payment_indicators) * 4   # Payment mentions increase suspicion
        score += len(location_indicators) * 3  # Location mentions increase suspicion
        
        # Urgency keywords
        urgency_count = sum(1 for keyword in self.drug_data.get("urgency_keywords", [])
                          if keyword.lower() in text.lower())
        score += urgency_count * 5
        
        # Bonus for multiple indicators
        if len(drug_matches) > 1:
            score += 10  # Multiple drug types
        if selling_indicators and payment_indicators:
            score += 15  # Selling + payment = high suspicion
        if location_indicators and (selling_indicators or buying_indicators):
            score += 10  # Location + intent = high suspicion
        
        # Cap the score at 100
        return min(score, 100)
    
    def _determine_intent(self, selling_indicators: List[str], buying_indicators: List[str],
                         payment_indicators: List[str]) -> str:
        """Determine the primary intent of the content"""
        selling_score = len(selling_indicators) + (len(payment_indicators) * 0.5)
        buying_score = len(buying_indicators)
        
        if selling_score > buying_score and selling_score > 0:
            return "Selling"
        elif buying_score > selling_score and buying_score > 0:
            return "Buying"
        elif selling_score > 0 or buying_score > 0:
            return "Informational"
        else:
            return "Unknown"
    
    def _calculate_confidence(self, drug_matches: List[str], selling_indicators: List[str],
                            buying_indicators: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        total_indicators = len(drug_matches) + len(selling_indicators) + len(buying_indicators)
        
        if total_indicators == 0:
            return 0.0
        
        # Higher confidence with more indicators
        confidence = min(total_indicators * 0.2, 1.0)
        
        # Bonus for multiple drug types
        if len(drug_matches) > 1:
            confidence += 0.2
        
        # Bonus for clear intent indicators
        if selling_indicators or buying_indicators:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _extract_intent_verbs(self, doc) -> List[str]:
        """Extract verbs that indicate intent using dependency parsing"""
        intent_verbs = []
        
        if not hasattr(doc, 'sents'):
            return intent_verbs
        
        for sent in doc.sents:
            for token in sent:
                if token.pos_ == "VERB":
                    # Check if verb indicates selling/buying
                    if token.lemma_ in ["sell", "buy", "purchase", "trade", "deal", "exchange"]:
                        intent_verbs.append(token.text)
                    # Check for imperative mood (commands)
                    elif token.tag_ == "VB":  # Base form verb (often imperative)
                        intent_verbs.append(token.text)
        
        return intent_verbs
    
    def _analyze_sentiment(self, doc) -> str:
        """Analyze sentiment of the text"""
        # Simple sentiment analysis based on common words
        positive_words = ["good", "great", "excellent", "amazing", "perfect", "best", "quality"]
        negative_words = ["bad", "terrible", "awful", "worst", "fake", "scam", "rip-off"]
        
        text_lower = doc.text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

# Global instance
content_analyzer = ContentAnalysisService()

def analyze_content(text: str) -> AnalysisResult:
    """
    Analyze text content for drug-related keywords and intent
    
    Args:
        text: Text content to analyze
        
    Returns:
        AnalysisResult with analysis details
    """
    return content_analyzer.analyze_text(text)
