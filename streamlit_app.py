import streamlit as st
import os
import shutil
import uuid
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content, verify_api_key

# Page Config
st.set_page_config(page_title="LinkedIn Carousel Generator", page_icon="✨", layout="wide")

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Wizard Steps */
    .step-container {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        border: 1px solid #eee;
    }
    
    .step-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 50px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.2s;
    }
    
    .primary-btn {
        background-color: #714B67 !important;
        color: white !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    
    /* Success Message */
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Global Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Global Settings")
    
    # API Key
    api_key = st.text_input("Gemini API Key", type="password", help="Required for AI generation.")
    if api_key:
        if st.button("Verify Key", key="verify_btn"):
            with st.spinner("Checking..."):
                is_valid, message = verify_api_key(api_key)
                if is_valid:
                    st.success("✅ Valid Key")
                else:
                    st.error(f"❌ Invalid: {message}")
    
    st.markdown("---")
    st.markdown("### 🎨 Brand Assets")
    logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
    author_handle = st.text_input("Handle / Website", "@metamorphosis")
    
    st.markdown("---")
    st.markdown("### 🌈 Brand Colors")
    col1, col2 = st.columns(2)
    with col1:
        primary_color = st.color_picker("Primary", "#714B67")
        bg_color = st.color_picker("Background", "#FFFFFF")
    with col2:
        secondary_color = st.color_picker("Secondary", "#017E84")
        text_color = st.color_picker("Text", "#333333")
    
    font_choice = st.selectbox("Font", ["Inter", "Roboto", "Poppins"])

# --- Main Content: Wizard ---
st.title("✨ AI Carousel Generator")
st.markdown("Create premium LinkedIn carousels in seconds.")

# Session State
if 'step' not in st.session_state: st.session_state.step = 1
if 'slides_content' not in st.session_state: st.session_state.slides_content = None
if 'thumbnail_url' not in st.session_state: st.session_state.thumbnail_url = None

# Step 1: Source
st.markdown('<div class="step-container">', unsafe_allow_html=True)
st.markdown('<div class="step-header">1️⃣ Content Source</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📺 YouTube Video", "📝 Manual Text"])
text_content = ""

with tab1:
    url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
with tab2:
    manual_text = st.text_area("Paste Text", height=150)

if st.button("Analyze & Generate Plan ➔", type="primary", use_container_width=True):
    with st.spinner("Analyzing content..."):
        # Fetch Text
        if manual_text:
            text_content = manual_text
            st.session_state.thumbnail_url = None
        elif url:
            try:
                text_content, thumb = get_transcript_text(url)
                st.session_state.thumbnail_url = thumb
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
        
        if not text_content:
            st.error("Please provide content.")
            st.stop()
            
        # Generate
        content, error = process_content(text_content, api_key=api_key, content_type="Success Story")
        
        if content:
            st.session_state.slides_content = content
            st.session_state.step = 2
            st.rerun()
        else:
            st.error(f"Generation Failed: {error}")

st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Review & Edit
if st.session_state.slides_content:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-header">2️⃣ Review Content</div>', unsafe_allow_html=True)
    
    updated_slides = []
    for i, slide in enumerate(st.session_state.slides_content):
        with st.expander(f"Slide {i+1}: {slide.get('title', 'Untitled')}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            with col1:
                sub = st.text_input(f"Subtitle {i+1}", slide.get('subtitle', ''))
                tit = st.text_input(f"Title {i+1}", slide.get('title', ''))
            with col2:
                if 'stats' in slide:
                    st.caption("Stats (Value | Label)")
                    new_stats = []
                    for j, stat in enumerate(slide['stats']):
                        c1, c2 = st.columns(2)
                        v = c1.text_input(f"Val {i}_{j}", stat.get('value', ''))
                        l = c2.text_input(f"Lbl {i}_{j}", stat.get('label', ''))
                        new_stats.append({"value": v, "label": l})
                    updated_slides.append({"subtitle": sub, "title": tit, "stats": new_stats, "body": ""})
                else:
                    b_val = slide.get('body', '')
                    if isinstance(b_val, list): b_val = "\n".join(b_val)
                    body = st.text_area(f"Body {i+1}", b_val)
                    body_list = [x.strip() for x in body.split('\n') if x.strip()]
                    updated_slides.append({"subtitle": sub, "title": tit, "body": body_list})
    
    st.session_state.final_slides = updated_slides
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Visuals
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-header">3️⃣ Visual Style</div>', unsafe_allow_html=True)
    
    bg_mode = st.radio("Background", ["Gradient Pattern", "Solid Color", "Video Thumbnail", "Custom Image"], horizontal=True)
    
    bg_url = None
    bg_opacity = 0.15
    
    if bg_mode == "Video Thumbnail":
        if st.session_state.thumbnail_url:
            st.image(st.session_state.thumbnail_url, width=200)
            bg_url = st.session_state.thumbnail_url
            bg_opacity = st.slider("Opacity", 0.0, 1.0, 0.15)
        else:
            st.warning("No thumbnail available.")
            
    elif bg_mode == "Custom Image":
        up_bg = st.file_uploader("Upload Background", type=['png', 'jpg'])
        if up_bg:
            st.image(up_bg, width=200)
            bg_url = up_bg
            bg_opacity = st.slider("Opacity", 0.0, 1.0, 0.15)

    if st.button("✨ Generate Carousel", type="primary", use_container_width=True):
        with st.spinner("Rendering High-Res Images..."):
            session_id = str(uuid.uuid4())
            out_dir = os.path.join("output", session_id)
            os.makedirs(out_dir, exist_ok=True)
            
            # Save Assets
            l_path = None
            if logo_file:
                l_path = os.path.join(out_dir, "logo.png")
                with open(l_path, "wb") as f: f.write(logo_file.getbuffer())
                
            final_bg_url = bg_url
            if bg_mode == "Custom Image" and bg_url:
                b_path = os.path.join(out_dir, "bg.png")
                with open(b_path, "wb") as f: f.write(bg_url.getbuffer())
                final_bg_url = os.path.abspath(b_path)
            
            # Generate
            gen = CarouselGenerator(l_path, primary_color, secondary_color, font_choice, author_handle)
            try:
                paths = gen.generate_all_slides(
                    st.session_state.final_slides, 
                    out_dir, 
                    bg_image_url=final_bg_url, 
                    bg_opacity=bg_opacity, 
                    bg_mode=bg_mode
                )
                st.session_state.generated_paths = paths
                st.session_state.output_dir = out_dir
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# Step 4: Results
if 'generated_paths' in st.session_state and st.session_state.generated_paths:
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown('<div class="step-header">🎉 Your Carousel is Ready!</div>', unsafe_allow_html=True)
    
    # Zip
    shutil.make_archive(os.path.join(st.session_state.output_dir, "carousel"), 'zip', st.session_state.output_dir)
    with open(os.path.join(st.session_state.output_dir, "carousel.zip"), "rb") as f:
        st.download_button("📦 Download All (ZIP)", f, "carousel.zip", "application/zip", type="primary")
    
    st.markdown("---")
    
    # Gallery
    cols = st.columns(3)
    for i, path in enumerate(st.session_state.generated_paths):
        with cols[i % 3]:
            st.image(path, caption=f"Slide {i+1}")
            with open(path, "rb") as f:
                st.download_button(f"⬇️ Slide {i+1}", f, f"slide_{i+1}.png", "image/png")
                
    st.markdown('</div>', unsafe_allow_html=True)
