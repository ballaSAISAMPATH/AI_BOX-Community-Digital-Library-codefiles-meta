import os
import sys
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import pyttsx3

def download_models():
    print("📥 Downloading models for complete offline operation...")
    
    # 1. Download embeddings model
    print("📥 Downloading sentence transformer...")
    os.makedirs("./models/embeddings", exist_ok=True)
    embeddings = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="./models/embeddings"
    )
    
    # 2. Download Telugu Whisper model
    print("📥 Downloading Telugu Whisper model...")
    os.makedirs("./models/whisper", exist_ok=True)
    asr = pipeline(
        "automatic-speech-recognition",
        model="vasista22/whisper-telugu-base",
        cache_dir="./models/whisper"
    )
    
    # 3. Test offline TTS
    print("🔊 Testing offline TTS...")
    tts = pyttsx3.init()
    print("✅ Offline TTS ready!")
    
    print("✅ All models downloaded! System ready for offline operation.")

if __name__ == "__main__":
    download_models()
