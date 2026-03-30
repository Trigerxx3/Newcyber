"""
ML-based Content Classifier
Uses TF-IDF Vectorizer + Logistic Regression for drug-related content classification
"""
import os
import joblib
import logging
from typing import Dict, Optional
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import re

logger = logging.getLogger(__name__)

class ContentClassifier:
    """
    ML-based content classifier for drug-related content detection
    
    Labels:
        1 → Drug-Related
        0 → Non-Drug-Related
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the content classifier
        
        Args:
            model_dir: Directory to load/save model artifacts (default: flask_backend/ml_models/)
        """
        if model_dir is None:
            # Default to flask_backend/ml_models/ directory
            base_dir = Path(__file__).parent
            model_dir = str(base_dir)
        
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'content_classifier.pkl')
        self.vectorizer_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
        
        self.model: Optional[Pipeline] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.is_loaded = False
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model and vectorizer from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.is_loaded = True
                logger.info(f"Loaded content classifier from {self.model_dir}")
            else:
                logger.warning(f"Model files not found. Train the model first using train_content_classifier.py")
                self.is_loaded = False
        except Exception as e:
            logger.error(f"Failed to load content classifier: {str(e)}")
            self.is_loaded = False
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for classification
        
        Args:
            text: Raw text input
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        return text.strip()
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Predict if content is drug-related
        
        Args:
            text: Raw text content to classify
            
        Returns:
            Dictionary with prediction and confidence:
            {
                "prediction": "Drug-Related" | "Non-Drug-Related",
                "confidence": float (0-1),
                "label": 1 | 0
            }
        """
        if not self.is_loaded or self.model is None:
            logger.warning("Model not loaded. Returning default prediction.")
            return {
                "prediction": "Non-Drug-Related",
                "confidence": 0.5,
                "label": 0
            }
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            if not processed_text:
                return {
                    "prediction": "Non-Drug-Related",
                    "confidence": 0.5,
                    "label": 0
                }
            
            # Predict
            prediction = self.model.predict([processed_text])[0]
            probabilities = self.model.predict_proba([processed_text])[0]
            
            # Get confidence (probability of predicted class)
            confidence = float(probabilities[prediction])
            
            # Map label to human-readable prediction
            prediction_label = "Drug-Related" if prediction == 1 else "Non-Drug-Related"
            
            return {
                "prediction": prediction_label,
                "confidence": confidence,
                "label": int(prediction)
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                "prediction": "Non-Drug-Related",
                "confidence": 0.5,
                "label": 0
            }
    
    def train(self, texts: list, labels: list, test_size: float = 0.2, random_state: int = 42):
        """
        Train the content classifier
        
        Args:
            texts: List of text samples
            labels: List of labels (1 for drug-related, 0 for non-drug-related)
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
        """
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                processed_texts, labels, test_size=test_size, random_state=random_state, stratify=labels
            )
            
            # Create pipeline with TF-IDF and Logistic Regression
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),  # Unigrams and bigrams
                    min_df=2,  # Minimum document frequency
                    max_df=0.95,  # Maximum document frequency
                    stop_words='english'
                )),
                ('classifier', LogisticRegression(
                    max_iter=1000,
                    random_state=random_state,
                    class_weight='balanced'  # Handle imbalanced data
                ))
            ])
            
            # Train
            logger.info(f"Training classifier on {len(X_train)} samples...")
            pipeline.fit(X_train, y_train)
            
            # Evaluate
            train_score = pipeline.score(X_train, y_train)
            test_score = pipeline.score(X_test, y_test)
            
            logger.info(f"Training accuracy: {train_score:.4f}")
            logger.info(f"Test accuracy: {test_score:.4f}")
            
            # Save model
            self.model = pipeline
            self.vectorizer = pipeline.named_steps['tfidf']
            
            # Save to disk
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump(pipeline, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            
            self.is_loaded = True
            logger.info(f"Model saved to {self.model_dir}")
            
            return {
                "train_accuracy": train_score,
                "test_accuracy": test_score,
                "model_path": self.model_path
            }
            
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise
