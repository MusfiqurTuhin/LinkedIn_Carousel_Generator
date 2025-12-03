import streamlit as st
import os
import shutil
import uuid
import zipfile
import json
from io import BytesIO
import streamlit.components.v1 as components
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content, verify_api_key
from config import COLOR_SCHEMES, FONT_OPTIONS, BACKGROUND_MODES, CONTENT_TYPES, DEFAULT_SETTINGS

# Page Config
st.set_page_config(
    page_title="Carousel Generator", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --primary: #714B67;
        --secondary: #017E84;
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .step-badge {
        background: var(--primary);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 10px;
    }
    
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1>✨ Carousel Generator</h1>
        <p>Turn Video & Text into Behance-level Carousels</p>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        if st.button("Verify Key"):
            success, msg = verify_api_key(api_key)
            if success:
                st.success(msg)
            else:
                st.error(msg)
    
    st.divider()
    
    st.subheader("🎨 Design System")
    color_scheme_name = st.selectbox("Color Palette", list(COLOR_SCHEMES.keys()))
    scheme = COLOR_SCHEMES[color_scheme_name]
    
    col1, col2 = st.columns(2)
    primary_color = col1.color_picker("Primary", scheme['primary'])
    secondary_color = col2.color_picker("Secondary", scheme['secondary'])
    
    font_name = st.selectbox("Typography", list(FONT_OPTIONS.keys()))
    
    st.divider()
    
    st.subheader("🏷️ Brand Identity")
    brand_name = st.text_input("Brand Name", DEFAULT_SETTINGS['brand_name'])
    author_handle = st.text_input("Handle", DEFAULT_SETTINGS['author_handle'])
    logo_file = st.file_uploader("Logo (PNG)", type=['png'])

# --- Session State ---
if 'slides' not in st.session_state:
    st.session_state.slides = []
if 'generated_html' not in st.session_state:
    st.session_state.generated_html = None
if 'generated_paths' not in st.session_state:
    st.session_state.generated_paths = None
if 'output_dir' not in st.session_state:
    st.session_state.output_dir = None

# --- Main Content ---
tab1, tab2, tab3 = st.tabs(["1. Content & Generate", "2. Edit & Refine", "3. Export"])

# TAB 1: Content
with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📥 Input Source")
    
    source_type = st.radio("Source", ["YouTube URL", "Manual Text"], horizontal=True)
    
    text_content = ""
    
    if source_type == "YouTube URL":
        url = st.text_input("Video URL", placeholder="https://youtube.com/...")
        if url:
            st.video(url)
            
    else:
        manual_text = st.text_area("Paste Text", height=200, placeholder="Paste your article, script, or notes here...")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox("Content Type", list(CONTENT_TYPES.keys()))
    with col2:
        style_seed = st.number_input("Style Seed (Randomness)", min_value=0, value=42)
        
    if st.button("🚀 Generate Carousel", type="primary", use_container_width=True):
        with st.spinner("Analyzing content and designing slides..."):
            # Get Text
            if source_type == "YouTube URL" and url:
                text_content = get_transcript_text(url)
                if not text_content:
                    st.error("Could not fetch transcript.")
                    st.stop()
            elif source_type == "Manual Text":
                text_content = manual_text
            
            if text_content:
                api_key_val = api_key if api_key else None
                slides, error = process_content(text_content, api_key=api_key_val, content_type=content_type, style_seed=style_seed)
                
                if slides:
                    st.session_state.slides = slides
                    st.success(f"Generated {len(slides)} slides!")
                    # Auto-switch to editor? Streamlit doesn't support tab switching programmatically easily, but we can show a message.
                    st.info("Go to the 'Edit & Refine' tab to see your carousel.")
                else:
                    st.error(f"Generation failed: {error}")
            else:
                st.warning("Please provide some content.")
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Editor
with tab2:
    if st.session_state.slides:
        col_edit, col_prev = st.columns([1, 1.5])
        
        with col_edit:
            st.markdown("### ✏️ Slide Editor")
            
            # Global Background Settings
            with st.expander("Background Settings", expanded=False):
                bg_mode = st.selectbox("Background Style", list(BACKGROUND_MODES.keys()), index=1)
                bg_image = st.file_uploader("Background Image", type=['png', 'jpg'])
                bg_opacity = st.slider("Image Opacity", 0.0, 1.0, 0.15)
            
            # Slide Iteration
            for i, slide in enumerate(st.session_state.slides):
                with st.expander(f"Slide {i+1}: {slide.get('layout', 'Unknown')}", expanded=(i==0)):
                    # Layout Switcher
                    new_layout = st.selectbox(
                        "Layout", 
                        ["layout-cover", "layout-quote", "layout-list", "layout-data", "layout-split", "layout-cta"],
                        index=["layout-cover", "layout-quote", "layout-list", "layout-data", "layout-split", "layout-cta"].index(slide.get('layout', 'layout-cover')),
                        key=f"layout_{i}"
                    )
                    slide['layout'] = new_layout
                    
                    # Fields
                    slide['title'] = st.text_input("Title", slide.get('title', ''), key=f"title_{i}")
                    slide['subtitle'] = st.text_input("Subtitle", slide.get('subtitle', ''), key=f"sub_{i}")
                    
                    if slide['layout'] == 'layout-list':
                        body_text = st.text_area("Items (one per line)", '\n'.join(slide.get('body', []) if isinstance(slide.get('body'), list) else [slide.get('body', '')]), key=f"body_{i}")
                        slide['body'] = [x.strip() for x in body_text.split('\n') if x.strip()]
                    else:
                        slide['body'] = st.text_area("Body", slide.get('body', ''), key=f"body_{i}")
                        
                    if slide['layout'] == 'layout-data':
                        # Simple stats editor
                        if 'stats' not in slide or not slide['stats']:
                            slide['stats'] = [{"value": "100%", "label": "Growth"}]
                        
                        st.caption("Stats")
                        for j, stat in enumerate(slide['stats']):
                            c1, c2 = st.columns(2)
                            stat['value'] = c1.text_input(f"Value {j+1}", stat.get('value', ''), key=f"val_{i}_{j}")
                            stat['label'] = c2.text_input(f"Label {j+1}", stat.get('label', ''), key=f"lbl_{i}_{j}")

        with col_prev:
            st.markdown("### 📱 Live Preview")
            
            # Generate HTML for preview
            # We need to save temp files for logo/bg if uploaded
            preview_dir = "preview_assets"
            os.makedirs(preview_dir, exist_ok=True)
            
            logo_path = None
            if logo_file:
                logo_path = os.path.join(preview_dir, "logo.png")
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            bg_path = None
            if bg_image:
                bg_path = os.path.join(preview_dir, "bg.png")
                with open(bg_path, "wb") as f:
                    f.write(bg_image.getbuffer())
            
            generator = CarouselGenerator(
                logo_path=logo_path,
                brand_color=primary_color,
                secondary_color=secondary_color,
                font_name=font_name,
                author_handle=author_handle,
                brand_name=brand_name
            )
            
            html = generator.generate_html_only(
                st.session_state.slides,
                bg_image_url=bg_path,
                bg_opacity=bg_opacity,
                bg_mode=bg_mode
            )
            
            # Render in iframe
            # Calculate height based on number of slides * slide height + gaps
            # But we want a scrollable preview.
            # Let's just show it.
            components.html(html, height=800, scrolling=True)
            
    else:
        st.info("👈 Generate some content first!")

# TAB 3: Export
with tab3:
    if st.session_state.slides:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📤 Export Carousel")
        
        if st.button("📸 Render High-Res Assets", type="primary"):
            with st.spinner("Rendering slides with Selenium (this may take a moment)..."):
                session_id = str(uuid.uuid4())
                out_dir = os.path.join("output", session_id)
                os.makedirs(out_dir, exist_ok=True)
                
                # Save assets again for the renderer
                logo_path = None
                if logo_file:
                    logo_path = os.path.join(out_dir, "logo.png")
                    logo_file.seek(0)
                    with open(logo_path, "wb") as f:
                        f.write(logo_file.read())
                
                bg_path = None
                if bg_image:
                    bg_path = os.path.join(out_dir, "bg.png")
                    bg_image.seek(0)
                    with open(bg_path, "wb") as f:
                        f.write(bg_image.read())
                
                generator = CarouselGenerator(
                    logo_path=logo_path,
                    brand_color=primary_color,
                    secondary_color=secondary_color,
                    font_name=font_name,
                    author_handle=author_handle,
                    brand_name=brand_name
                )
                
                try:
                    paths = generator.generate_all_slides(
                        st.session_state.slides,
                        out_dir,
                        bg_image_url=bg_path,
                        bg_opacity=bg_opacity,
                        bg_mode=bg_mode
                    )
                    
                    st.session_state.generated_paths = paths
                    st.session_state.output_dir = out_dir
                    st.success(f"Successfully rendered {len(paths)} slides!")
                    
                except Exception as e:
                    st.error(f"Rendering failed: {e}")

        if st.session_state.generated_paths:
            st.divider()
            
            # Prepare Downloads
            col1, col2, col3 = st.columns(3)
            
            # 1. ZIP Download
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, path in enumerate(st.session_state.generated_paths):
                    zip_file.write(path, f"slide_{i+1}.png")
            zip_buffer.seek(0)
            
            with col1:
                st.download_button(
                    "📦 Download Images (ZIP)",
                    zip_buffer,
                    "carousel_images.zip",
                    "application/zip",
                    use_container_width=True
                )
            
            # 2. PDF Download
            try:
                from PIL import Image
                pdf_buffer = BytesIO()
                images = [Image.open(p).convert('RGB') for p in st.session_state.generated_paths]
                if images:
                    images[0].save(
                        pdf_buffer, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
                    )
                    pdf_buffer.seek(0)
                    
                    with col2:
                        st.download_button(
                            "📄 Download PDF",
                            pdf_buffer,
                            "carousel.pdf",
                            "application/pdf",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"PDF Error: {e}")

            # 3. MP4 Download
            try:
                # We need to install moviepy first. If it fails, we hide the button.
                from moviepy.editor import ImageSequenceClip
                
                # Create video
                # Each slide 2 seconds
                clip = ImageSequenceClip(st.session_state.generated_paths, fps=0.5) 
                video_path = os.path.join(st.session_state.output_dir, "carousel.mp4")
                clip.write_videofile(video_path, codec="libx264", fps=24)
                
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                    
                with col3:
                    st.download_button(
                        "🎥 Download Video (MP4)",
                        video_bytes,
                        "carousel.mp4",
                        "video/mp4",
                        use_container_width=True
                    )
            except Exception as e:
                # st.warning(f"Video generation unavailable: {e}")
                pass
            
            st.divider()
            
            # Show gallery
            st.markdown("### Preview Assets")
            cols = st.columns(min(len(st.session_state.generated_paths), 4))
            for i, path in enumerate(st.session_state.generated_paths):
                with cols[i % 4]:
                    st.image(path, caption=f"Slide {i+1}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Generate content first!")
