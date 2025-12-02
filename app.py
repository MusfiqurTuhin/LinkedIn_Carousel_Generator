import os
import uuid
from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
from carousel_generator import CarouselGenerator
from youtube_extractor import get_transcript_text
from content_processor import process_content

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    video_url = request.form.get('url')
    logo_file = request.files.get('logo')
    
    # Create unique session ID
    session_id = str(uuid.uuid4())
    session_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    os.makedirs(session_output_dir, exist_ok=True)
    
    logo_path = None
    if logo_file and logo_file.filename:
        filename = secure_filename(logo_file.filename)
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        logo_file.save(logo_path)
    
    # Logic
    slides_content = []
    if video_url:
        print(f"Processing URL: {video_url}")
        text = get_transcript_text(video_url)
        if text:
            slides_content = process_content(text)
        else:
            # Fallback content if transcript fails
             slides_content = [
                {"subtitle": "Error", "title": "Could not fetch transcript", "body": "Please check the URL or try another video."},
            ]
    
    if not slides_content:
         slides_content = [
            {"subtitle": "Demo", "title": "No Content Found", "body": "We couldn't extract content. Here is a demo slide."},
        ]

    # Generate Images
    generator = CarouselGenerator(logo_path=logo_path)
    generated_images = []
    
    try:
        abs_paths = generator.generate_all_slides(slides_content, session_output_dir)
        for abs_path in abs_paths:
             # Convert to relative URL for template
            filename = os.path.basename(abs_path)
            rel_url = url_for('static', filename=f'output/{session_id}/{filename}')
            generated_images.append(rel_url)
    except Exception as e:
        print(f"Generation failed: {e}")
        # Handle error gracefully or show error page
        return f"Error: {e}", 500
        
    return render_template('result.html', images=generated_images)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
