#!/usr/bin/env python3
"""
Test script for content analysis API
"""
import requests
import json
import time

def test_content_analysis():
    """Test the content analysis API"""
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_cases = [
        {
            "name": "High Suspicion (Selling)",
            "data": {
                "platform": "Instagram",
                "username": "drugdealer123",
                "content": "Fresh batch of cocaine available. DM for prices. Cash only."
            },
            "expected_score": 80
        },
        {
            "name": "Medium Suspicion (Buying)",
            "data": {
                "platform": "Telegram",
                "username": "buyer456",
                "content": "Looking for some good weed in the area. Any recommendations?"
            },
            "expected_score": 40
        },
        {
            "name": "Low Suspicion (Informational)",
            "data": {
                "platform": "Twitter",
                "username": "info_user",
                "content": "What are the effects of marijuana on the brain?"
            },
            "expected_score": 20
        },
        {
            "name": "Clean Content",
            "data": {
                "platform": "Instagram",
                "username": "clean_user",
                "content": "Just had a great workout at the gym today! 💪"
            },
            "expected_score": 0
        }
    ]
    
    print("🧪 Testing Content Analysis API...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Content: '{test_case['data']['content']}'")
        
        try:
            # Note: In a real test, you'd need to authenticate first
            # For now, we'll test the service directly
            from services.content_analysis import analyze_content
            
            result = analyze_content(test_case['data']['content'])
            
            print(f"✅ Analysis Result:")
            print(f"   Suspicion Score: {result.suspicion_score}%")
            print(f"   Intent: {result.intent}")
            print(f"   Flagged: {result.is_flagged}")
            print(f"   Keywords: {result.matched_keywords}")
            print(f"   Confidence: {result.confidence:.2f}")
            
            # Check if score is in expected range
            if test_case['expected_score'] == 0:
                if result.suspicion_score <= 10:
                    print("✅ PASS - Low suspicion as expected")
                else:
                    print(f"⚠️  UNEXPECTED - Expected ~{test_case['expected_score']}, got {result.suspicion_score}")
            elif abs(result.suspicion_score - test_case['expected_score']) <= 20:
                print(f"✅ PASS - Score within expected range")
            else:
                print(f"⚠️  UNEXPECTED - Expected ~{test_case['expected_score']}, got {result.suspicion_score}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Content Analysis Test Complete!")
    print("\n💡 To test the full API:")
    print("1. Go to http://localhost:5000/api/auth/login")
    print("2. Login with admin@cyber.com / admin123456")
    print("3. Use the token to test POST /api/content-analysis/analyze")

if __name__ == "__main__":
    test_content_analysis()
