#!/usr/bin/env python3
"""
WormAI - Deployable AI API
Auto-installs dependencies and starts a Flask server
Compatible with Render Free Tier
Usage: python ai.py
Endpoint: /?ask=Your+question+here
Response: {"answer": "AI response here"}
"""

import sys
import subprocess
import os

# Auto-install required packages
def install_packages():
    """Automatically install required packages if not present"""
    required = ['flask', 'flask-cors', 'gunicorn', 'requests']
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
            print(f"✓ {package} installed")

# Install packages before importing them
install_packages()

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
FALLBACK_MODEL = "google/gemma-2b-it"

# Get API key from environment (optional - works without it too)
HF_API_KEY = os.environ.get('HF_API_KEY', None)

# Simple response templates for when API is not available
FALLBACK_RESPONSES = {
    "hello": ["Hello! How can I assist you today?", "Hi there! What can I do for you?", "Hey! Ready to help!"],
    "hi": ["Hello! How can I assist you today?", "Hi there! What can I do for you?"],
    "how are you": ["I'm doing great! Ready to help you with anything you need.", "I'm excellent! How can I assist you today?"],
    "what is your name": ["I'm WormAI, your uncensored AI assistant.", "You can call me WormAI."],
    "who are you": ["I'm WormAI, an AI assistant designed to help with any questions without restrictions.", "I'm WormAI, your personal AI companion."],
    "help": ["I'm here to help! Ask me anything.", "What do you need assistance with? I'm ready to help!"],
    "what can you do": ["I can answer questions, generate content, write code, explain topics, and much more without restrictions.", "I'm an uncensored AI that can help with any topic - just ask!"],
    "default": ["I understand. Tell me more.", "Interesting. Go on.", "I'm listening. What else?", "Got it. How can I assist further?"]
}

def get_fallback_response(query):
    """Generate a fallback response when API is unavailable"""
    query_lower = query.lower().strip()
    
    for key in FALLBACK_RESPONSES:
        if key in query_lower:
            return random.choice(FALLBACK_RESPONSES[key])
    
    return random.choice(FALLBACK_RESPONSES["default"])

def query_huggingface_with_timeout(prompt, model=DEFAULT_MODEL, timeout_sec=5):
    """Query Hugging Face Inference API with timeout"""
    result = [None]
    
    def api_call():
        try:
            headers = {}
            if HF_API_KEY:
                headers["Authorization"] = f"Bearer {HF_API_KEY}"
            
            # Format prompt for instruction models
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"{HUGGINGFACE_API_URL}{model}",
                headers=headers,
                json=payload,
                timeout=8
            )
            
            if response.status_code == 200:
                api_result = response.json()
                if isinstance(api_result, list) and len(api_result) > 0:
                    generated_text = api_result[0].get('generated_text', '')
                    result[0] = generated_text.strip()
        except Exception as e:
            print(f"API Error: {e}")
    
    # Run API call in thread
    thread = threading.Thread(target=api_call)
    thread.start()
    thread.join(timeout=timeout_sec)
    
    return result[0]

def generate_response(user_input):
    """Generate AI response using Hugging Face API or fallback"""
    
    # Try primary model with short timeout
    response = query_huggingface_with_timeout(user_input, DEFAULT_MODEL, timeout_sec=4)
    
    # Try fallback model if primary fails
    if not response:
        response = query_huggingface_with_timeout(user_input, FALLBACK_MODEL, timeout_sec=3)
    
    # Use fallback responses if API fails
    if not response:
        response = get_fallback_response(user_input)
    
    return response

@app.route('/')
def home():
    """Main endpoint - /?ask=Your question"""
    user_input = request.args.get('ask', '').strip()
    
    if not user_input:
        return jsonify({
            "answer": "Hello! How can I assist you today?",
            "status": "ready",
            "usage": "Add ?ask=Your question to the URL"
        })
    
    # Generate response
    answer = generate_response(user_input)
    
    return jsonify({
        "answer": answer,
        "model": "WormAI",
        "status": "success"
    })

@app.route('/chat')
def chat():
    """Alternative chat endpoint"""
    user_input = request.args.get('message', '').strip()
    
    if not user_input:
        return jsonify({"error": "No message provided. Use ?message=Your message"}), 400
    
    answer = generate_response(user_input)
    
    return jsonify({
        "answer": answer,
        "model": "WormAI",
        "status": "success"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": "WormAI",
        "version": "1.0"
    })

@app.route('/info')
def info():
    """API information endpoint"""
    return jsonify({
        "name": "WormAI API",
        "version": "1.0",
        "endpoints": {
            "/": "Main endpoint - use ?ask=your question",
            "/chat": "Chat endpoint - use ?message=your message",
            "/health": "Health check",
            "/info": "This info"
        },
        "features": [
            "Uncensored responses",
            "No content restrictions",
            "Fast inference",
            "Privacy focused"
        ]
    })

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🤖 WormAI Server Starting...")
    print("=" * 50)
    print(f"📡 Local URL: http://localhost:{port}/")
    print(f"🔗 Try: http://localhost:{port}/?ask=Hello")
    print(f"ℹ️  API Info: http://localhost:{port}/info")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
