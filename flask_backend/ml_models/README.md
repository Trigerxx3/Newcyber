# ML Models for Content Classification and Risk Scoring

This directory contains machine learning models for enhanced content analysis in the Narcotics Intelligence Platform.

## Overview

The ML system consists of two main components:

1. **Content Classifier** (`content_classifier.py`): Uses TF-IDF + Logistic Regression to classify content as "Drug-Related" or "Non-Drug-Related"
2. **Risk Scoring Engine** (`risk_scoring.py`): Uses RandomForest/GradientBoosting to calculate risk scores (0-100) and risk levels (High/Medium/Low)

## Files

- `content_classifier.py`: ML-based content classification model
- `risk_scoring.py`: ML-based risk scoring engine
- `train_content_classifier.py`: Training script for content classifier
- `__init__.py`: Package initialization

## Training the Models

### Content Classifier

To train the content classifier:

```bash
cd flask_backend
python ml_models/train_content_classifier.py
```

This will:
- Generate sample training data
- Train the TF-IDF + Logistic Regression model
- Save the model to `ml_models/content_classifier.pkl`
- Save the vectorizer to `ml_models/tfidf_vectorizer.pkl`

### Risk Scoring Engine

The risk scoring engine can be trained programmatically. Example:

```python
from ml_models.risk_scoring import RiskScoringEngine

engine = RiskScoringEngine()
engine.train(
    texts=texts,
    keyword_counts=keyword_counts,
    ml_confidences=ml_confidences,
    post_frequencies=post_frequencies,
    platforms=platforms,
    risk_scores=risk_scores
)
```

## Usage

The models are automatically integrated into the content analysis pipeline via `services/ml_content_analysis.py`. They are used when analyzing content through the `/api/content-analysis/analyze` endpoint.

### Manual Usage

```python
from ml_models.content_classifier import ContentClassifier
from ml_models.risk_scoring import RiskScoringEngine

# Content Classification
classifier = ContentClassifier()
result = classifier.predict("Buy MDMA cheap, DM me")
# Returns: {"prediction": "Drug-Related", "confidence": 0.92, "label": 1}

# Risk Scoring
risk_engine = RiskScoringEngine()
risk_result = risk_engine.calculate_risk_score(
    text="Buy MDMA cheap, DM me",
    keyword_count=3,
    ml_confidence=0.92,
    post_frequency=2.0,
    platform="Telegram"
)
# Returns: {"risk_score": 87, "risk_level": "High"}
```

## Model Artifacts

Trained models are saved as:
- `content_classifier.pkl`: Trained classification pipeline
- `tfidf_vectorizer.pkl`: TF-IDF vectorizer
- `risk_scoring_rf.pkl` or `risk_scoring_gb.pkl`: Risk scoring model
- `platform_encoder.pkl`: Platform label encoder

## Fallback Behavior

If models are not trained or fail to load, the system falls back to:
- Keyword-based classification (default: "Non-Drug-Related" with 0.5 confidence)
- Rule-based risk scoring using keyword counts and platform multipliers

## Dependencies

- scikit-learn >= 1.3.0
- joblib >= 1.3.0
- numpy >= 1.26.0

## Notes

- Models are loaded lazily on first use
- Training data should be representative of real-world content
- Models can be retrained with new data to improve accuracy
- Risk thresholds: 0-40 (Low), 41-70 (Medium), 71-100 (High)
