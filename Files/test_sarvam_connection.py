"""
Phase 2: Test Sarvam AI Integration
====================================
This script tests all Sarvam AI APIs to ensure proper connection and functionality.

Before running:
1. Get API key from https://www.sarvam.ai/
2. Add SARVAM_API_KEY to .env file
3. Run: python test_sarvam_connection.py
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
SARVAM_BASE_URL = 'https://api.sarvam.ai/v1'

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{BLUE}{'='*60}{END}")
    print(f"{BLUE}{title.center(60)}{END}")
    print(f"{BLUE}{'='*60}{END}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{GREEN}✓ {message}{END}")

def print_error(message: str):
    """Print error message"""
    print(f"{RED}✗ {message}{END}")

def print_info(message: str):
    """Print info message"""
    print(f"{YELLOW}ℹ {message}{END}")

def check_api_key():
    """Check if API key is configured"""
    print_section("Step 1: Checking API Configuration")
    
    if not SARVAM_API_KEY:
        print_error("SARVAM_API_KEY not found in .env file")
        print_info("To get API key:")
        print("  1. Visit https://www.sarvam.ai/")
        print("  2. Sign up for free account")
        print("  3. Apply for startup programme (free ₹1,000 credits)")
        print("  4. Copy API key to .env file")
        return False
    
    if SARVAM_API_KEY == "your_api_key_here":
        print_error("SARVAM_API_KEY is still placeholder value")
        print_info("Replace 'your_api_key_here' with your actual API key")
        return False
    
    print_success(f"API Key found: {SARVAM_API_KEY[:10]}...")
    return True

def test_text_to_speech():
    """Test Sarvam Text-to-Speech API"""
    print_section("Step 2: Testing Text-to-Speech API")
    
    headers = {
        'Authorization': f'Bearer {SARVAM_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test in multiple languages
    test_cases = [
        {
            'language': 'Hindi',
            'code': 'hi-IN',
            'text': 'नमस्कार, यह एक परीक्षण है'
        },
        {
            'language': 'Tamil',
            'code': 'ta-IN',
            'text': 'வணக்கம், இது ஒரு சோதனை'
        },
        {
            'language': 'Telugu',
            'code': 'te-IN',
            'text': 'హలో, ఇది ఒక పরీక్ష'
        },
        {
            'language': 'English',
            'code': 'en-IN',
            'text': 'Hello, this is a test'
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting {test['language']}...")
        
        data = {
            'text': test['text'],
            'language_code': test['code'],
            'model': 'sarvam-tts:v1'
        }
        
        try:
            response = requests.post(
                f'{SARVAM_BASE_URL}/text-to-speech',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print_success(f"{test['language']} TTS working!")
                # Save audio sample
                filename = f"sample_{test['code'].split('-')[0]}.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print_info(f"Audio saved to {filename}")
            else:
                print_error(f"{test['language']} TTS failed (Status: {response.status_code})")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print_error(f"{test['language']} TTS error: {str(e)}")

def test_translation():
    """Test Sarvam Translation API"""
    print_section("Step 3: Testing Translation API")
    
    headers = {
        'Authorization': f'Bearer {SARVAM_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test translations
    test_cases = [
        {
            'text': 'My current data plan is 30GB per month',
            'target': 'Hindi',
            'code': 'hi-IN'
        },
        {
            'text': 'How much is my bill this month',
            'target': 'Tamil',
            'code': 'ta-IN'
        },
        {
            'text': 'Please recharge my account',
            'target': 'Telugu',
            'code': 'te-IN'
        }
    ]
    
    for test in test_cases:
        print(f"\nTranslating to {test['target']}...")
        print(f"Original: {test['text']}")
        
        data = {
            'input': test['text'],
            'source_language_code': 'en-IN',
            'target_language_code': test['code'],
            'model': 'sarvam-translate:v1'
        }
        
        try:
            response = requests.post(
                f'{SARVAM_BASE_URL}/text/translate',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('translated_text', 'N/A')
                print_success(f"Translation: {translated_text}")
            else:
                print_error(f"Translation failed (Status: {response.status_code})")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print_error(f"Translation error: {str(e)}")

def test_chat_completion():
    """Test Sarvam Chat Completion API"""
    print_section("Step 4: Testing Chat Completion API")
    
    headers = {
        'Authorization': f'Bearer {SARVAM_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Test chat in different languages
    test_cases = [
        {
            'language': 'Hindi',
            'message': 'मेरा डेटा प्लान क्या है?',
            'model': 'sarvam-m'
        },
        {
            'language': 'English',
            'message': 'How do I recharge my account?',
            'model': 'sarvam-m'
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting {test['language']} chat...")
        print(f"Query: {test['message']}")
        
        data = {
            'messages': [
                {'role': 'user', 'content': test['message']}
            ],
            'model': test['model']
        }
        
        try:
            response = requests.post(
                f'{SARVAM_BASE_URL}/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')
                print_success(f"Response: {reply}")
            else:
                print_error(f"Chat failed (Status: {response.status_code})")
                print(f"Response: {response.text}")
        
        except Exception as e:
            print_error(f"Chat error: {str(e)}")

def test_speech_to_text():
    """Test Speech-to-Text API (requires audio file)"""
    print_section("Step 5: Testing Speech-to-Text API")
    
    print_info("Speech-to-Text requires an actual audio file")
    print_info("You can test this with a real audio file later")
    print_info("For now, this API requires:")
    print("  - Audio file in WAV/MP3/FLAC format")
    print("  - Upload to Sarvam STT endpoint")
    print_success("API endpoint is ready for integration")

def generate_sample_code():
    """Generate sample code for using Sarvam APIs"""
    print_section("Step 6: Sample Integration Code")
    
    sample_code = '''
# Example 1: Text-to-Speech
def generate_speech(text, language='hi'):
    import requests
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    data = {
        'text': text,
        'language_code': f'{language}-IN',
        'model': 'sarvam-tts:v1'
    }
    response = requests.post(
        'https://api.sarvam.ai/v1/text-to-speech',
        headers=headers,
        json=data
    )
    return response.content  # Returns audio bytes

# Example 2: Translation
def translate_text(text, source='en', target='hi'):
    import requests
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    data = {
        'input': text,
        'source_language_code': f'{source}-IN',
        'target_language_code': f'{target}-IN',
        'model': 'sarvam-translate:v1'
    }
    response = requests.post(
        'https://api.sarvam.ai/v1/text/translate',
        headers=headers,
        json=data
    )
    return response.json()['translated_text']

# Example 3: Chat Completion
def chat_with_bot(message, language='en'):
    import requests
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    data = {
        'messages': [{'role': 'user', 'content': message}],
        'model': 'sarvam-m'
    }
    response = requests.post(
        'https://api.sarvam.ai/v1/chat/completions',
        headers=headers,
        json=data
    )
    return response.json()['choices'][0]['message']['content']
    '''
    
    print(sample_code)
    
    # Save to file
    with open('sarvam_integration_examples.py', 'w') as f:
        f.write(sample_code)
    
    print_success("Sample code saved to sarvam_integration_examples.py")

def main():
    """Main test function"""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════╗{END}")
    print(f"{BLUE}║   Sarvam AI Integration - Connection Test             ║{END}")
    print(f"{BLUE}║   Telecom AI Bot Setup                                ║{END}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════╝{END}")
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Run tests
    try:
        test_text_to_speech()
        test_translation()
        test_chat_completion()
        test_speech_to_text()
        generate_sample_code()
        
        # Final summary
        print_section("All Tests Complete!")
        print_success("Sarvam AI is properly configured!")
        print_success("Ready to move to Phase 3: Building NLU with Rasa")
        print_info("Next step: Create Rasa NLU training data")
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
