import streamlit as st
import os
import shutil
import uuid
import zipfile
from io import BytesIO
from functools import lru_cache
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content, verify_api_key
from config import COLOR_SCHEMES, FONT_OPTIONS, BACKGROUND_MODES, CONTENT_TYPES, DEFAULT_SETTINGS

# Page Config
st.set_page_config(
    page_title="LinkedIn Carousel Generator", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium CSS ---
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --primary: #714B67;
        --secondary: #017E84;
        --accent: #FF6B35;
        --bg-light: #F8FAFC;
        --bg-dark: #0F172A;
        --glass: rgba(255, 255, 255, 0.7);
        --shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    }
    
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .card-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Step Indicator */
    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(113, 75, 103, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(113, 75, 103, 0.4);
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #E2E8F0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(113, 75, 103, 0.1);
    }
    
    /* Color Pickers */
    .color-picker-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #F8FAFC;
        border-radius: 12px;
        font-weight: 600;
        color: #1E293B;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Preview Container */
    .preview-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: white;
    }
    
    /* Download Section */
    .download-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    /* Animation */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .card {
        animation: slideIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
    <div class="main-header">
        <h1>✨ AI Carousel Generator</h1>
        <p>Create stunning LinkedIn carousels in seconds with AI-powered content generation</p>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar: Global Settings ---
with st.sidebar:
    st.markdown("### ⚙️ Global Settings")
    
    # API Key
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Required for AI-powered content generation")
    if api_key:
        if st.button("✓ Verify Key", use_container_width=True):
            with st.spinner("Verifying..."):
                success, msg = verify_api_key(api_key)
                if success:
                    st.success(f"✓ {msg}")
                else:
                    st.error(f"✗ {msg}")
    
    st.divider()
    
    # Content Type Selection
    st.markdown("### 📋 Content Type")
    content_type = st.selectbox(
        "Template",
        list(CONTENT_TYPES.keys()),
        index=0,
        help="Choose the type of carousel content"
    )
    st.caption(CONTENT_TYPES[content_type]["description"])
    
    st.divider()
    
    # Design Settings
    st.markdown("### 🎨 Design Settings")
    
    # Color Scheme
    color_scheme_name = st.selectbox(
        "Color Scheme",
        list(COLOR_SCHEMES.keys()),
        index=0
    )
    scheme = COLOR_SCHEMES[color_scheme_name]
    st.caption(f"🎨 {scheme['description']}")
    
    # Custom Colors Option
    use_custom_colors = st.checkbox("🎨 Use Custom Colors")
    if use_custom_colors:
        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker("Primary", scheme['primary'])
        with col2:
            secondary_color = st.color_picker("Secondary", scheme['secondary'])
    else:
        primary_color = scheme['primary']
        secondary_color = scheme['secondary']
    
    # Font Selection
    font_name = st.selectbox(
        "Font Family",
        list(FONT_OPTIONS.keys()),
        index=0
    )
    st.caption(f"✍️ {FONT_OPTIONS[font_name]['description']}")
    
    st.divider()
    
    # Branding
    st.markdown("### 🏷️ Branding")
    author_handle = st.text_input("Author Handle", DEFAULT_SETTINGS['author_handle'])
    brand_name = st.text_input("Brand Name", DEFAULT_SETTINGS['brand_name'])
    
# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'slides_content' not in st.session_state:
    st.session_state.slides_content = None
if 'generated_paths' not in st.session_state:
    st.session_state.generated_paths = None
if 'thumbnail_url' not in st.session_state:
    st.session_state.thumbnail_url = None

# --- STEP 1: Content Source ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-header"><span class="step-badge">1</span> Content Source</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📺 YouTube Video", "📝 Manual Text"])

text_content = ""

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            label_visibility="collapsed"
        )
    with col2:
        if url:
            st.image(f"https://img.youtube.com/vi/{url.split('v=')[-1].split('&')[0]}/mqdefault.jpg", 
                    use_container_width=True)

with tab2:
    manual_text = st.text_area(
        "Paste your content here",
        height=200,
        placeholder="Enter the text content you want to transform into a carousel...",
        label_visibility="collapsed"
    )

# Add caching for content processing
@st.cache_data(show_spinner=False, ttl=3600)
def cached_process_content(text, api_key_hash, content_type):
    """Cached version of content processing to avoid regenerating same content"""
    return process_content(text, api_key=api_key_hash if api_key_hash != "no_key" else None, content_type=content_type)

if st.button("🚀 Analyze & Generate Content", type="primary", use_container_width=True):
    with st.spinner("🤖 AI is analyzing your content..."):
        # Fetch Text
        if manual_text:
            text_content = manual_text
        elif url:
            text_content = get_transcript_text(url)
            if text_content:
                st.session_state.thumbnail_url = f"https://img.youtube.com/vi/{url.split('v=')[-1].split('&')[0]}/maxresdefault.jpg"
            else:
                st.error("❌ Could not fetch transcript. Check the URL or try manual text.")
                st.stop()
        
        if text_content:
            # Generate Content with caching
            api_key_hash = api_key if api_key else "no_key"
            content, error = cached_process_content(
                text_content,
                api_key_hash,
                content_type
            )
            
            if content:
                st.session_state.slides_content = content
                st.session_state.step = 2
                st.success("✅ Content generated successfully!")
                st.rerun()
            else:
                st.error(f"❌ Generation Failed: {error}")
        else:
            st.warning("⚠️ Please provide content via YouTube URL or manual text input.")

st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 2: Review & Edit ---
if st.session_state.slides_content:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><span class="step-badge">2</span> Review & Edit Content</div>', unsafe_allow_html=True)
    
    updated_slides = []
    
    cols = st.columns(min(len(st.session_state.slides_content), 3))
    
    for i, slide in enumerate(st.session_state.slides_content):
        with st.expander(f"📄 Slide {i+1}: {slide.get('title', 'Untitled')}", expanded=(i==0)):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                sub = st.text_input(f"Subtitle {i+1}", slide.get('subtitle', ''), key=f"sub_{i}")
                
            with col2:
                tit = st.text_input(f"Title {i+1}", slide.get('title', ''), key=f"tit_{i}")
            
            # Body
            if isinstance(slide.get('body'), list):
                body = st.text_area(
                    f"Body {i+1}",
                    '\n'.join(slide['body']),
                    height=120,
                    key=f"body_{i}",
                    help="Separate bullet points with new lines"
                )
                body_list = [x.strip() for x in body.split('\n') if x.strip()]
                updated_slides.append({
                    "subtitle": sub,
                    "title": tit,
                    "body": body_list,
                    "stats": slide.get('stats')
                })
            else:
                body = st.text_area(f"Body {i+1}", slide.get('body', ''), height=100, key=f"body_{i}")
                updated_slides.append({
                    "subtitle": sub,
                    "title": tit,
                    "body": body,
                    "stats": slide.get('stats')
                })
    
    st.session_state.final_slides = updated_slides
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- STEP 3: Visual Customization ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><span class="step-badge">3</span> Visual Customization</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Background Mode**")
        bg_mode = st.selectbox(
            "Mode",
            list(BACKGROUND_MODES.keys()),
            index=1,
            label_visibility="collapsed"
        )
        st.caption(BACKGROUND_MODES[bg_mode])
    
    with col2:
        st.markdown("**Logo Upload**")
        logo_file = st.file_uploader("Logo", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if logo_file:
            st.image(logo_file, width=100)
    
    with col3:
        st.markdown("**Background Image**")
        bg_url = None
        bg_opacity = 0.15
        
        if bg_mode == "Uploaded Image":
            up_bg = st.file_uploader("Background", type=['png', 'jpg'], label_visibility="collapsed")
            if up_bg:
                st.image(up_bg, width=100)
                bg_url = up_bg
                bg_opacity = st.slider("Opacity", 0.0, 1.0, 0.15)
    
    if st.button("✨ Generate Carousel", type="primary", use_container_width=True):
        with st.spinner("🎨 Rendering high-resolution images..."):
            session_id = str(uuid.uuid4())
            out_dir = os.path.join("output", session_id)
            os.makedirs(out_dir, exist_ok=True)
            
            # Save Logo
            logo_path = None
            if logo_file:
                logo_filename = f"logo_{session_id}.png"
                logo_path = os.path.join(out_dir, logo_filename)
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            # Save Background
            bg_path = None
            if bg_url:
                bg_filename = f"bg_{session_id}.png"
                bg_path = os.path.join(out_dir, bg_filename)
                with open(bg_path, "wb") as f:
                    f.write(bg_url.getbuffer())
            
            # Generate
            try:
                generator = CarouselGenerator(
                    logo_path=logo_path,
                    brand_color=primary_color,
                    secondary_color=secondary_color,
                    font_name=font_name,
                    author_handle=author_handle,
                    brand_name=brand_name
                )
                
                paths = generator.generate_all_slides(
                    st.session_state.final_slides,
                    out_dir,
                    bg_image_url=bg_path,
                    bg_opacity=bg_opacity,
                    bg_mode=bg_mode
                )
                
                st.session_state.generated_paths = paths
                st.session_state.output_dir = out_dir
                st.success("✅ Carousel generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- STEP 4: Download Results ---
if 'generated_paths' in st.session_state and st.session_state.generated_paths:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><span class="step-badge">4</span> Download Your Carousel</div>', unsafe_allow_html=True)
    
    # Create ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, path in enumerate(st.session_state.generated_paths):
            zip_file.write(path, f"slide_{i+1}.png")
    
    zip_buffer.seek(0)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.download_button(
            "📦 Download All (ZIP)",
            zip_buffer,
            f"linkedin_carousel_{uuid.uuid4().hex[:8]}.zip",
            "application/zip",
            use_container_width=True
        )
    
    with col2:
        st.info(f"✅ Generated {len(st.session_state.generated_paths)} slides at 1080x1080px")
    
    # Preview Grid
    st.markdown("### Preview")
    cols = st.columns(min(len(st.session_state.generated_paths), 3))
    
    for i, path in enumerate(st.session_state.generated_paths):
        with cols[i % 3]:
            st.image(path, caption=f"Slide {i+1}", use_container_width=True)
            with open(path, "rb") as f:
                st.download_button(
                    f"⬇️ Download",
                    f,
                    f"slide_{i+1}.png",
                    "image/png",
                    key=f"download_{i}",
                    use_container_width=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Reset Button
    if st.button("🔄 Create Another Carousel", use_container_width=True):
        st.session_state.clear()
        st.rerun()
