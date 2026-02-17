import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile
from verifier import IdentityVerifier

# Set page config
st.set_page_config(
    page_title="Identity Verification System v2.0",
    page_icon="ic_lock",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
    }
    .error-box {
        padding: 20px;
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 10px;
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def main():
    st.title("[LOCK] Production-Grade Identity Verification")
    st.markdown("### Powered by TensorFlow, DeepFace & Qdrant")
    
    # --- Sidebar Configuration ---
    st.sidebar.header("[GEAR] System Configuration")
    
    model_name = st.sidebar.selectbox(
        "Face Recognition Model",
        ["ArcFace", "VGG-Face", "Facenet", "Facenet512"],
        index=0
    )
    
    detector_backend = st.sidebar.selectbox(
        "Face Detection Backend",
        ["retinaface", "mtcnn", "opencv", "ssd"],
        index=0
    )
    
    distance_threshold = st.sidebar.slider(
        "Similarity Threshold (Cosine)",
        min_value=0.0, max_value=1.0, value=0.4, step=0.05,
        help="Higher value = Stricter matching for Cosine Similarity (0-1)"
    )
    
    # Initialize Verifier (Cached to avoid reloading model on every interaction)
    @st.cache_resource
    def get_verifier(model, backend):
        return IdentityVerifier(model_name=model, detector_backend=backend)
    
    try:
        verifier = get_verifier(model_name, detector_backend)
        st.sidebar.success(f"Model {model_name} loaded!")
    except Exception as e:
        st.sidebar.error(f"Failed to load model: {e}")
        return

    # --- Main Tabs ---
    tab1, tab2, tab3 = st.tabs(["[SEARCH] Verification (1:1)", "[ID] Identification (1:N)", "[EDIT] Enrollment"])
    
    # --- Tab 1: 1:1 Verification ---
    with tab1:
        st.header("1:1 Verification")
        col1, col2 = st.columns(2)
        
        with col1:
            id_card = st.file_uploader("Upload ID Card", type=['jpg', 'png'], key="v_id")
            if id_card: st.image(id_card, width=300)
            
        with col2:
            selfie = st.file_uploader("Upload Selfie", type=['jpg', 'png'], key="v_selfie")
            if selfie: st.image(selfie, width=300)
            
        if st.button("Verify Identity", key="btn_verify"):
            if id_card and selfie:
                with st.spinner("Verifying..."):
                    path1 = save_uploaded_file(id_card)
                    path2 = save_uploaded_file(selfie)
                    
                    if path1 and path2:
                        result = verifier.verify_1_to_1(path1, path2)
                        
                        # Cleanup
                        os.remove(path1)
                        os.remove(path2)
                        
                        if result.get('verified'):
                            st.markdown(f"""
                                <div class="success-box">
                                    <h2>[SUCCESS] Verified Match</h2>
                                    <p>Distance: {result.get('distance'):.4f}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class="error-box">
                                    <h2>[FAILURE] No Match</h2>
                                    <p>Distance: {result.get('distance'):.4f}</p>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("Please upload both images.")

    # --- Tab 2: 1:N Identification ---
    with tab2:
        st.header("1:N Identification")
        st.markdown("Search the database for a matching identity.")
        
        query_img = st.file_uploader("Upload Query Image", type=['jpg', 'png'], key="i_query")
        if query_img:
            st.image(query_img, width=300)
            
            if st.button("Identify Person", key="btn_identify"):
                with st.spinner("Searching Database..."):
                    path = save_uploaded_file(query_img)
                    if path:
                        found, user_id, score = verifier.identify_from_database(path, threshold=distance_threshold)
                        os.remove(path)
                        
                        if found:
                            st.markdown(f"""
                                <div class="success-box">
                                    <h2>[SUCCESS] Identity Found: {user_id}</h2>
                                    <p>Similarity Score: {score:.4f}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class="error-box">
                                    <h2>[?] Unknown Person</h2>
                                    <p>No match found above threshold {distance_threshold}</p>
                                </div>
                            """, unsafe_allow_html=True)

    # --- Tab 3: Enrollment ---
    with tab3:
        st.header("New User Enrollment")
        st.markdown("Add a new person to the database.")
        
        new_name = st.text_input("Enter Name / User ID")
        enroll_img = st.file_uploader("Upload Photo", type=['jpg', 'png'], key="e_img")
        
        if enroll_img: st.image(enroll_img, width=300)
        
        if st.button("Enroll User", key="btn_enroll"):
            if new_name and enroll_img:
                with st.spinner("Enrolling..."):
                    path = save_uploaded_file(enroll_img)
                    if path:
                        success, msg = verifier.enroll_identity(path, new_name)
                        os.remove(path)
                        
                        if success:
                            st.success(f"[SUCCESS] {msg}")
                        else:
                            st.error(f"[FAILURE] {msg}")
            else:
                st.warning("Please provide both a name and an image.")

if __name__ == '__main__':
    main()
