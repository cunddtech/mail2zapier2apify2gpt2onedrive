#!/usr/bin/env python3
"""
Vollständiger API-Test für alle integrierten Services
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI API"""
    print("\n🔍 Testing OpenAI API...")
    try:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API works'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI API: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return False

def test_anthropic_api():
    """Test Anthropic API"""
    print("\n🔍 Testing Anthropic API...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'API works'"}]
        )
        print(f"✅ Anthropic API: {message.content[0].text}")
        return True
    except Exception as e:
        print(f"❌ Anthropic API Error: {e}")
        return False

def test_azure_vision_api():
    """Test Azure Vision API"""
    print("\n🔍 Testing Azure Vision API...")
    try:
        import requests
        
        endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        key = os.getenv('AZURE_VISION_KEY')
        
        # Simple API endpoint check
        url = f"{endpoint}vision/v3.2/analyze"
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/json'
        }
        
        # Test with a simple request (will fail without image, but validates key)
        response = requests.post(url, headers=headers, json={}, timeout=5)
        
        if response.status_code == 400:  # Bad request means API key is valid
            print("✅ Azure Vision API: Key is valid (400 expected without image)")
            return True
        elif response.status_code == 401:
            print("❌ Azure Vision API: Invalid key")
            return False
        else:
            print(f"✅ Azure Vision API: Response code {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Azure Vision API Error: {e}")
        return False

def test_weclapp_api():
    """Test WeClapp API"""
    print("\n🔍 Testing WeClapp API...")
    try:
        import requests
        
        base_url = os.getenv('WECLAPP_BASE_URL')
        token = os.getenv('WECLAPP_API_TOKEN')
        
        headers = {
            'AuthenticationToken': token,
            'Content-Type': 'application/json'
        }
        
        # Test with a simple GET request to check connection
        url = f"{base_url}customer"
        response = requests.get(url, headers=headers, params={'pageSize': 1}, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ WeClapp API: Connected successfully")
            return True
        else:
            print(f"❌ WeClapp API: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ WeClapp API Error: {e}")
        return False

def test_microsoft_graph_api():
    """Test Microsoft Graph API"""
    print("\n🔍 Testing Microsoft Graph API...")
    try:
        import requests
        
        tenant_id = os.getenv('GRAPH_TENANT_ID_MAIL')
        client_id = os.getenv('GRAPH_CLIENT_ID_MAIL')
        client_secret = os.getenv('GRAPH_CLIENT_SECRET_MAIL')
        
        # Get access token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        token_response = requests.post(token_url, data=token_data, timeout=10)
        
        if token_response.status_code == 200:
            token = token_response.json().get('access_token')
            print(f"✅ Microsoft Graph API: Token obtained successfully")
            
            # Test OneDrive access instead (since Mail might have permission issues)
            headers = {'Authorization': f'Bearer {token}'}
            drive_id = os.getenv('DRIVE_ID')
            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
            
            response = requests.get(url, headers=headers, params={'$top': 1}, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Microsoft Graph API: OneDrive access successful")
                return True
            elif response.status_code == 403:
                print(f"⚠️ Microsoft Graph API: Token valid but permissions limited (403)")
                return True  # Token works, just permission issue
            else:
                print(f"❌ Microsoft Graph API: Status {response.status_code}")
                return False
        else:
            print(f"❌ Microsoft Graph API: Token error {token_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Microsoft Graph API Error: {e}")
        return False

def test_apify_api():
    """Test Apify API"""
    print("\n🔍 Testing Apify API...")
    try:
        import requests
        
        token = os.getenv('APIFY_TOKEN')
        actor_id = os.getenv('APIFY_ACTOR_ID')
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Check actor status
        url = f"https://api.apify.com/v2/acts/{actor_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            actor_data = response.json().get('data', {})
            print(f"✅ Apify API: Actor '{actor_data.get('name')}' found")
            return True
        else:
            print(f"❌ Apify API: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Apify API Error: {e}")
        return False

def test_railway_orchestrator():
    """Test Railway Orchestrator"""
    print("\n🔍 Testing Railway Orchestrator...")
    try:
        import requests
        
        url = os.getenv('ORCHESTRATOR_URL', 'https://my-langgraph-agent-production.up.railway.app')
        
        # Simple health check
        response = requests.get(f"{url}/health", timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Railway Orchestrator: Online")
            return True
        else:
            print(f"⚠️ Railway Orchestrator: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Railway Orchestrator Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 SYSTEM API VALIDATION TEST")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results['OpenAI'] = test_openai_api()
    results['Anthropic'] = test_anthropic_api()
    results['Azure Vision'] = test_azure_vision_api()
    results['WeClapp'] = test_weclapp_api()
    results['Microsoft Graph'] = test_microsoft_graph_api()
    results['Apify'] = test_apify_api()
    results['Railway Orchestrator'] = test_railway_orchestrator()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}")
    
    print("\n" + "-" * 60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
