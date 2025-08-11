#!/usr/bin/env python
"""
Quick test script to verify The Quotes Hub API is working.
"""

import requests
import json


def test_quotes_hub_api():
    """Test The Quotes Hub API."""
    url = "https://thequoteshub.com/api/random-quote"
    
    print("Testing The Quotes Hub API...")
    print(f"URL: {url}\n")
    
    try:
        # Make request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        # Display results
        print("✅ API is working!")
        print("\nResponse format:")
        print(json.dumps(data, indent=2))
        
        # Extract fields (API returns: text, author, topic)
        text = data.get('text', 'N/A')
        author = data.get('author', 'N/A')
        topic = data.get('topic', 'N/A')
        
        print("\nExtracted data:")
        print(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
        print(f"Author: {author}")
        print(f"Topic: {topic}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_multiple_requests():
    """Test multiple API requests to check consistency."""
    print("\n" + "="*50)
    print("Testing multiple requests (5 quotes)...")
    print("="*50 + "\n")
    
    url = "https://thequoteshub.com/api/random-quote"
    
    for i in range(5):
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            text = data.get('text', 'N/A')
            # Truncate long quotes for display
            if len(text) > 80:
                text = text[:77] + "..."
            author = data.get('author', 'Unknown')
            topic = data.get('topic', 'N/A')
            
            print(f"{i+1}. \"{text}\"")
            print(f"   - {author} (Topic: {topic})\n")
            
        except Exception as e:
            print(f"{i+1}. Failed: {e}\n")


if __name__ == "__main__":
    print("🔧 Testing The Quotes Hub API for Quotescape\n")
    
    # Test single request
    if test_quotes_hub_api():
        # Test multiple requests
        test_multiple_requests()
        
        print("\n✅ All tests passed! The API is working correctly.")
        print("\nYou can now run Quotescape with:")
        print("  python run_quotescape.py")
    else:
        print("\n❌ API test failed. Please check your internet connection.")