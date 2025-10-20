#!/usr/bin/env python
"""
Test script for the disease prediction integration.
This script tests the webhook functionality without running the full Django server.
"""

import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agripulse.settings')
django.setup()

from farmbot.disease_prediction_service import disease_service

def test_disease_prediction():
    """Test the disease prediction service with a sample image URL."""
    
    # Test with a sample image URL (you can replace this with a real image URL)
    test_image_url = "https://example.com/potato_leaf.jpg"  # Replace with actual image URL
    test_crop = "potato"
    
    print("Testing disease prediction service...")
    print(f"Image URL: {test_image_url}")
    print(f"Crop: {test_crop}")
    print("-" * 50)
    
    try:
        # Test the prediction
        result = disease_service.predict_from_url(test_image_url, test_crop)
        
        print("Prediction Result:")
        print(json.dumps(result, indent=2))
        print("-" * 50)
        
        # Test the response formatting
        formatted_response = disease_service.format_response(result)
        print("Formatted Response:")
        print(formatted_response)
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        print("Note: This is expected if the image URL is not accessible.")

def test_webhook_payload():
    """Test the webhook payload structure."""
    
    sample_payload = {
        "queryResult": {
            "intent": {
                "displayName": "crop_disease_prediction"
            },
            "parameters": {
                "crop": "potato",
                "image_url": "https://example.com/potato_leaf.jpg"
            }
        }
    }
    
    print("Sample Dialogflow webhook payload:")
    print(json.dumps(sample_payload, indent=2))
    print("-" * 50)

if __name__ == "__main__":
    print("=== Disease Prediction Integration Test ===")
    print()
    
    # Test webhook payload structure
    test_webhook_payload()
    
    # Test disease prediction service
    test_disease_prediction()
    
    print("\n=== Test Complete ===")
    print("Note: To test with real images, replace the test_image_url with a valid image URL.")
