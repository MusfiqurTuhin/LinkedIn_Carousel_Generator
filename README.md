# LinkedIn Carousel Generator ✨

Professional AI-powered tool to create stunning LinkedIn carousel posts in seconds.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Access at: **http://localhost:8501**

## ✨ Features

### Premium UI/UX
- Modern gradient design with glassmorphism effects
- Step-by-step wizard interface
- Real-time preview and customization
- Responsive layout

### Content Types
- **Success Story**: Client case studies with metrics
- **Tutorial**: Step-by-step how-to guides
- **Tips & Tricks**: Quick actionable advice
- **Data Insights**: Statistics and data-driven content

### Customization
- **6 Color Schemes** + custom color picker
- **5 Font Options**: Inter, Poppins, Montserrat, Roboto, Space Grotesk
- **Logo Upload**: Add your branding
- **Background Options**: Solid, gradient, or custom image
- **Dynamic Branding**: Custom author handle and brand name

### AI-Powered
- Uses latest Gemini AI models (2.0-flash-exp, 1.5-pro, 1.5-flash)
- Content-type-specific prompts
- Intelligent fallback without API key
- Automatic content structuring

### Export
- High-resolution 1080x1080 LinkedIn-ready images
- Download all as ZIP or individual slides
- PNG format for optimal quality

## 📋 Usage

1. **Configure Settings** (Sidebar):
   - Enter Gemini API key (optional)
   - Select content type
   - Choose color scheme and font
   - Set your branding

2. **Provide Content**:
   - Paste YouTube URL OR
   - Enter manual text

3. **Review & Edit**:
   - Customize slide content
   - Edit titles, subtitles, and body text

4. **Customize Visuals**:
   - Upload logo
   - Select background mode
   - Upload custom background (optional)

5. **Generate & Download**:
   - Click "Generate Carousel"
   - Download ZIP or individual slides

## 🎨 Color Schemes

- **Modern Tech** (Default): Purple & Teal
- **Startup Orange**: Orange & Navy
- **Corporate Navy**: Navy & Green
- **Creative Magenta**: Magenta & Amber
- **Professional Slate**: Slate & Sky Blue
- **Elegant Violet**: Violet & Pink

## 🔧 Configuration

Create `.streamlit/config.toml` (optional):

```toml
[theme]
primaryColor = "#714B67"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 📦 Requirements

- Python 3.8+
- Streamlit
- Google Generative AI (Gemini)
- Selenium + ChromeDriver
- Jinja2
- YouTube Transcript API

## 🎯 Output

- **Dimensions**: 1080x1080 pixels (LinkedIn carousel standard)
- **Format**: PNG
- **Quality**: High-resolution, web-optimized
- **Slides**: 5 slides per carousel

## 💡 Tips

- Use Gemini API key for AI-generated content
- Without API key, app uses smart heuristic fallback
- Upload logo in PNG format for best results
- Keep text concise for better readability
- Choose colors that match your brand

## 📝 Project Structure

```
LinkedIn_Carousel_Generator/
├── streamlit_app.py          # Main Streamlit application
├── carousel_generator.py     # Image generation engine
├── content_processor.py      # AI content processing
├── config.py                 # Configuration and presets
├── youtube_extractor.py      # YouTube transcript extraction
├── templates/
│   └── carousel_template.html # HTML/CSS template
├── output/                   # Generated carousels
└── requirements.txt          # Python dependencies
```

## 🔑 API Key

Get your free Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Enter it in the sidebar of the app

## 🎉 Recent Enhancements

- ✅ Premium UI with modern design
- ✅ 4 content types with specialized prompts
- ✅ 6 color schemes + custom colors
- ✅ 5 professional font options
- ✅ Dynamic branding support
- ✅ Enhanced template design
- ✅ ZIP download functionality
- ✅ Latest Gemini AI models

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Support

For issues or questions, create an issue in the repository.

---

**Built with ❤️ using Streamlit and Gemini AI**
