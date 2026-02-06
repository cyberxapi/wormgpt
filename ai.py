#!/usr/bin/env python3
"""
WormAI - Real Open Source AI Model API
Uses Hugging Face Inference API with REAL models (Mistral-7B, Llama, etc.)
Compatible with Render Free Tier
Usage: python ai.py
Endpoint: /?ask=Your+question+here
Response: {"answer":"Real AI generated response"}
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
import time

app = Flask(__name__)
CORS(app)

# Hugging Face Inference API - REAL AI MODELS
# These are actual open-source models hosted on Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/"

# List of REAL models to try (in order of preference)
MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.2",  # Mistral 7B - very capable
    "meta-llama/Llama-2-7b-chat-hf",        # Meta's Llama 2 7B
    "google/gemma-2b-it",                   # Google's Gemma 2B
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",   # TinyLlama 1.1B
]

# Optional: Get API key from environment for better rate limits
# Get free key at: https://huggingface.co/settings/tokens
HF_API_KEY = os.environ.get('HF_API_KEY', None)

def query_model(prompt, model_name, max_retries=2):
    """Query a REAL AI model via Hugging Face Inference API"""
    headers = {"Content-Type": "application/json"}
    if HF_API_KEY:
        headers["Authorization"] = f"Bearer {HF_API_KEY}"
    
    # Format prompt based on model type
    if "mistral" in model_name.lower() or "llama" in model_name.lower():
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
    elif "gemma" in model_name.lower():
        formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
    else:
        formatted_prompt = f"User: {prompt}\nAssistant:"
    
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{HF_API_URL}{model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '').strip()
                    # Clean up the response
                    generated_text = generated_text.replace("<s>", "").replace("</s>", "")
                    generated_text = generated_text.replace("[INST]", "").replace("[/INST]", "")
                    generated_text = generated_text.strip()
                    return generated_text, model_name
                    
            elif response.status_code == 503:
                # Model is loading, wait and retry
                time.sleep(2)
                continue
                
        except Exception as e:
            print(f"Error querying {model_name}: {e}")
            continue
    
    return None, model_name

def generate_ai_response(user_input):
    """Generate response using REAL AI models"""
    
    # Try each model in order
    for model_name in MODELS:
        print(f"Trying model: {model_name}")
        response, used_model = query_model(user_input, model_name)
        
        if response:
            print(f"✓ Got response from {used_model}")
            return response, used_model
    
    # If all models fail, return error
    return None, None

@app.route('/')
def home():
    """Main endpoint - /?ask=Your question"""
    user_input = request.args.get('ask', '').strip()
    
    if not user_input:
        return jsonify({
            "answer": "Hello! I'm powered by real AI models (Mistral-7B, Llama-2, etc.). How can I assist you today?",
            "status": "ready",
            "type": "real_ai",
            "usage": "Add ?ask=Your question to the URL"
        })
    
    # Generate REAL AI response
    answer, model_used = generate_ai_response(user_input)
    
    if answer:
        return jsonify({
            "answer": answer,
            "model": model_used,
            "status": "success",
            "type": "real_ai"
        })
    else:
        return jsonify({
            "answer": "I'm having trouble connecting to the AI models. Please try again in a moment.",
            "status": "error",
            "type": "real_ai"
        }), 503

@app.route('/chat')
def chat():
    """Alternative chat endpoint"""
    user_input = request.args.get('message', '').strip()
    
    if not user_input:
        return jsonify({"error": "No message provided. Use ?message=Your message"}), 400
    
    answer, model_used = generate_ai_response(user_input)
    
    if answer:
        return jsonify({
            "answer": answer,
            "model": model_used,
            "status": "success",
            "type": "real_ai"
        })
    else:
        return jsonify({
            "answer": "I'm having trouble connecting to the AI models. Please try again.",
            "status": "error",
            "type": "real_ai"
        }), 503

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "models_available": MODELS,
        "version": "2.0",
        "type": "real_ai"
    })

@app.route('/info')
def info():
    """API information endpoint"""
    return jsonify({
        "name": "WormAI API - Real AI Models",
        "version": "2.0",
        "type": "real_ai",
        "models": MODELS,
        "description": "Uses REAL open-source AI models via Hugging Face Inference API",
        "endpoints": {
            "/": "Main endpoint - use ?ask=your question",
            "/chat": "Chat endpoint - use ?message=your message",
            "/health": "Health check",
            "/info": "This info"
        },
        "features": [
            "Real AI models (Mistral-7B, Llama-2, Gemma-2B, TinyLlama)",
            "No API key required (but recommended for better limits)",
            "Fast inference via Hugging Face",
            "Privacy focused"
        ],
        "get_api_key": "https://huggingface.co/settings/tokens (optional, free)"
    })

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("🤖 WormAI Server - REAL AI Models")
    print("=" * 60)
    print(f"📡 Local URL: http://localhost:{port}/")
    print(f"🔗 Try: http://localhost:{port}/?ask=Hello")
    print(f"ℹ️  API Info: http://localhost:{port}/info")
    print("=" * 60)
    print("Models available:")
    for m in MODELS:
        print(f"  • {m}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
