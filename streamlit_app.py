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
    api_key = st.text_input("Gemini API Key (Recommended)", type="password", help="Required for 'Smart' content generation.")
    
    st.markdown("---")
    st.markdown("### 🎨 Design & Branding")
    
    # Brand Identity
    logo_file = st.file_uploader("Upload Brand Logo", type=['png', 'jpg', 'jpeg'])
    author_handle = st.text_input("LinkedIn Handle/Website", "@metamorphosis", help="Shown in the footer")
    
    # Colors
    col1, col2 = st.columns(2)
    with col1:
        primary_color = st.color_picker("Primary Color", "#714B67") # Odoo Purple
        bg_color = st.color_picker("Background", "#FFFFFF")
    with col2:
        secondary_color = st.color_picker("Secondary Color", "#017E84") # Odoo Teal
        text_color = st.color_picker("Text Color", "#333333")
        
    # Font
    font_choice = st.selectbox("Font Style", ["Inter", "Roboto", "Poppins", "Merriweather"])

    st.markdown("---")
    st.info("Built for Metamorphosis & Odoo Partners.")

# Main Content
st.markdown("### 1. Content Source")
tab1, tab2 = st.tabs(["📺 YouTube Video", "📝 Manual Text"])

text = ""
with tab1:
    url = st.text_input("YouTube Video URL", placeholder="https://youtube.com/watch?v=...")
    if url: st.caption("We'll extract the transcript automatically.")

with tab2:
    manual_text = st.text_area("Paste Text Content", height=150, placeholder="Paste a blog post, transcript, or rough notes here.")

st.markdown("### 2. Carousel Type")
content_type = st.selectbox(
    "Choose the goal of this carousel:",
    ["Success Story (Problem/Solution)", "Tutorial (Step-by-Step)", "Educational (Deep Dive)", "Video Takeaway (Summary)"],
    index=0
)

if st.button("✨ Generate Carousel", type="primary"):
    with st.spinner("Processing..."):
        # 1. Get Text
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
                    st.info("💡 Tip: Use the 'Manual Text' tab.")
                    st.stop()
                except Exception as e:
                    st.error(f"Unexpected Error: {e}")
                    st.stop()
        else:
            st.error("Please provide a Video URL or Manual Text.")
            st.stop()

        # 2. Process Content (LLM)
        with st.spinner("🧠 Analyzing & Writing Copy..."):
            if not api_key:
                st.warning("⚠️ No API Key. Using Basic Mode. Add Gemini Key for premium content.")
            
            slides_content = process_content(text, api_key=api_key, content_type=content_type)
            if not slides_content:
                st.error("Failed to generate content.")
                st.stop()

        # 3. Generate Images
        with st.spinner("🎨 Rendering Infographic Slides..."):
            session_id = str(uuid.uuid4())
            output_dir = os.path.join("output", session_id)
            os.makedirs(output_dir, exist_ok=True)
            
            logo_path = None
            if logo_file:
                logo_path = os.path.join(output_dir, "logo.png")
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            # Initialize Generator with new options
            generator = CarouselGenerator(
                logo_path=logo_path, 
                brand_color=primary_color, 
                secondary_color=secondary_color,
                font_name=font_choice,
                author_handle=author_handle
            )
            
            try:
                image_paths = generator.generate_all_slides(slides_content, output_dir)
            except Exception as e:
                st.error(f"Generation Failed: {e}")
                st.stop()
                
        # 4. Display Results
        st.success("🎉 Carousel Ready!")
        
        # Display in a grid with individual download buttons
        for idx, img_path in enumerate(image_paths):
            col_img, col_btn = st.columns([3, 1])
            with col_img:
                st.image(img_path, caption=f"Slide {idx+1}", use_container_width=True)
            with col_btn:
                with open(img_path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Slide {idx+1}",
                        data=f,
                        file_name=f"slide_{idx+1}.png",
                        mime="image/png",
                        key=f"btn_{idx}"
                    )
        
        # Zip Download
        shutil.make_archive(os.path.join(output_dir, "carousel"), 'zip', output_dir)
        zip_path = os.path.join(output_dir, "carousel.zip")
        
        st.markdown("---")
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Download Full Carousel (ZIP)",
                data=f,
                file_name="linkedin_carousel.zip",
                mime="application/zip",
                type="primary"
            )

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8em;'>Powered by Metamorphosis AI • <a href='#'>Documentation</a></p>", unsafe_allow_html=True)
