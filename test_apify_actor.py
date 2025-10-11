#!/usr/bin/env python3
"""
Test Apify Actor Execution
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_apify_actor_run():
    """Test running the Apify actor"""
    print("🔍 Testing Apify Actor Execution...")
    
    token = os.getenv('APIFY_TOKEN')
    actor_id = os.getenv('APIFY_ACTOR_ID')
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Get actor info
    url = f"https://api.apify.com/v2/acts/{actor_id}"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        actor_data = response.json().get('data', {})
        print(f"✅ Actor: {actor_data.get('name')}")
        print(f"   Version: {actor_data.get('taggedBuilds', {}).get('latest', 'Unknown')}")
        print(f"   Modified: {actor_data.get('modifiedAt', 'Unknown')}")
        
        # Get last runs
        runs_url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
        runs_response = requests.get(runs_url, headers=headers, params={'limit': 5}, timeout=10)
        
        if runs_response.status_code == 200:
            runs = runs_response.json().get('data', {}).get('items', [])
            print(f"\n📊 Last 5 Runs:")
            for run in runs:
                status = run.get('status')
                started = run.get('startedAt', 'Unknown')
                finished = run.get('finishedAt', 'Unknown')
                print(f"   • {status}: {started[:19]} → {finished[:19] if finished != 'Unknown' else 'Running'}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

if __name__ == "__main__":
    test_apify_actor_run()
