import streamlit as st
import requests
from io import BytesIO

# Backend API URL
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Document Upload", page_icon="📄")

st.title("📄 Document Upload")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx", "doc"])

if uploaded_file is not None:
    st.info(f"Selected file: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
    
    if st.button("Upload to Azure"):
        try:
            # Step 1: Get SAS URL from backend
            with st.spinner("Getting upload URL..."):
                init_response = requests.post(
                    f"{BACKEND_URL}/api/v1/uploads/init",
                    params={"filename": uploaded_file.name}
                )
                
                if init_response.status_code == 200:
                    data = init_response.json()
                    blob_name = data["blob_name"]
                    sas_url = data["blob_url"]
                    
                    # Step 2: Upload file directly to Azure
                    st.info("Uploading file to Azure...")
                    file_content = uploaded_file.read()
                    
                    upload_response = requests.put(
                        sas_url,
                        data=file_content,
                        headers={"x-ms-blob-type": "BlockBlob", "Content-Type": uploaded_file.type}
                    )
                    
                    if upload_response.status_code in [200, 201]:
                        # Step 3: Verify upload completed
                        st.info("Verifying upload...")
                        complete_response = requests.post(
                            f"{BACKEND_URL}/api/v1/uploads/complete",
                            json={"blob_name": blob_name}
                        )
                        
                        if complete_response.status_code == 200:
                            metadata = complete_response.json()
                            st.success("✅ Upload successful!")
                            
                            st.subheader("File Details")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**File Name:** {metadata['file_name']}")
                                st.write(f"**Size:** {metadata['size_bytes']:,} bytes")
                            with col2:
                                st.write(f"**Content Type:** {metadata['content_type']}")
                                st.write(f"**Path:** {metadata['path']}")
                            
                            # Display Azure URL (without SAS token)
                            azure_url = sas_url.split("?")[0]
                            st.code(azure_url, language=None)
                        else:
                            st.error(f"❌ Verification failed: {complete_response.text}")
                    else:
                        st.error(f"❌ Azure upload failed: Status {upload_response.status_code}")
                        st.error(upload_response.text)
                else:
                    st.error(f"❌ Failed to get upload URL: {init_response.status_code}")
                    st.error(init_response.text)
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Make sure FastAPI is running on http://localhost:8000")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
