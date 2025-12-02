import streamlit as st
import os
import shutil
import uuid
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content

# Page Config
st.set_page_config(page_title="LinkedIn Carousel Generator", page_icon="✨", layout="wide")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #714B67;
        text-align: center;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #017E84;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        border: none;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #016064;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>✨ AI LinkedIn Carousel Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Turn any YouTube video into a professional, industry-standard carousel in seconds.</p>", unsafe_allow_html=True)

# Sidebar for Inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key (Optional)", type="password", help="Enter your Google Gemini API Key for deep analysis. If left blank, a basic summarizer will be used.")
    logo_file = st.file_uploader("Upload Brand Logo", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    st.markdown("### 🎨 Brand Colors")
    primary_color = st.color_picker("Primary Color", "#714B67")
    
    st.markdown("---")
    st.info("Built for Metamorphosis & Odoo Partners.")

# Main Content
tab1, tab2 = st.tabs(["📺 YouTube Video", "📝 Manual Text"])

text = ""

with tab1:
    url = st.text_input("🔗 YouTube Video URL", placeholder="https://youtube.com/watch?v=...")
    if url:
        st.info("Note: If the video has no captions, use the 'Manual Text' tab.")

with tab2:
    manual_text = st.text_area("Paste Transcript or Content Here", height=200, placeholder="Paste the video transcript, a blog post, or any text you want to turn into a carousel.")

if st.button("Generate Carousel"):
    with st.spinner("Processing..."):
        # Determine source
        if manual_text:
            text = manual_text
        elif url:
            with st.spinner("🔍 Fetching transcript..."):
                try:
                    text = get_transcript_text(url)
                    if not text:
                        st.error("Transcript is empty. Please use Manual Text.")
                        st.stop()
                except ValueError as ve:
                    st.error(f"Transcript Error: {ve}")
                    st.info("💡 Tip: You can copy the transcript manually from YouTube description/captions and use the 'Manual Text' tab.")
                    st.stop()
                except Exception as e:
                    st.error(f"Unexpected Error: {e}")
                    st.stop()
        else:
            st.error("Please provide a Video URL or Manual Text.")
            st.stop()

        with st.spinner("🧠 Generating deep insights..."):
            # 2. Process Content (LLM)
            if not api_key:
                st.warning("⚠️ No API Key provided. Using Basic Mode (Keyword Extraction). For professional AI summaries, please enter a Gemini API Key in the sidebar.")
            
            slides_content = process_content(text, api_key=api_key)
            if not slides_content:
                st.error("Failed to generate content.")
                st.stop()

        with st.spinner("🎨 Designing premium slides..."):
            # 3. Generate Images
            # Setup directories
            session_id = str(uuid.uuid4())
            output_dir = os.path.join("output", session_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Save logo if uploaded
            logo_path = None
            if logo_file:
                logo_path = os.path.join(output_dir, "logo.png")
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            # Initialize Generator
            generator = CarouselGenerator(logo_path=logo_path, brand_color=primary_color)
            
            image_paths = []
            for i, slide in enumerate(slides_content):
                path = generator.generate_slide(slide, i + 1, len(slides_content), output_dir)
                image_paths.append(path)
                
        # 4. Display Results
        st.success("🎉 Carousel Generated Successfully!")
        
        # Display in a grid
        cols = st.columns(len(image_paths))
        for idx, col in enumerate(cols):
            with col:
                st.image(image_paths[idx], caption=f"Slide {idx+1}", use_container_width=True)
        
        # Zip Download
        shutil.make_archive(os.path.join(output_dir, "carousel"), 'zip', output_dir)
        zip_path = os.path.join(output_dir, "carousel.zip")
        
        with open(zip_path, "rb") as f:
            st.download_button(
                label="⬇️ Download All Images (ZIP)",
                data=f,
                file_name="linkedin_carousel.zip",
                mime="application/zip"
            )

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8em;'>Powered by Metamorphosis AI • <a href='#'>Documentation</a></p>", unsafe_allow_html=True)
