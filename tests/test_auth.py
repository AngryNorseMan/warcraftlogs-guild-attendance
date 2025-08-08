#!/usr/bin/env python3
"""
Simple test to debug the Warcraft Logs API connection
"""

import requests
import base64
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTH_URL = "https://www.warcraftlogs.com/oauth/token"

def test_auth():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: CLIENT_ID and CLIENT_SECRET must be set in .env file")
        print("Copy .env.sample to .env and add your credentials")
        sys.exit(1)
        
    print("🔐 Testing Warcraft Logs API authentication...")
    
    # Create basic auth header
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials'
    }
    
    try:
        print(f"Making request to: {AUTH_URL}")
        response = requests.post(AUTH_URL, headers=headers, data=data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            print("✓ Successfully authenticated!")
            print(f"Token (first 20 chars): {access_token[:20]}...")
            return True
        else:
            print("❌ No access token in response")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    test_auth()
