"""
Training script for content classifier
Generates sample training data and trains the ML model
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_models.content_classifier import ContentClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_training_data():
    """
    Generate sample training data for drug-related content classification
    
    Returns:
        Tuple of (texts, labels) where labels are 1 for drug-related, 0 for non-drug-related
    """
    # Drug-related content samples (label = 1)
    drug_related_texts = [
        "Buy MDMA cheap, DM me for prices",
        "LSD available, high quality, tested",
        "Cocaine for sale, contact for delivery",
        "Weed available, message for details",
        "Heroin pure quality, DM for price",
        "Methamphetamine in stock, cheap prices",
        "Ecstasy pills available, contact me",
        "Cannabis for sale, delivery available",
        "Oxycodone prescription drugs, message me",
        "Fentanyl available, high purity",
        "Looking to buy cocaine, DM me",
        "Need LSD, who has it?",
        "Selling weed, contact for prices",
        "MDMA pills, tested and pure",
        "Cocaine delivery available",
        "Buy drugs online, secure payment",
        "Weed for sale, message me",
        "LSD tabs available, contact",
        "Cocaine pure quality, DM",
        "Methamphetamine cheap prices",
        "Need prescription drugs, oxycodone",
        "Buying heroin, who sells?",
        "Ecstasy available, tested",
        "Cannabis delivery service",
        "Fentanyl high quality",
        "Looking for cocaine dealer",
        "MDMA for sale, contact",
        "Weed available, cheap",
        "LSD tabs, message me",
        "Cocaine pure, DM for price",
        "Buying drugs, need contact",
        "Heroin available, delivery",
        "Methamphetamine in stock",
        "Prescription drugs for sale",
        "Ecstasy pills, tested",
        "Cannabis for sale, contact",
        "Fentanyl pure quality",
        "Need cocaine, DM me",
        "Weed delivery available",
        "LSD available, message",
        "Buying MDMA, who has?",
        "Cocaine dealer needed",
        "Heroin for sale, contact",
        "Methamphetamine cheap",
        "Prescription drugs available",
        "Ecstasy tabs, DM me",
        "Cannabis cheap prices",
        "Fentanyl high purity",
        "Looking for drug dealer",
        "Cocaine available, message"
    ]
    
    # Non-drug-related content samples (label = 0)
    non_drug_texts = [
        "Just had a great coffee this morning",
        "Beautiful weather today, perfect for a walk",
        "Working on a new project, excited to share",
        "Love spending time with family",
        "Reading a great book, highly recommend",
        "Cooked an amazing dinner tonight",
        "Went to the gym, feeling great",
        "Watching a movie with friends",
        "Learning a new programming language",
        "Traveling to a new city next week",
        "Enjoying the weekend, relaxing",
        "Had a productive day at work",
        "Trying out a new restaurant",
        "Playing video games with friends",
        "Listening to music, great playlist",
        "Working on my fitness goals",
        "Spending time in nature",
        "Learning to cook new recipes",
        "Reading about history",
        "Planning a vacation",
        "Enjoying a cup of tea",
        "Working on personal projects",
        "Meeting friends for lunch",
        "Watching sports on TV",
        "Learning photography",
        "Gardening in my backyard",
        "Writing in my journal",
        "Practicing meditation",
        "Attending a concert",
        "Exploring local parks",
        "Trying new hobbies",
        "Volunteering in the community",
        "Learning a musical instrument",
        "Reading news articles",
        "Planning home improvements",
        "Enjoying art galleries",
        "Attending workshops",
        "Spending time with pets",
        "Learning new skills",
        "Exploring new neighborhoods",
        "Trying different cuisines",
        "Working on creative projects",
        "Attending social events",
        "Learning about technology",
        "Enjoying outdoor activities",
        "Reading science articles",
        "Planning future goals",
        "Spending quality time",
        "Learning about culture",
        "Exploring new interests"
    ]
    
    # Combine and label
    texts = drug_related_texts + non_drug_texts
    labels = [1] * len(drug_related_texts) + [0] * len(non_drug_texts)
    
    return texts, labels

def main():
    """Main training function"""
    logger.info("Starting content classifier training...")
    
    # Initialize classifier
    classifier = ContentClassifier()
    
    # Generate training data
    logger.info("Generating training data...")
    texts, labels = generate_training_data()
    
    logger.info(f"Training on {len(texts)} samples ({sum(labels)} drug-related, {len(labels) - sum(labels)} non-drug-related)")
    
    # Train model
    try:
        results = classifier.train(texts, labels)
        
        logger.info("Training completed successfully!")
        logger.info(f"Training accuracy: {results['train_accuracy']:.4f}")
        logger.info(f"Test accuracy: {results['test_accuracy']:.4f}")
        logger.info(f"Model saved to: {results['model_path']}")
        
        # Test prediction
        test_text = "Buy MDMA cheap, DM me"
        prediction = classifier.predict(test_text)
        logger.info(f"\nTest prediction for '{test_text}':")
        logger.info(f"  Prediction: {prediction['prediction']}")
        logger.info(f"  Confidence: {prediction['confidence']:.4f}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
