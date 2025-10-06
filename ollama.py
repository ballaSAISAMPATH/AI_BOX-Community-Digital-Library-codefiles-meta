import os
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import requests
import json

warnings.filterwarnings('ignore')

class AITextbookTutor:
    def __init__(self):
        print("🤖 Starting AI Textbook Tutor with Llama 3.2")
        self.textbooks = {}
        self.vectorstore = None
        self.setup_embeddings()
        self.check_llama()
    
    def setup_embeddings(self):
        print("🧠 Setting up search engine...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    def check_llama(self):
        """Check if Llama 3.2 is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if any('llama3.2' in name for name in model_names):
                    print("✅ Llama 3.2 found and ready!")
                    self.llm_available = True
                    self.model_name = "llama3.2"
                else:
                    print("⚠️  Llama 3.2 not found, using available model")
                    self.llm_available = True if models else False
                    self.model_name = model_names[0].split(':')[0] if models else ""
            else:
                print("❌ Ollama not responding")
                self.llm_available = False
        except:
            print("❌ Ollama not running")
            self.llm_available = False
    
    def chat_with_llama(self, prompt: str, context: str = "") -> str:
        """Chat with local Llama 3.2"""
        if not self.llm_available:
            return "❌ AI not available. Make sure Ollama is running."
        
        full_prompt = f"""You are a helpful tutor explaining concepts from a student's textbook. Be clear, educational, and encouraging.

Textbook Context:
{context}

Student Question: {prompt}

Provide a clear, friendly explanation. Use simple language and examples when helpful."""
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"❌ AI Error: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "❌ AI is thinking too long. Try a simpler question."
        except Exception as e:
            return f"❌ AI Error: {str(e)}"
    
    def add_textbook(self, pdf_path: str, subject_name: str):
        """Add textbook to knowledge base"""
        print(f"\n📖 Adding {subject_name}: {pdf_path}")
        
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        print(f"📄 Loaded {len(pages)} pages")
        
        for page in pages:
            page.metadata['subject'] = subject_name
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        text_pages = [page for page in pages if len(page.page_content.strip()) > 100]
        chunks = text_splitter.split_documents(text_pages)
        print(f"✂️ Created {len(chunks)} chunks")
        
        self.textbooks[subject_name] = len(text_pages)
        
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./ai_tutor_db"
            )
        else:
            self.vectorstore.add_documents(chunks)
        
        print(f"✅ {subject_name} added to AI tutor!")
    
    def ai_explain(self, question: str):
        """Get AI explanation with textbook context"""
        if not self.vectorstore:
            print("❌ No textbooks loaded!")
            return
        
        print(f"\n🤖 Let me explain: '{question}'")
        print("🔍 Finding relevant information in your textbook...")
        
        # Get context from textbook
        relevant_docs = self.vectorstore.similarity_search(question, k=3)
        
        if not relevant_docs:
            # Ask AI without textbook context
            ai_response = self.chat_with_llama(question, "No specific textbook information found.")
        else:
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            ai_response = self.chat_with_llama(question, context)
        
        print("\n" + "="*70)
        print("🤖 **AI TUTOR EXPLANATION:**")
        print("="*70)
        print(ai_response)
        
        if relevant_docs:
            print(f"\n📚 **Information from your textbook:**")
            for i, doc in enumerate(relevant_docs, 1):
                page_num = doc.metadata.get('page', 'Unknown')
                subject = doc.metadata.get('subject', 'Unknown')
                print(f"  {i}. {subject} - Page {page_num}")
        
        print("="*70)
    
    def interactive_chat(self):
        """Interactive AI chat about textbooks"""
        print("\n" + "="*70)
        print("🤖 AI TUTOR CHAT - Ask me anything about your textbooks!")
        print("Examples:")
        print("  • 'Why are Himalayas cold?'")
        print("  • 'Explain Greater Himalayas'")
        print("  • 'What causes mountain formation?'")
        print("Type 'quit' to exit")
        print("="*70)
        
        while True:
            question = input(f"\n💬 You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("🤖 Happy learning! Keep asking questions!")
                break
            
            elif question:
                self.ai_explain(question)
            else:
                print("🤖 Ask me anything about your textbook!")
    
    def main_menu(self):
        """Main menu"""
        print("\n" + "="*70)
        print("🤖 AI TEXTBOOK TUTOR with Llama 3.2")
        print("Commands:")
        print("  • 'chat' - Start AI conversation")
        print("  • 'add textbook' - Add a new textbook")
        print("  • 'list' - Show loaded textbooks")
        print("  • 'quit' - Exit")
        print("="*70)
        
        if not self.llm_available:
            print("⚠️  AI chat not available - check Ollama is running")
        
        while True:
            command = input(f"\n{'🤖' if self.llm_available else '📚'} Command: ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Keep learning!")
                break
            
            elif command == 'chat' and self.llm_available:
                self.interactive_chat()
            
            elif command == 'add textbook':
                pdf_path = input("📁 PDF filename: ").strip().strip('"')
                if os.path.exists(pdf_path):
                    subject = input("📚 Subject name: ").strip()
                    if not subject:
                        subject = os.path.splitext(pdf_path)[0]
                    self.add_textbook(pdf_path, subject)
                else:
                    print(f"❌ File not found: {pdf_path}")
            
            elif command == 'list':
                if self.textbooks:
                    print("\n📚 Your Textbooks:")
                    for subject, pages in self.textbooks.items():
                        print(f"  • {subject}: {pages} pages")
                else:
                    print("❌ No textbooks loaded")
            
            else:
                print("Available: chat, add textbook, list, quit")

def main():
    print("🚀 Starting AI Textbook Tutor...")
    tutor = AITextbookTutor()
    
    # Quick textbook setup
    pdf_path = input("\n📁 Enter your textbook PDF filename (or press Enter to skip): ").strip().strip('"')
    
    if pdf_path and os.path.exists(pdf_path):
        subject = input("📚 Subject name: ").strip()
        if not subject:
            subject = os.path.splitext(pdf_path)[0]
        tutor.add_textbook(pdf_path, subject)
    
    tutor.main_menu()

if __name__ == "__main__":
    main()
