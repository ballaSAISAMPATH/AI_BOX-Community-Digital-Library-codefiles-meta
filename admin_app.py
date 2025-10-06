import streamlit as st
from admin_backend import AITextbookAdminBackendOffline
import pandas as pd

st.set_page_config(
    page_title="📚 AI Textbook Tutor - Admin Panel",
    page_icon="🎓",
    layout="wide"
)

# Language options
LANGUAGE_OPTIONS = {
    'english': {'name': 'English', 'flag': '🇺🇸'},
    'telugu': {'name': 'Telugu (తెలుగు)', 'flag': '🇮🇳'}
}

def main():
    st.title("🎓 AI Textbook Tutor - Admin Panel")
    st.markdown("**Upload and manage textbooks for the AI tutoring system**")
    
    # Initialize backend
    if 'admin' not in st.session_state:
        with st.spinner("🚀 Initializing Admin Backend..."):
            st.session_state.admin = AITextbookAdminBackendOffline()
    
    admin = st.session_state.admin
    
    # Display system status
    stats = admin.get_system_stats()
    
    st.header("📊 System Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if admin.llm_available:
            st.success(f"🤖 AI Ready\n({admin.model_name})")
        else:
            st.error("❌ Ollama\nNot Running")
    
    with col2:
        st.metric("📚 Textbooks", stats['total_textbooks'])
    
    with col3:
        st.metric("📄 Pages", stats['total_pages'])
    
    with col4:
        st.metric("🔍 Database", "Ready" if stats['vectorstore_ready'] else "Empty")
    
    # Language breakdown
    if stats['languages']:
        st.markdown("**Languages:**")
        lang_cols = st.columns(len(stats['languages']))
        for i, (lang, count) in enumerate(stats['languages'].items()):
            flag = LANGUAGE_OPTIONS.get(lang, {}).get('flag', '📖')
            name = LANGUAGE_OPTIONS.get(lang, {}).get('name', lang.title())
            lang_cols[i].info(f"{flag} {name}: {count}")
    
    st.divider()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📁 Upload Textbooks", "📚 Manage Textbooks", "⚙️ Settings"])
    
    with tab1:
        show_upload_interface(admin)
    
    with tab2:
        show_manage_interface(admin)
    
    with tab3:
        show_settings_interface(admin)

def show_upload_interface(admin):
    """Upload interface for textbooks"""
    st.header("📁 Upload New Textbooks")
    
    # Upload mode selection
    upload_mode = st.radio(
        "Choose upload method:",
        ["📝 Manual Language Selection (Recommended)", "🔍 Automatic Language Detection"],
        help="Manual selection is more accurate for mixed-content textbooks"
    )
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF textbooks",
        type="pdf",
        accept_multiple_files=True,
        help="Upload one or more PDF textbooks. Maximum 200MB per file."
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected for upload**")
        
        if upload_mode == "📝 Manual Language Selection (Recommended)":
            show_manual_upload(admin, uploaded_files)
        else:
            show_auto_upload(admin, uploaded_files)

def show_manual_upload(admin, uploaded_files):
    """Manual language selection upload"""
    st.markdown("### 📝 Configure Each Textbook")
    
    # Process each file
    files_config = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        with st.expander(f"📖 {uploaded_file.name}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                subject_name = st.text_input(
                    "Subject Name:",
                    value=uploaded_file.name.replace('.pdf', '').replace('_', ' ').title(),
                    key=f"subject_{i}",
                    help="Enter a descriptive name for this textbook"
                )
            
            with col2:
                language = st.selectbox(
                    "Language:",
                    options=list(LANGUAGE_OPTIONS.keys()),
                    format_func=lambda x: f"{LANGUAGE_OPTIONS[x]['flag']} {LANGUAGE_OPTIONS[x]['name']}",
                    key=f"language_{i}",
                    help="Select the primary language of this textbook"
                )
            
            # Show file info
            st.caption(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.1f} MB)")
            
            files_config.append({
                'file': uploaded_file,
                'subject': subject_name,
                'language': language
            })
    
    # Bulk upload button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Upload All Textbooks", type="primary", width='stretch'):
            upload_all_textbooks(admin, files_config)

def show_auto_upload(admin, uploaded_files):
    """Automatic language detection upload"""
    st.markdown("### 🔍 Automatic Language Detection")
    st.info("📝 System will automatically detect the language of each textbook")
    
    # Show files to be processed
    for uploaded_file in uploaded_files:
        st.write(f"📖 {uploaded_file.name}")
    
    # Bulk upload with auto-detection
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔍 Auto-Detect & Upload", type="primary", width='stretch'):
            upload_with_auto_detection(admin, uploaded_files)

def upload_all_textbooks(admin, files_config):
    """Upload all configured textbooks"""
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    results_placeholder = st.empty()
    
    results = []
    
    for i, config in enumerate(files_config):
        # Update progress
        progress = (i) / len(files_config)
        progress_bar.progress(progress)
        status_placeholder.info(f"📖 Processing: {config['subject']} ({i+1}/{len(files_config)})")
        
        # Upload textbook
        success, message = admin.add_textbook(
            config['file'], 
            config['subject'], 
            config['language'],
            auto_detected=False
        )
        
        results.append({
            'Subject': str(config['subject']),
            'Language': str(LANGUAGE_OPTIONS[config['language']]['name']),
            'Status': 'Success' if success else 'Failed',
            'Message': str(message)
        })
        
        # Update progress
        progress_bar.progress((i + 1) / len(files_config))
    
    # Show results
    status_placeholder.success("🎉 Upload process completed!")
    progress_bar.progress(1.0)
    
    # Display results table
    results_df = pd.DataFrame(results)
    results_df = results_df.astype(str)  # Ensure all columns are strings
    
    # Display with success/failure styling
    st.markdown("### 📋 Upload Results")
    for i, row in results_df.iterrows():
        with st.expander(f"{'✅' if row['Status'] == 'Success' else '❌'} {row['Subject']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Language:** {row['Language']}")
                st.write(f"**Status:** {row['Status']}")
            with col2:
                st.write(f"**Details:** {row['Message']}")
    
    # Summary
    success_count = sum(1 for r in results if r['Status'] == 'Success')
    if success_count == len(results):
        st.success(f"🎉 All {success_count} textbooks uploaded successfully!")
    else:
        failed_count = len(results) - success_count
        st.warning(f"⚠️ {success_count} succeeded, {failed_count} failed. Check details above.")

def upload_with_auto_detection(admin, uploaded_files):
    """Upload with automatic language detection"""
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    results = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Update progress
        progress = (i) / len(uploaded_files)
        progress_bar.progress(progress)
        status_placeholder.info(f"🔍 Detecting language: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
        
        # Auto-detect language
        detected_lang, confidence = admin.detect_pdf_language(uploaded_file)
        
        if detected_lang == "unknown":
            detected_lang = "english"  # Default fallback
            confidence = 0.5
        
        # Generate subject name
        subject_name = uploaded_file.name.replace('.pdf', '').replace('_', ' ').title()
        
        status_placeholder.info(f"📚 Processing: {subject_name}")
        
        # Upload textbook
        success, message = admin.add_textbook(
            uploaded_file, 
            subject_name, 
            detected_lang,
            auto_detected=True
        )
        
        results.append({
            'Subject': str(subject_name),
            'Detected Language': str(LANGUAGE_OPTIONS[detected_lang]['name']),
            'Confidence': f"{confidence:.1%}",
            'Status': 'Success' if success else 'Failed',
            'Message': str(message)
        })
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Show results
    status_placeholder.success("🎉 Auto-detection and upload completed!")
    progress_bar.progress(1.0)
    
    # Display results
    st.markdown("### 📋 Auto-Detection Results")
    for i, result in enumerate(results):
        with st.expander(f"{'✅' if result['Status'] == 'Success' else '❌'} {result['Subject']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Detected Language:** {result['Detected Language']}")
                st.write(f"**Confidence:** {result['Confidence']}")
                st.write(f"**Status:** {result['Status']}")
            with col2:
                st.write(f"**Details:** {result['Message']}")
    
    success_count = sum(1 for r in results if r['Status'] == 'Success')
    if success_count == len(results):
        st.success(f"🎉 All {success_count} textbooks uploaded successfully!")
    else:
        failed_count = len(results) - success_count
        st.warning(f"⚠️ {success_count} succeeded, {failed_count} failed. Check details above.")

def show_manage_interface(admin):
    """Interface to manage existing textbooks"""
    st.header("📚 Manage Existing Textbooks")
    
    if not admin.textbooks:
        st.info("📚 No textbooks uploaded yet. Use the Upload tab to add textbooks.")
        return
    
    # Create textbooks summary cards
    st.markdown("### 📖 Uploaded Textbooks")
    
    # Display as cards instead of problematic dataframe
    cols_per_row = 2
    textbook_items = list(admin.textbooks.items())
    
    for i in range(0, len(textbook_items), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(textbook_items):
                subject, info = textbook_items[i + j]
                
                with col:
                    lang_info = LANGUAGE_OPTIONS.get(info['language'], {'name': info['language'].title(), 'flag': '📖'})
                    
                    with st.container():
                        st.markdown(f"#### {lang_info['flag']} {subject}")
                        st.markdown(f"**Language:** {lang_info['name']}")
                        st.markdown(f"**Pages:** {info['pages']}")
                        st.markdown(f"**Chunks:** {info['chunks']}")
                        st.markdown(f"**Method:** {'Auto-detected' if info.get('auto_detected', False) else 'Manual'}")
                        st.markdown(f"**Status:** {info['status'].title()}")
                        
                        # Individual remove button with confirmation
                        if st.button(f"🗑️ Remove", key=f"remove_{subject}", type="secondary"):
                            # Use session state to handle confirmation
                            st.session_state[f"confirm_remove_{subject}"] = True
                        
                        # Show confirmation if button was clicked
                        if st.session_state.get(f"confirm_remove_{subject}", False):
                            st.warning(f"⚠️ Remove '{subject}' textbook?")
                            
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("✅ Yes, Remove", key=f"confirm_yes_{subject}", type="primary"):
                                    success, message = admin.remove_textbook(subject)
                                    if success:
                                        st.success(message)
                                        st.session_state[f"confirm_remove_{subject}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                                        st.session_state[f"confirm_remove_{subject}"] = False
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"confirm_no_{subject}"):
                                    st.session_state[f"confirm_remove_{subject}"] = False
                                    st.rerun()
                        
                        st.divider()

    # Bulk operations section
    st.markdown("### 🔧 Bulk Operations")
    
    if textbook_items:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Statistics")
            total_pages = sum(info['pages'] for _, info in textbook_items)
            total_chunks = sum(info['chunks'] for _, info in textbook_items)
            st.metric("Total Pages", total_pages)
            st.metric("Total Chunks", total_chunks)
        
        with col2:
            st.markdown("#### ⚠️ Danger Zone")
            if st.button("🗑️ Remove All Textbooks", type="secondary"):
                st.session_state["confirm_remove_all"] = True
            
            # Confirmation for remove all
            if st.session_state.get("confirm_remove_all", False):
                st.error("⚠️ This will remove ALL textbooks. Are you sure?")
                
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Remove All", key="remove_all_yes", type="primary"):
                        removed_count = 0
                        for subject in list(admin.textbooks.keys()):
                            success, _ = admin.remove_textbook(subject)
                            if success:
                                removed_count += 1
                        
                        st.success(f"✅ Removed {removed_count} textbooks")
                        st.session_state["confirm_remove_all"] = False
                        st.rerun()
                
                with col_no:
                    if st.button("❌ Cancel", key="remove_all_no"):
                        st.session_state["confirm_remove_all"] = False
                        st.rerun()

def show_settings_interface(admin):
    """System settings and maintenance"""
    st.header("⚙️ System Settings")
    
    # Database management
    st.subheader("🔍 Database Management")
    
    if admin.vectorstore:
        st.success("✅ Vector database is active and ready")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reload Database", help="Reload the vector database from disk"):
                with st.spinner("🔄 Reloading database..."):
                    try:
                        admin.load_existing_data()
                        st.success("✅ Database reloaded successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed to reload database: {e}")
        
        with col2:
            st.warning("⚠️ Danger Zone")
            if st.button("🗑️ Clear All Data", help="This will delete all textbooks and the database"):
                st.session_state["confirm_clear_all"] = True
            
            # Confirmation for clearing all data
            if st.session_state.get("confirm_clear_all", False):
                st.error("⚠️ Type 'DELETE ALL' to confirm complete data wipe:")
                confirm_text = st.text_input("Confirmation:", key="confirm_delete_input")
                
                col_confirm, col_cancel = st.columns(2)
                
                with col_confirm:
                    if st.button("🗑️ Delete Everything", type="primary", disabled=(confirm_text != "DELETE ALL")):
                        if confirm_text == "DELETE ALL":
                            clear_all_data(admin)
                            st.session_state["confirm_clear_all"] = False
                            st.rerun()
                
                with col_cancel:
                    if st.button("❌ Cancel", key="cancel_clear"):
                        st.session_state["confirm_clear_all"] = False
                        st.rerun()
    else:
        st.error("❌ Vector database not initialized")
        if st.button("🔧 Initialize Database"):
            try:
                admin.load_existing_data()
                st.success("✅ Database initialized!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to initialize database: {e}")
    
    st.divider()
    
    # System info
    st.subheader("ℹ️ System Information")
    stats = admin.get_system_stats()
    
    # Display system info as cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🤖 AI System")
        if admin.llm_available:
            st.success(f"✅ Ollama Running")
            st.info(f"🧠 Model: {admin.model_name}")
        else:
            st.error("❌ Ollama Not Running")
            st.markdown("Make sure Ollama is installed and running:\n``````")
    
    with col2:
        st.markdown("#### 📊 Database Stats")
        st.metric("Total Textbooks", stats['total_textbooks'])
        st.metric("Total Pages", stats['total_pages'])
        st.metric("Total Chunks", stats['total_chunks'])
        
        if stats['vectorstore_ready']:
            st.success("✅ Database Ready")
        else:
            st.error("❌ Database Not Ready")
    
    # Language breakdown
    if stats['languages']:
        st.markdown("#### 🌍 Languages")
        for lang, count in stats['languages'].items():
            lang_info = LANGUAGE_OPTIONS.get(lang, {'name': lang.title(), 'flag': '📖'})
            st.write(f"{lang_info['flag']} **{lang_info['name']}:** {count} textbooks")

def clear_all_data(admin):
    """Clear all data (for testing/reset purposes)"""
    with st.spinner("🗑️ Clearing all data..."):
        try:
            # Clear metadata
            admin.textbooks = {}
            admin.save_metadata()
            
            # Note: Vector database clearing would need additional implementation
            st.warning("⚠️ Metadata cleared. Vector database may need manual cleanup.")
            st.info("🔄 Please restart the application for full cleanup.")
            
        except Exception as e:
            st.error(f"❌ Error clearing data: {e}")


if __name__ == "__main__":
    main()
