import os
import json
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langdetect import detect
import requests

warnings.filterwarnings('ignore')

class AITextbookAdminBackendOffline:
    def __init__(self):
        print("🚀 Initializing Offline Admin Backend...")
        self.textbooks = {}
        self.vectorstore = None
        self.setup_embeddings_offline()
        self.check_llama_offline()
        self.load_existing_data()
        print("✅ Offline Admin Backend Ready!")
    
    def setup_embeddings_offline(self):
        """Setup embeddings with offline mode"""
        print("🧠 Setting up offline embeddings...")
        try:
            # Create models directory if it doesn't exist
            os.makedirs("./models/embeddings", exist_ok=True)
            
            # Set offline environment variables
            os.environ['HF_HUB_OFFLINE'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '1'
            
            try:
                # Try to load in offline mode first
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu', 'local_files_only': True},
                    cache_folder="./models/embeddings"
                )
                print("✅ Offline embeddings loaded from cache!")
                
            except Exception as offline_error:
                print(f"⚠️ Offline mode failed: {offline_error}")
                print("💡 Models not downloaded yet. Please run download_models.py first!")
                
                # Ask user what to do
                print("\n🔧 SOLUTION:")
                print("1. Make sure you have internet connection")
                print("2. Run: python download_models.py")
                print("3. Then restart this application")
                
                raise Exception("Models not available offline. Run download_models.py first with internet connection.")
                
        except Exception as e:
            print(f"❌ Embeddings setup failed: {e}")
            raise e

    
    def check_llama_offline(self):
        """Check Ollama availability with offline fallback"""
        print("🤖 Checking local AI availability...")
        try:
            # This is localhost communication, not internet
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.llm_available = len(models) > 0
                if models:
                    model_names = [model['name'] for model in models]
                    if any('llama3.2' in name for name in model_names):
                        self.model_name = "llama3.2"
                    else:
                        self.model_name = model_names[0].split(':')[0]
                    print(f"✅ Local AI ready: {self.model_name}")
                else:
                    self.model_name = ""
                    self.llm_available = False
                    print("⚠️ Ollama running but no models found")
            else:
                self.llm_available = False
                print("⚠️ Ollama not responding properly")
        except requests.exceptions.ConnectionError:
            self.llm_available = False
            print("⚠️ Ollama not running - Admin functions will work without AI")
        except Exception as e:
            self.llm_available = False
            print(f"⚠️ Ollama check failed: {e} - Continuing without AI")
    
    def load_existing_data(self):
        """Load existing textbook metadata (fully offline)"""
        print("📂 Loading existing data...")
        if os.path.exists("textbook_metadata.json"):
            with open("textbook_metadata.json", 'r', encoding='utf-8') as f:
                self.textbooks = json.load(f)
            print(f"📚 Loaded metadata for {len(self.textbooks)} textbooks")
        
        # Load existing vectorstore (fully offline)
        if os.path.exists("./ai_tutor_db"):
            try:
                self.vectorstore = Chroma(
                    persist_directory="./ai_tutor_db",
                    embedding_function=self.embeddings
                )
                print("✅ Existing vector database loaded!")
            except Exception as e:
                print(f"⚠️ Could not load existing database: {e}")
                self.vectorstore = None
        else:
            print("📄 No existing database found - will create new one")
    
    def save_metadata(self):
        """Save textbook metadata to JSON file (fully offline)"""
        with open("textbook_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.textbooks, f, indent=2, ensure_ascii=False)
        print("💾 Metadata saved locally")
    
    def detect_pdf_language_offline(self, pdf_file):
        """Offline language detection from PDF content"""
        temp_path = "temp_detect.pdf"
        try:
            print("🔍 Detecting language offline...")
            # Save file temporarily
            with open(temp_path, "wb") as f:
                f.write(pdf_file.getvalue())
            
            # Extract text from first few pages (offline)
            loader = PyPDFLoader(temp_path)
            pages = loader.load()
            
            # Get sample text from first 3 pages
            sample_text = ""
            for i, page in enumerate(pages[:3]):
                if len(page.page_content.strip()) > 50:
                    sample_text += page.page_content[:1000] + " "
                    if len(sample_text) > 2000:
                        break
            
            if len(sample_text.strip()) < 50:
                print("⚠️ Not enough text for language detection")
                return "unknown", 0.0
            
            # Detect language (langdetect works offline after installation)
            detected_lang = detect(sample_text)
            
            # Map language codes to our supported languages
            language_map = {
                'te': 'telugu',
                'en': 'english',
                'hi': 'hindi'
            }
            
            detected_language = language_map.get(detected_lang, 'english')
            confidence = 0.85  # langdetect doesn't provide confidence scores
            
            print(f"✅ Detected language: {detected_language} ({confidence:.1%} confidence)")
            return detected_language, confidence
            
        except Exception as e:
            print(f"❌ Language detection failed: {e}")
            print("💡 Defaulting to English")
            return "english", 0.5  # Default fallback
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def add_textbook_offline(self, pdf_file, subject_name: str, language: str, auto_detected=False):
        """Add textbook with specified language (fully offline processing)"""
        temp_path = f"temp_{subject_name.replace(' ', '_')}.pdf"
        
        try:
            print(f"📖 Processing {subject_name} ({language}) offline...")
            
            # Save uploaded file temporarily
            with open(temp_path, "wb") as f:
                f.write(pdf_file.getvalue())
            
            # Load PDF (offline)
            loader = PyPDFLoader(temp_path)
            pages = loader.load()
            
            if not pages:
                return False, "❌ Could not read PDF file"
            
            print(f"📄 Loaded {len(pages)} pages")
            
            # Add metadata to each page
            for page in pages:
                page.metadata['subject'] = subject_name
                page.metadata['language'] = language
                page.metadata['auto_detected'] = auto_detected
            
            # Split text into chunks (offline)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            # Filter out pages with minimal content
            text_pages = [page for page in pages if len(page.page_content.strip()) > 100]
            
            if not text_pages:
                return False, "❌ No readable content found in PDF"
            
            chunks = text_splitter.split_documents(text_pages)
            print(f"✂️ Created {len(chunks)} chunks")
            
            # Store metadata
            self.textbooks[subject_name] = {
                'pages': len(text_pages),
                'chunks': len(chunks),
                'language': language,
                'status': 'processed',
                'auto_detected': auto_detected,
                'file_name': pdf_file.name,
                'processed_offline': True  # Mark as offline processed
            }
            
            # Add to vector store (offline)
            if self.vectorstore is None:
                print("🔍 Creating new offline vector database...")
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory="./ai_tutor_db"
                )
            else:
                print("📚 Adding to existing offline database...")
                self.vectorstore.add_documents(chunks)
            
            # Save metadata (offline)
            self.save_metadata()
            
            print(f"✅ {subject_name} processed offline successfully!")
            return True, f"✅ {subject_name} successfully processed offline! ({len(chunks)} chunks, {language})"
        
        except Exception as e:
            print(f"❌ Error processing {subject_name}: {str(e)}")
            return False, f"❌ Error processing {subject_name}: {str(e)}"
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def remove_textbook(self, subject_name: str):
        """Remove a textbook from the system (offline)"""
        if subject_name in self.textbooks:
            del self.textbooks[subject_name]
            self.save_metadata()
            print(f"🗑️ Removed {subject_name} from offline storage")
            # Note: Removing from vectorstore is complex, would need to rebuild
            return True, f"✅ {subject_name} removed from metadata"
        return False, f"❌ {subject_name} not found"
    
    def get_system_stats(self):
        """Get system statistics (fully offline)"""
        if not self.textbooks:
            return {
                'total_textbooks': 0,
                'total_pages': 0,
                'total_chunks': 0,
                'languages': {},
                'vectorstore_ready': False,
                'offline_mode': True
            }
        
        total_pages = sum(book['pages'] for book in self.textbooks.values())
        total_chunks = sum(book['chunks'] for book in self.textbooks.values())
        
        # Count by language
        language_count = {}
        for book in self.textbooks.values():
            lang = book['language']
            language_count[lang] = language_count.get(lang, 0) + 1
        
        return {
            'total_textbooks': len(self.textbooks),
            'total_pages': total_pages,
            'total_chunks': total_chunks,
            'languages': language_count,
            'vectorstore_ready': self.vectorstore is not None,
            'offline_mode': True,
            'ai_available': self.llm_available
        }

    # Wrapper methods for compatibility with existing admin_fixed.py
    def detect_pdf_language(self, pdf_file):
        return self.detect_pdf_language_offline(pdf_file)
    
    def add_textbook(self, pdf_file, subject_name: str, language: str, auto_detected=False):
        return self.add_textbook_offline(pdf_file, subject_name, language, auto_detected)
