import streamlit as st
from tutor_backend_multilingual import AITextbookTutorMultilingualBackend
import os

# Language configurations
LANGUAGES = {
    'english': {
        'name': 'English',
        'flag': '🇺🇸',
        'title': '🤖 AI Textbook Tutor (Offline Mode)',
        'subtitle': 'Ask questions about your textbooks and get intelligent explanations - Running completely offline!',
        'loading': 'Loading Offline AI Tutor...',
        'no_textbooks': '📚 No textbooks available. Please contact your instructor to upload textbooks using the admin interface.',
        'system_unavailable': '⚠️ AI system not available. You can still search textbook content, but responses will be basic.',
        'system_offline_mode': '🔄 Running in offline mode - Basic textbook search available',
        'select_subjects': '📚 Select Subjects',
        'choose_textbooks': 'Choose textbooks to search in:',
        'textbooks_help': 'Select which textbooks to search for answers',
        'searching_in': 'Searching in',
        'textbook_s': 'textbook(s)',
        'pages': 'pages',
        'voice_input': '🎤 Voice Input (Offline)',
        'record_question': 'Record your question in English (processed offline)',
        'record_help': 'Click the record button and speak your question - all processing happens locally',
        'transcribing': 'Converting voice to text offline...',
        'you_said': 'You said:',
        'recognition_failed': 'Offline voice recognition failed. Please try typing your question.',
        'sources_from': '📚 Sources from textbooks',
        'chat_placeholder': 'Ask me anything about your textbooks...',
        'searching_response': 'Searching textbooks offline and generating response...',
        'clear_chat': '🗑️ Clear Chat',
        'how_to_use': 'ℹ️ How to Use (Offline Mode)',
        'voice_instructions': '''
        **Using Voice Input (Offline):**
        1. Click the record button under "Voice Input" in the sidebar
        2. Speak your question clearly in English
        3. Voice is processed completely offline on your device
        4. Transcribed text will appear automatically
        
        **Using Text Input:**
        1. Type your question in English in the chat box below
        2. Press Enter or click the send button
        3. All processing happens offline
        
        **Example Questions:**
        - Why are mountains cold?
        - Explain photosynthesis  
        - What causes earthquakes?
        
        **Note:** This system runs completely offline for privacy and reliability!
        '''
    },
    'telugu': {
        'name': 'తెలుగు',
        'flag': '🇮🇳',
        'title': '🤖 తెలుగు AI పాఠ్యపుస్తక ఉపాధ్యాయి (ఆఫ్‌లైన్)',
        'subtitle': 'మీ పాఠ్యపుస్తకాల గురించి ప్రశ్నలు అడగండి - పూర్తిగా ఆఫ్‌లైన్‌లో పనిచేస్తుంది!',
        'loading': 'ఆఫ్‌లైన్ AI ఉపాధ్యాయిని లోడ్ చేస్తోంది...',
        'no_textbooks': '📚 పాఠ్యపుస్తకాలు అందుబాటులో లేవు. దయచేసి అడ్మిన్ ఇంటర్‌ఫేస్ ఉపయోగించి పాఠ్యపుస్తకాలను అప్‌లోడ్ చేయమని మీ ఉపాధ్యాయుడిని అడగండి.',
        'system_unavailable': '⚠️ AI సిస్టమ్ అందుబాటులో లేదు. మీరు ఇప్పటికీ పాఠ్యపుస్తక కంటెంట్‌ను శోధించవచ్చు, కానీ ప్రతిస్పందనలు ప్రాథమికంగా ఉంటాయి.',
        'system_offline_mode': '🔄 ఆఫ్‌లైన్ మోడ్‌లో రన్ అవుతోంది - ప్రాథమిక పాఠ్యపుస్తక శోధన అందుబాటులో ఉంది',
        'select_subjects': '📚 విષయాలను ఎంచుకోండి',
        'choose_textbooks': 'శోధించడానికి పాఠ్యపుస్తకాలను ఎంచుకోండి:',
        'textbooks_help': 'సమాధానాల కోసం ఏ పాఠ్యపుస్తకాలను శోధించాలో ఎంచుకోండి',
        'searching_in': 'శోధిస్తోంది',
        'textbook_s': 'పాఠ్యపుస్తక(లు)లో',
        'pages': 'పేజీలు',
        'voice_input': '🎤 వాయిస్ ఇన్‌పుట్ (ఆఫ్‌లైన్)',
        'record_question': 'తెలుగులో మీ ప్రశ్నను రికార్డ్ చేయండి (ఆఫ్‌లైన్‌లో ప్రాసెస్ అవుతుంది)',
        'record_help': 'రికార్డ్ బటన్‌ను నొక్కి మీ ప్రశ్నను చెప్పండి - అన్ని ప్రాసెసింగ్ స్థానికంగా జరుగుతుంది',
        'transcribing': 'వాయిస్‌ను టెక్స్ట్‌గా ఆఫ్‌లైన్‌లో మారుస్తోంది...',
        'you_said': 'మీరు చెప్పినది:',
        'recognition_failed': 'ఆఫ్‌లైన్ వాయిస్ గుర్తింపు విఫలమైంది. దయచేసి మీ ప్రశ్నను టైప్ చేయండి.',
        'sources_from': '📚 పాఠ్యపుస్తకాల నుండి మూలాలు',
        'chat_placeholder': 'మీ పాఠ్యపుస్తకాల గురించి ఏదైనా అడగండి...',
        'searching_response': 'పాఠ్యపుస్తకాలను ఆఫ్‌లైన్‌లో శోధిస్తోంది మరియు ప్రతిస్పందనను రూపొందిస్తోంది...',
        'clear_chat': '🗑️ చాట్ క్లియర్ చేయండి',
        'how_to_use': 'ℹ️ ఎలా ఉపయోగించాలి (ఆఫ్‌లైన్ మోడ్)',
        'voice_instructions': '''
        **వాయిస్ ఇన్‌పుట్ ఉపయోగించడం (ఆఫ్‌లైన్):**
        1. సైడ్‌బార్‌లో "వాయిస్ ఇన్‌పుట్" కింద రికార్డ్ బటన్‌ను క్లిక్ చేయండి
        2. తెలుగులో మీ ప్రశ్నను స్పష్టంగా చెప్పండి
        3. వాయిస్ పూర్తిగా మీ పరికరంలో ఆఫ్‌లైన్‌లో ప్రాసెస్ అవుతుంది
        4. ట్రాన్స్‌క్రైబ్ చేసిన టెక్స్ట్ ఆటోమేటిక్‌గా కనిపిస్తుంది
        
        **టెక్స్ట్ ఇన్‌పుట్ ఉపయోగించడం:**
        1. దిగువ చాట్ బాక్స్‌లో తెలుగులో మీ ప్రశ్నను టైప్ చేయండి
        2. Enter నొక్కండి లేదా పంపు బటన్‌ను క్లిక్ చేయండి
        3. అన్ని ప్రాసెసింగ్ ఆఫ్‌లైన్‌లో జరుగుతుంది
        
        **ఉదాహరణ ప్రశ్నలు:**
        - హిమాలయాలు ఎందుకు చల్లగా ఉంటాయి?
        - గ్రేటర్ హిమాలయాలను వివరించండి
        - పర్వత నిర్మాణానికి కారణాలు ఏమిటి?
        
        **గమనిక:** ఈ సిస్టమ్ గోప్యత మరియు విశ్వసనీయత కోసం పూర్తిగా ఆఫ్‌లైన్‌లో పనిచేస్తుంది!
        '''
    }
}

def main():
    # Language selection at startup
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = None
    
    if st.session_state.selected_language is None:
        show_language_selection()
        return
    
    # Get current language config
    lang_config = LANGUAGES[st.session_state.selected_language]
    
    # Set page config
    st.set_page_config(
        page_title=lang_config['title'],
        page_icon="🤖",
        layout="wide"
    )
    
    # Main app interface
    show_main_interface(lang_config)

def show_language_selection():
    """Display language selection screen"""
    st.set_page_config(
        page_title="Language Selection - AI Textbook Tutor (Offline)",
        page_icon="🌍",
        layout="centered"
    )
    
    st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
    st.title("🌍 Select Your Language")
    st.markdown("### Choose your preferred language to continue")
    st.markdown("###  భాష ఎంచుకోండి")
    st.success("🔒 **Completely Offline System** - Your data never leaves this device!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        # English button
        if st.button(
            f"🇺🇸 **English**\nContinue in English (Offline Mode)", 
            key="english_btn",
            help="Click to use the app in English - runs completely offline",
            use_container_width=True
        ):
            st.session_state.selected_language = 'english'
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Telugu button  
        if st.button(
            f"🇮🇳 **తెలుగు (Telugu)**\nతెలుగులో కొనసాగించండి (ఆఫ్‌లైన్)", 
            key="telugu_btn",
            help="తెలుగులో యాప్ ఉపయోగించడానికి క్లిక్ చేయండి - పూర్తిగా ఆఫ్‌లైన్‌లో పనిచేస్తుంది",
            use_container_width=True
        ):
            st.session_state.selected_language = 'telugu'
            st.rerun()
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 14px;'>"
            "🔒 Privacy First: All processing happens on your device offline"
            "<br>🚀 Select your language above to start learning with offline AI"
            "</div>", 
            unsafe_allow_html=True
        )

def show_main_interface(lang_config):
    """Display the main app interface with offline status"""
    
    # Add offline status indicator
    st.sidebar.success("🔒 **OFFLINE MODE**\nAll processing on device")
    
    # Add language switcher in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button(f"🌍 Change Language", key="change_lang"):
            st.session_state.selected_language = None
            st.rerun()
        st.markdown("---")
    
    # Title and subtitle with offline indicator
    st.title(lang_config['title'])
    st.markdown(lang_config['subtitle'])
    
    # Enhanced initialization with better error handling
    if 'tutor' not in st.session_state or st.session_state.get('tutor_language') != st.session_state.selected_language:
        with st.spinner(lang_config['loading']):
            try:
                st.session_state.tutor = AITextbookTutorMultilingualBackend(st.session_state.selected_language)
                st.session_state.tutor_language = st.session_state.selected_language
                st.success("✅ Offline AI system loaded successfully!")
            except Exception as e:
                st.error(f"❌ Error loading offline system: {e}")
                st.info("💡 Make sure all offline models are downloaded. Run the setup script first.")
                return
    
    tutor = st.session_state.tutor
    
    # Enhanced debug info with more details
    with st.expander("🔧 System Debug Info", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Backend Status:**")
            st.write(f"- Language: {st.session_state.selected_language}")
            st.write(f"- ASR Available: {getattr(tutor, 'asr_available', 'Not Set')}")
            st.write(f"- Whisper Model: {hasattr(tutor, 'whisper_model')}")
            st.write(f"- LLM Available: {getattr(tutor, 'llm_available', 'Not Set')}")
            if hasattr(tutor, 'model_name'):
                st.write(f"- AI Model: {tutor.model_name}")
            st.write(f"- TTS Available: {getattr(tutor, 'tts_available', 'Not Set')}")
        
        with col2:
            st.write("**Data Status:**")
            st.write(f"- Textbooks: {len(tutor.textbooks)}")
            st.write(f"- Vector Store: {tutor.vectorstore is not None}")
            st.write(f"- Embeddings: {hasattr(tutor, 'embeddings')}")
            
            # Show textbook files with more details
            if os.path.exists("textbook_metadata.json"):
                st.write("- Metadata File: ✅ Found")
                # Show actual textbook list
                if tutor.textbooks:
                    st.write("**Available Textbooks:**")
                    for subject, info in tutor.textbooks.items():
                        pages = info.get('pages', 'Unknown')
                        chunks = info.get('chunks', 'Unknown')
                        st.write(f"  • {subject}: {pages} pages, {chunks} chunks")
            else:
                st.write("- Metadata File: ❌ Missing")
    
    # Check system status with more detailed messaging
    if not tutor.textbooks:
        st.warning(lang_config['no_textbooks'])
        st.info("💡 **For Teachers**: Use the admin interface to upload textbooks offline")
        st.info("🧪 **Testing Mode**: You can still test voice input and general AI chat")

    # Show system status with enhanced information
    col1, col2 = st.columns(2)
    with col1:
        if tutor.llm_available:
            st.success("🤖 **AI Mode**: Intelligent responses available")
            if hasattr(tutor, 'model_name'):
                st.info(f"Using model: {tutor.model_name}")
        else:
            st.warning(lang_config['system_offline_mode'])
            st.info("💡 **Basic Mode**: Textbook search without AI enhancement")
    
    with col2:
        if tutor.textbooks:
            total_pages = sum(info.get('pages', 0) for info in tutor.textbooks.values())
            st.info(f"📚 **{len(tutor.textbooks)} textbooks** ({total_pages} total pages) loaded offline")
        else:
            st.warning("📚 **No textbooks** loaded")
    
    # Sidebar for subject selection with enhanced info
    st.sidebar.header(lang_config['select_subjects'])
    available_subjects = list(tutor.textbooks.keys())
    
    if available_subjects:
        selected_subjects = st.sidebar.multiselect(
            lang_config['choose_textbooks'],
            available_subjects,
            default=available_subjects,
            help=lang_config['textbooks_help']
        )
        
        # Display selected subjects info with page counts
        if selected_subjects:
            st.sidebar.success(f"✅ {lang_config['searching_in']} {len(selected_subjects)} {lang_config['textbook_s']}")
            for subject in selected_subjects:
                pages = tutor.textbooks[subject].get('pages', 0)
                chunks = tutor.textbooks[subject].get('chunks', 0)
                st.sidebar.info(f"📖 {subject}: {pages} {lang_config['pages']}, {chunks} chunks")
    else:
        selected_subjects = []
        st.sidebar.warning("No textbooks available for selection")

    # Voice input section (only for supported languages)
    transcribed_text = None
    if st.session_state.selected_language in ['telugu']:
        st.sidebar.header(lang_config['voice_input'])
        
        asr_available = hasattr(tutor, 'asr_available') and tutor.asr_available
        
        if asr_available:
            st.sidebar.success("🎤 Voice recognition ready")
            
            audio_input = st.sidebar.audio_input(
                lang_config['record_question'],
                help=lang_config['record_help']
            )
            
            if audio_input is not None:
                transcription_placeholder = st.sidebar.empty()
                transcription_placeholder.info(f"🔄 {lang_config['transcribing']}")
                
                try:
                    transcribed_text = tutor.transcribe_audio(audio_input)
                    
                    if transcribed_text and not transcribed_text.startswith("❌"):
                        transcription_placeholder.success(f"✅ {lang_config['you_said']} {transcribed_text}")
                        st.session_state.pending_voice_input = transcribed_text
                    else:
                        transcription_placeholder.error(f"❌ {lang_config['recognition_failed']}")
                except Exception as e:
                    transcription_placeholder.error(f"❌ Transcription error: {str(e)}")
        else:
            st.sidebar.warning("🎤 Voice input not available")
            if hasattr(tutor, 'asr_error') and tutor.asr_error:
                st.sidebar.error(f"❌ {tutor.asr_error}")
            
            if st.sidebar.button("🔄 Retry Voice Setup", key="retry_asr"):
                with st.spinner("Retrying voice model setup..."):
                    tutor.setup_telugu_asr_offline()
                    st.rerun()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history with enhanced source display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Display the text response
            st.markdown(message["content"])
            
            # Display audio player for assistant messages
            if message["role"] == "assistant" and "audio_data" in message:
                st.audio(message["audio_data"], format="audio/mp3")
                st.caption("🔊 Audio generated offline")
            
            # Enhanced sources display with better formatting
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander(f"{lang_config['sources_from']} ({len(message['sources'])} sources)", expanded=False):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}.** {source}")
                        
                st.success(f"📄 Information found from {len(message['sources'])} textbook sources")

    # Handle voice input if available
    prompt = None
    if st.session_state.get('pending_voice_input'):
        st.info(f"🎤 {lang_config['you_said']} {st.session_state.pending_voice_input}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Send Voice Message", key="send_voice", type="primary"):
                prompt = st.session_state.pending_voice_input
                del st.session_state.pending_voice_input

    # Regular chat input
    if not st.session_state.get('pending_voice_input') and not prompt:
        prompt = st.chat_input(lang_config['chat_placeholder'])

    # Process the prompt with enhanced error handling and debugging
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response with debugging
        with st.chat_message("assistant"):
            with st.spinner(lang_config['searching_response']):
                try:
                    # Add debug info
                    st.caption(f"🔍 Searching in {len(selected_subjects)} subjects...")
                    
                    response, sources = tutor.get_response(prompt, selected_subjects)
                    
                    # Debug: Show what was returned
                    st.caption(f"📊 Found {len(sources)} sources" if sources else "📊 No sources found")
                    
                except Exception as e:
                    response = f"❌ Offline processing error: {str(e)}"
                    sources = []
                    st.error(f"Debug: Error in get_response: {str(e)}")

            # Display text response
            st.markdown(response)
            st.caption("🔒 Response generated offline")

            # Enhanced sources display - IMMEDIATELY after response
            if sources:
                st.success(f"📄 **Found information from {len(sources)} textbook sources**")
                
                with st.expander(f"{lang_config['sources_from']} ({len(sources)} sources)", expanded=True):
                    for i, source in enumerate(sources, 1):
                        st.write(f"**{i}.** 📖 {source}")
            else:
                st.info("ℹ️ No specific textbook sources found for this query")

            # Generate audio if available
            audio_data = None
            try:
                if hasattr(tutor, 'speak_text'):
                    audio_data = tutor.speak_text(response)
                    if audio_data:
                        st.audio(audio_data, format="audio/mp3", autoplay=False)
                        st.caption("🔊 Audio generated offline using local TTS")
            except Exception as e:
                st.caption(f"🔇 Audio generation unavailable: {str(e)}")

        # Add assistant response to chat history with sources
        message_data = {
            "role": "assistant", 
            "content": response,
            "sources": sources  # Make sure sources are always included
        }
        if audio_data:
            message_data["audio_data"] = audio_data
        
        st.session_state.messages.append(message_data)
        
        # Clean up
        if 'pending_voice_input' in st.session_state:
            del st.session_state.pending_voice_input
        
        st.rerun()

    # Clear chat button
    if st.sidebar.button(lang_config['clear_chat']):
        st.session_state.messages = []
        if 'pending_voice_input' in st.session_state:
            del st.session_state.pending_voice_input
        st.rerun()

    # Usage instructions
    with st.expander(lang_config['how_to_use']):
        st.markdown(lang_config['voice_instructions'])

if __name__ == "__main__":
    main()
