#!/usr/bin/env python
"""
Test script for file upload functionality.
This script tests the webhook with a sample image file.
"""

import os
import sys
import django
import requests
from pathlib import Path

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agripulse.settings')
django.setup()

def test_file_upload():
    """Test the file upload functionality with a sample image."""
    
    # Test with a sample image file (you can replace this with any image file)
    sample_image_path = "CDDM/potato early.png"  # Use one of your existing images
    
    if not os.path.exists(sample_image_path):
        print(f"Sample image not found at {sample_image_path}")
        print("Please provide a valid image file path.")
        return
    
    # Test data
    test_data = {
        'crop': 'potato'
    }
    
    # Test file
    test_files = {
        'image': open(sample_image_path, 'rb')
    }
    
    print("Testing file upload functionality...")
    print(f"Image file: {sample_image_path}")
    print(f"Crop: {test_data['crop']}")
    print("-" * 50)
    
    try:
        # Make request to webhook
        response = requests.post(
            'http://localhost:8000/farmbot/webhook/',
            data=test_data,
            files=test_files
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✅ Success! Webhook response:")
                print(result.get('fulfillmentText', 'No response text'))
            except:
                print("\n⚠️ Response is not JSON format:")
                print(response.text)
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Make sure Django server is running on localhost:8000")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        # Close the file
        test_files['image'].close()

def test_webhook_with_curl():
    """Show curl command for testing."""
    print("\n" + "="*60)
    print("ALTERNATIVE: Test with curl command")
    print("="*60)
    print("Replace 'path/to/your/image.jpg' with actual image path:")
    print()
    print("curl -X POST http://localhost:8000/farmbot/webhook/ \\")
    print("  -F 'crop=potato' \\")
    print("  -F 'image=@path/to/your/image.jpg'")
    print()
    print("Or test the web interface at: http://localhost:8000/farmbot/test-upload/")

if __name__ == "__main__":
    print("=== File Upload Test for Disease Prediction ===")
    print()
    
    # Test file upload
    test_file_upload()
    
    # Show alternative testing methods
    test_webhook_with_curl()
    
    print("\n=== Test Complete ===")
    print("Note: Make sure your Django server is running with: python manage.py runserver")
