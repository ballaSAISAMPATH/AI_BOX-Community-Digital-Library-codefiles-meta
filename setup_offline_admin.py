#!/usr/bin/env python3
"""
Offline Setup Script for AI Textbook Admin
Run this once with internet to download all required models
"""

import os
import sys
from sentence_transformers import SentenceTransformer
from langdetect import detect
import requests

def create_directories():
    """Create necessary directories"""
    directories = [
        "./models",
        "./models/embeddings", 
        "./ai_tutor_db",
        "./temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_embedding_model():
    """Download sentence transformer model"""
    print("📥 Downloading sentence transformer model...")
    try:
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder="./models/embeddings"
        )
        print("✅ Sentence transformer model downloaded!")
        return True
    except Exception as e:
        print(f"❌ Failed to download embedding model: {e}")
        return False

def test_language_detection():
    """Test offline language detection"""
    print("🔍 Testing offline language detection...")
    try:
        # Test English
        english_result = detect("This is a test sentence in English")
        print(f"✅ English detection: {english_result}")
        
        # Test basic functionality
        print("✅ Language detection ready!")
        return True
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed and has models"""
    print("🤖 Checking Ollama installation...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✅ Ollama ready with {len(models)} model(s)")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("⚠️ Ollama running but no models found")
                print("💡 Run: ollama pull llama3.2")
        else:
            print("⚠️ Ollama not responding")
    except:
        print("❌ Ollama not running")
        print("💡 Install Ollama from: https://ollama.ai")

def main():
    print("🚀 Setting up Offline AI Textbook Admin System...")
    print("="*50)
    
    success = True
    
    # Create directories
    create_directories()
    
    # Download models
    if not download_embedding_model():
        success = False
    
    # Test language detection
    if not test_language_detection():
        success = False
    
    # Check Ollama (optional)
    check_ollama()
    
    print("="*50)
    if success:
        print("✅ Offline setup completed successfully!")
        print("🚀 System ready for offline operation!")
    else:
        print("❌ Setup completed with errors")
        print("💡 Some features may not work offline")

if __name__ == "__main__":
    main()
