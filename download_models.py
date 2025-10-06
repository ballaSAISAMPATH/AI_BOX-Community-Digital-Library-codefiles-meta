# download_models.py
import os
from langchain_community.embeddings import HuggingFaceEmbeddings

def download_all_models():
    """Download all models for offline use"""
    print("📥 Downloading models for offline use...")
    print("🌐 Make sure you have internet connection!")
    
    # Create directories
    os.makedirs("./models/embeddings", exist_ok=True)
    
    # Download embedding model
    print("📥 Downloading embedding model...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            cache_folder="./models/embeddings"
        )
        
        # Test the model to ensure it's fully downloaded
        test_result = embeddings.embed_query("test")
        print(f"✅ Embedding model downloaded and tested! (Vector size: {len(test_result)})")
        
    except Exception as e:
        print(f"❌ Failed to download embedding model: {e}")
        return False
    
    print("🎉 All models downloaded successfully!")
    print("🔒 You can now disconnect from internet and run offline!")
    return True

if __name__ == "__main__":
    success = download_all_models()
    if success:
        print("\n✅ Setup complete! Now you can run your app offline.")
    else:
        print("\n❌ Setup failed. Please check your internet connection.")
