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
    
    if api_key:
        if st.button("Verify Key"):
            with st.spinner("Checking API Key..."):
                is_valid, message = verify_api_key(api_key)
                if is_valid:
                    st.success(message)
                else:
                    st.error(f"Invalid Key: {message}")
    
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
st.info("🔒 Mode: Success Story (Fixed)")
content_type = "Success Story"

# Session State for Content
if 'slides_content' not in st.session_state:
    st.session_state.slides_content = None

if st.button("🔍 Analyze Video & Plan Content", type="primary"):
    with st.spinner("Processing Transcript..."):
        # 1. Get Text
        if manual_text:
            text = manual_text
        elif url:
            with st.spinner("Fetching transcript..."):
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
        with st.spinner("🧠 Drafting Content Plan..."):
            if not api_key:
                st.warning("⚠️ No API Key. Using Basic Mode.")
            
            content = process_content(text, api_key=api_key, content_type=content_type)
            if content:
                st.session_state.slides_content = content
                st.rerun() # Rerun to show the editor
            else:
                st.error("Failed to generate content.")

# Review & Edit Section
if st.session_state.slides_content:
    st.markdown("---")
    st.header("📝 Review & Edit Plan")
    st.info("Edit the text below before generating the final images.")
    
    updated_slides = []
    for i, slide in enumerate(st.session_state.slides_content):
        with st.expander(f"Slide {i+1}: {slide.get('title', 'Untitled')}", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                subtitle = st.text_input(f"Subtitle {i+1}", slide.get('subtitle', ''))
                title = st.text_input(f"Title {i+1}", slide.get('title', ''))
            with col2:
                # Check for Stats (Success Story Result Slide)
                if 'stats' in slide:
                    st.caption("📊 Key Metrics (Value | Label)")
                    current_stats = slide['stats']
                    new_stats = []
                    for j, stat in enumerate(current_stats):
                        c1, c2 = st.columns(2)
                        with c1:
                            val = st.text_input(f"Value {j+1} (Slide {i+1})", stat.get('value', ''))
                        with c2:
                            lbl = st.text_input(f"Label {j+1} (Slide {i+1})", stat.get('label', ''))
                        new_stats.append({"value": val, "label": lbl})
                    
                    # Store stats, clear body
                    updated_slides.append({
                        "subtitle": subtitle,
                        "title": title,
                        "body": "",
                        "stats": new_stats
                    })
                else:
                    # Handle body as list or string
                    body_val = slide.get('body', '')
                    if isinstance(body_val, list):
                        body_val = "\n".join(body_val)
                    
                    body = st.text_area(f"Body Text {i+1}", body_val, height=100, help="Enter bullet points on new lines.")
                    
                    # Convert back to list if it looks like a list
                    if "\n" in body:
                        body_final = [line.strip() for line in body.split("\n") if line.strip()]
                    else:
                        body_final = body
                        
                    updated_slides.append({
                        "subtitle": subtitle,
                        "title": title,
                        "body": body_final
                    })
    
    # Update session state with edits (optional, but good for persistence)
    # st.session_state.slides_content = updated_slides 

    st.markdown("---")
    if st.button("✨ Generate Final Images", type="primary"):
        with st.spinner("🎨 Rendering High-Quality Slides..."):
            session_id = str(uuid.uuid4())
            output_dir = os.path.join("output", session_id)
            os.makedirs(output_dir, exist_ok=True)
            
            logo_path = None
            if logo_file:
                logo_path = os.path.join(output_dir, "logo.png")
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            # Initialize Generator
            generator = CarouselGenerator(
                logo_path=logo_path, 
                brand_color=primary_color, 
                secondary_color=secondary_color,
                font_name=font_choice,
                author_handle=author_handle
            )
            
            try:
                # Use the UPDATED slides from the form
                image_paths = generator.generate_all_slides(updated_slides, output_dir)
            except Exception as e:
                st.error(f"Generation Failed: {e}")
                st.stop()
                
        # Display Results
        st.success("🎉 Carousel Ready!")
        
        # Grid Display
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
