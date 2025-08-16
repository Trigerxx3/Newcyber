import re
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

class KeywordDetector:
    """Keyword detection and content analysis service"""
    
    def __init__(self):
        # Define keyword categories for threat detection
        self.keyword_categories = {
            'drug_trafficking': [
                'cocaine', 'heroin', 'methamphetamine', 'fentanyl', 'opioids',
                'drug trafficking', 'narcotics', 'smuggling', 'cartel',
                'dealer', 'supplier', 'shipment', 'delivery'
            ],
            'weapons': [
                'firearms', 'weapons', 'guns', 'ammunition', 'explosives',
                'bombs', 'terrorism', 'attack', 'threat', 'violence'
            ],
            'cybercrime': [
                'hacking', 'malware', 'ransomware', 'phishing', 'ddos',
                'cyber attack', 'data breach', 'stolen', 'credentials',
                'bitcoin', 'cryptocurrency', 'dark web', 'tor'
            ],
            'human_trafficking': [
                'human trafficking', 'sex trafficking', 'forced labor',
                'smuggling', 'victims', 'exploitation', 'modern slavery'
            ],
            'financial_crime': [
                'money laundering', 'fraud', 'scam', 'identity theft',
                'credit card', 'banking', 'financial crime', 'embezzlement'
            ],
            'extremism': [
                'terrorism', 'extremist', 'radical', 'hate speech',
                'violent', 'threat', 'attack', 'bomb', 'kill'
            ]
        }
        
        # Risk scoring weights
        self.risk_weights = {
            'drug_trafficking': 8,
            'weapons': 9,
            'cybercrime': 7,
            'human_trafficking': 10,
            'financial_crime': 6,
            'extremism': 9
        }
        
        # Compile regex patterns for better performance
        self.patterns = {}
        for category, keywords in self.keyword_categories.items():
            pattern = '|'.join(map(re.escape, keywords))
            self.patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def analyze_content(self, text: str) -> Dict:
        """
        Analyze content for keywords and assess risk level
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not text:
                return {
                    'risk_level': 'low',
                    'keywords': [],
                    'categories_found': [],
                    'risk_score': 0,
                    'analysis': 'No content to analyze'
                }
            
            # Find keywords in each category
            found_keywords = {}
            category_matches = {}
            
            for category, pattern in self.patterns.items():
                matches = pattern.findall(text.lower())
                if matches:
                    found_keywords[category] = list(set(matches))
                    category_matches[category] = len(matches)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(category_matches)
            risk_level = self._determine_risk_level(risk_score)
            
            # Get all unique keywords found
            all_keywords = []
            for keywords in found_keywords.values():
                all_keywords.extend(keywords)
            
            analysis_result = {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'keywords': list(set(all_keywords)),
                'categories_found': list(found_keywords.keys()),
                'category_details': found_keywords,
                'match_counts': category_matches,
                'analysis': self._generate_analysis_summary(found_keywords, risk_level)
            }
            
            logger.info(f"Content analysis completed. Risk level: {risk_level}, Score: {risk_score}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {
                'risk_level': 'unknown',
                'keywords': [],
                'categories_found': [],
                'risk_score': 0,
                'analysis': f'Error during analysis: {str(e)}'
            }
    
    def _calculate_risk_score(self, category_matches: Dict) -> int:
        """Calculate risk score based on keyword matches"""
        total_score = 0
        
        for category, count in category_matches.items():
            weight = self.risk_weights.get(category, 1)
            # Apply logarithmic scaling to prevent score explosion
            score = weight * min(count, 10)  # Cap at 10 matches per category
            total_score += score
        
        return total_score
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level based on score"""
        if risk_score >= 50:
            return 'critical'
        elif risk_score >= 30:
            return 'high'
        elif risk_score >= 15:
            return 'medium'
        else:
            return 'low'
    
    def _generate_analysis_summary(self, found_keywords: Dict, risk_level: str) -> str:
        """Generate human-readable analysis summary"""
        if not found_keywords:
            return "No suspicious keywords detected."
        
        categories = list(found_keywords.keys())
        total_keywords = sum(len(keywords) for keywords in found_keywords.values())
        
        summary = f"Risk Level: {risk_level.upper()}. "
        summary += f"Found {total_keywords} suspicious keywords across {len(categories)} categories: "
        summary += ", ".join(categories)
        
        return summary
    
    def add_custom_keywords(self, category: str, keywords: List[str]):
        """Add custom keywords to a category"""
        if category not in self.keyword_categories:
            self.keyword_categories[category] = []
            self.risk_weights[category] = 5  # Default weight
        
        self.keyword_categories[category].extend(keywords)
        
        # Recompile pattern for this category
        pattern = '|'.join(map(re.escape, self.keyword_categories[category]))
        self.patterns[category] = re.compile(pattern, re.IGNORECASE)
        
        logger.info(f"Added {len(keywords)} custom keywords to category '{category}'")
    
    def remove_keywords(self, category: str, keywords: List[str]):
        """Remove keywords from a category"""
        if category in self.keyword_categories:
            for keyword in keywords:
                if keyword in self.keyword_categories[category]:
                    self.keyword_categories[category].remove(keyword)
            
            # Recompile pattern for this category
            if self.keyword_categories[category]:
                pattern = '|'.join(map(re.escape, self.keyword_categories[category]))
                self.patterns[category] = re.compile(pattern, re.IGNORECASE)
            else:
                # Remove category if no keywords left
                del self.keyword_categories[category]
                del self.risk_weights[category]
                if category in self.patterns:
                    del self.patterns[category]
        
        logger.info(f"Removed {len(keywords)} keywords from category '{category}'")
    
    def get_keyword_statistics(self) -> Dict:
        """Get statistics about keyword categories"""
        stats = {
            'total_categories': len(self.keyword_categories),
            'total_keywords': sum(len(keywords) for keywords in self.keyword_categories.values()),
            'categories': {}
        }
        
        for category, keywords in self.keyword_categories.items():
            stats['categories'][category] = {
                'keyword_count': len(keywords),
                'risk_weight': self.risk_weights.get(category, 1)
            }
        
        return stats
    
    def validate_keywords(self, text: str, keywords: List[str]) -> Dict:
        """Validate which keywords are found in text"""
        found = []
        not_found = []
        
        for keyword in keywords:
            if re.search(re.escape(keyword), text, re.IGNORECASE):
                found.append(keyword)
            else:
                not_found.append(keyword)
        
        return {
            'found': found,
            'not_found': not_found,
            'total_found': len(found),
            'total_searched': len(keywords)
        } 