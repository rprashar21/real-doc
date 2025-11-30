import streamlit as st
import requests
import hashlib

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="RAG Document Processor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Card-like containers */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Progress steps */
    .step-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .step-number {
        font-size: 2rem;
        font-weight: bold;
        opacity: 0.8;
    }
    
    /* File info card */
    .file-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'upload_in_progress': False,
        'upload_completed': False,
        'book_processed': False,
        'current_file_hash': None,
        'file_content': None,
        'file_name': None,
        'file_type': None,
        'blob_name': None,
        'file_metadata': None,
        'book_data': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/book.png", width=100)
    st.title("RAG Doc")
    st.markdown("---")
    st.markdown("### 📋 How it works")
    st.markdown("""
    1. **Upload** your PDF document
    2. **Process** to extract text
    3. **Use** for RAG queries
    """)
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("[API Docs](http://localhost:8000/docs)")
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content
st.title("📚 Document Processor")
st.markdown("Upload and process documents for your RAG application")

# Progress indicator
def show_progress():
    col1, col2, col3 = st.columns(3)
    
    step1_color = "🟢" if st.session_state.get('file_content') else "⚪"
    step2_color = "🟢" if st.session_state.get('upload_completed') else "⚪"
    step3_color = "🟢" if st.session_state.get('book_processed') else "⚪"
    
    with col1:
        st.markdown(f"### {step1_color} Step 1")
        st.caption("Select File")
    with col2:
        st.markdown(f"### {step2_color} Step 2")
        st.caption("Upload to Cloud")
    with col3:
        st.markdown(f"### {step3_color} Step 3")
        st.caption("Process Document")

show_progress()
st.markdown("---")

# ============================================
# STEP 1: File Selection
# ============================================
if not st.session_state.get('upload_completed'):
    st.subheader("📁 Step 1: Select Your Document")
    
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload",
        type=["pdf", "txt", "docx"],
        help="Supported formats: PDF, TXT, DOCX"
    )
    
    if uploaded_file is not None:
        # Read and hash file
        file_content = uploaded_file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        
        # Store in session state
        st.session_state['file_content'] = file_content
        st.session_state['file_name'] = uploaded_file.name
        st.session_state['file_type'] = uploaded_file.type
        
        # Reset if different file
        if st.session_state.get('current_file_hash') != file_hash:
            st.session_state['upload_completed'] = False
            st.session_state['book_processed'] = False
            st.session_state['current_file_hash'] = file_hash
        
        # File info card
        col1, col2 = st.columns([2, 1])
        with col1:
            st.success(f"✅ **{uploaded_file.name}** selected")
            
            # File details
            file_size_mb = len(file_content) / (1024 * 1024)
            st.markdown(f"""
            | Property | Value |
            |----------|-------|
            | **Size** | {file_size_mb:.2f} MB |
            | **Type** | {uploaded_file.type or 'Unknown'} |
            | **Hash** | `{file_hash[:12]}...` |
            """)
        
        with col2:
            st.markdown("### Ready to Upload")
            
            if st.session_state['upload_in_progress']:
                st.button("⏳ Uploading...", disabled=True, use_container_width=True)
            else:
                if st.button("☁️ Upload to Azure", type="primary", use_container_width=True):
                    st.session_state['upload_in_progress'] = True
                    
                    try:
                        # Step 1: Get SAS URL
                        with st.spinner("Generating upload URL..."):
                            init_response = requests.post(
                                f"{BACKEND_URL}/api/v1/uploads/init",
                                params={"filename": uploaded_file.name, "file_hash": file_hash}
                            )
                        
                        if init_response.status_code == 200:
                            data = init_response.json()
                            blob_name = data["blob_name"]
                            sas_url = data["blob_url"]
                            is_existing = data.get("is_existing", False)
                            
                            if not is_existing:
                                # Upload to Azure
                                with st.spinner("Uploading to Azure Blob Storage..."):
                                    upload_response = requests.put(
                                        sas_url,
                                        data=file_content,
                                        headers={
                                            "x-ms-blob-type": "BlockBlob",
                                            "Content-Type": uploaded_file.type or "application/octet-stream"
                                        },
                                        timeout=300
                                    )
                                
                                if upload_response.status_code not in [200, 201]:
                                    st.error(f"Upload failed: {upload_response.status_code}")
                                    st.session_state['upload_in_progress'] = False
                                    st.stop()
                            
                            # Verify upload
                            with st.spinner("Verifying upload..."):
                                complete_response = requests.post(
                                    f"{BACKEND_URL}/api/v1/uploads/complete",
                                    json={"blob_name": blob_name}
                                )
                            
                            if complete_response.status_code == 200:
                                st.session_state['upload_completed'] = True
                                st.session_state['upload_in_progress'] = False
                                st.session_state['blob_name'] = blob_name
                                st.session_state['file_metadata'] = complete_response.json()
                                st.rerun()
                            else:
                                st.error("Verification failed")
                                st.session_state['upload_in_progress'] = False
                        else:
                            st.error(f"Failed to get upload URL: {init_response.text}")
                            st.session_state['upload_in_progress'] = False
                            
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend. Is FastAPI running?")
                        st.session_state['upload_in_progress'] = False
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state['upload_in_progress'] = False

# ============================================
# STEP 2: File Uploaded - Ready for Processing
# ============================================
elif st.session_state.get('upload_completed') and not st.session_state.get('book_processed'):
    st.subheader("✅ Step 2: File Uploaded Successfully")
    
    metadata = st.session_state.get('file_metadata', {})
    
    # Success banner
    st.success("🎉 Your document has been uploaded to Azure Blob Storage!")
    
    # File details
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 File Information")
        st.markdown(f"""
        | Property | Value |
        |----------|-------|
        | **File Name** | {metadata.get('file_name', 'N/A')} |
        | **Size** | {metadata.get('size_bytes', 0):,} bytes |
        | **Content Type** | {metadata.get('content_type', 'N/A')} |
        """)
    
    with col2:
        st.markdown("### ☁️ Cloud Storage")
        st.code(st.session_state.get('blob_name', 'N/A'), language=None)
    
    st.markdown("---")
    
    # Process section
    st.subheader("📚 Step 3: Process Document")
    st.info("Extract text from your document and create a structured representation for RAG.")
    
    col1, col2 = st.columns(2)
    with col1:
        title_input = st.text_input("📖 Title (optional)", placeholder="Enter book title")
    with col2:
        author_input = st.text_input("✍️ Author (optional)", placeholder="Enter author name")
    
    st.markdown("")
    
    if st.button("🚀 Process Document", type="primary", use_container_width=True):
        blob_name = st.session_state.get('blob_name')
        
        if not blob_name:
            st.error("No blob name found. Please re-upload the file.")
        else:
            try:
                with st.spinner("Processing document... This may take a moment."):
                    process_response = requests.post(
                        f"{BACKEND_URL}/api/v1/process/book",
                        json={
                            "blob_name": blob_name,
                            "title": title_input if title_input else None,
                            "author": author_input if author_input else None
                        },
                        timeout=120
                    )
                
                if process_response.status_code == 200:
                    st.session_state['book_processed'] = True
                    st.session_state['book_data'] = process_response.json()
                    st.rerun()
                else:
                    error_detail = process_response.json().get('detail', process_response.text)
                    st.error(f"Processing failed: {error_detail}")
                    
            except requests.exceptions.Timeout:
                st.error("Request timed out. The file might be too large.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is FastAPI running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================
# STEP 3: Processing Complete - Show Results
# ============================================
elif st.session_state.get('book_processed'):
    book_data = st.session_state.get('book_data', {})
    book_meta = book_data.get('metadata', {})
    chapters = book_data.get('chapters', [])
    
    # Success banner
    st.balloons()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="margin: 0; color: white;">🎉 Document Processed Successfully!</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your document is ready for RAG queries</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Book details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h1 style="margin: 0; color: #667eea;">📄</h1>
            <h3 style="margin: 0.5rem 0;">{}</h3>
            <p style="margin: 0; color: #666;">Pages</p>
        </div>
        """.format(book_meta.get('num_pages', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h1 style="margin: 0; color: #667eea;">📚</h1>
            <h3 style="margin: 0.5rem 0;">{}</h3>
            <p style="margin: 0; color: #666;">Chapters</p>
        </div>
        """.format(len(chapters)), unsafe_allow_html=True)
    
    with col3:
        total_chars = sum(len(ch.get('text', '')) for ch in chapters)
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; text-align: center;">
            <h1 style="margin: 0; color: #667eea;">📝</h1>
            <h3 style="margin: 0.5rem 0;">{:,}</h3>
            <p style="margin: 0; color: #666;">Characters</p>
        </div>
        """.format(total_chars), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Book metadata
    st.subheader("📖 Document Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Title:** {book_meta.get('title', 'Untitled')}")
        st.markdown(f"**Author:** {book_meta.get('author', 'Unknown')}")
    with col2:
        st.markdown(f"**Source:** `{book_meta.get('source_blob', 'N/A')}`")
        st.markdown(f"**Book ID:** `{book_meta.get('book_id', 'N/A')[:50]}...`")
    
    st.markdown("---")
    
    # Chapter preview
    st.subheader("📑 Chapter Preview")
    
    if chapters:
        chapter_options = [f"Chapter {ch['index']}: {ch.get('title') or 'Untitled'}" for ch in chapters[:10]]
        selected_chapter = st.selectbox("Select a chapter to preview", chapter_options)
        
        selected_idx = int(selected_chapter.split(":")[0].replace("Chapter ", ""))
        chapter_text = next((ch['text'] for ch in chapters if ch['index'] == selected_idx), "")
        
        st.text_area(
            "Content Preview",
            value=chapter_text[:2000] + ("..." if len(chapter_text) > 2000 else ""),
            height=300,
            disabled=True
        )
    
    st.markdown("---")
    
    # Storage info
    st.subheader("☁️ Storage Information")
    st.info(f"📄 JSON stored in processed container as: `{book_meta.get('book_id', 'N/A')}.json`")
    
    # Next steps
    st.markdown("---")
    st.subheader("🚀 What's Next?")
    st.markdown("""
    Your document is now ready for:
    - **Embedding Generation** - Create vector embeddings for semantic search
    - **RAG Queries** - Ask questions about your document
    - **Summarization** - Generate summaries of chapters or the entire document
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Built with ❤️ using FastAPI + Streamlit</p>",
    unsafe_allow_html=True
)
