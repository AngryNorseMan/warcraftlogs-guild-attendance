#!/usr/bin/env python3
"""
Simple test script to verify Warcraft Logs API authentication
"""

import requests
import base64
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTH_URL = "https://fresh.warcraftlogs.com/oauth/token"

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: CLIENT_ID and CLIENT_SECRET must be set in .env file")
        print("Copy .env.sample to .env and add your credentials")
        sys.exit(1)
        
    print("🔐 Testing Fresh Warcraft Logs API authentication...")
    print(f"Using URL: {AUTH_URL}")
    
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
        print("Making authentication request...")
        response = requests.post(AUTH_URL, headers=headers, data=data, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text[:500]}...")
        
        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                print("✅ Authentication successful!")
                print(f"Token type: {token_data.get('token_type', 'N/A')}")
                print(f"Expires in: {token_data.get('expires_in', 'N/A')} seconds")
                return True
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
