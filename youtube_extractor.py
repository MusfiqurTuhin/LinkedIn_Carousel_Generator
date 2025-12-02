import yt_dlp
import json
import os

def get_transcript_text(video_url):
    if not video_url:
        raise ValueError("Invalid YouTube URL")
    
    try:
        # Configure yt-dlp to download subtitles (auto or manual)
        # We don't want to download the video, just the subs
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Check for subtitles
            subtitles = info.get('subtitles', {})
            auto_subtitles = info.get('automatic_captions', {})
            
            # Prefer manual English subs
            if 'en' in subtitles:
                subs_url = subtitles['en'][0]['url']
            # Fallback to auto-generated English subs
            elif 'en' in auto_subtitles:
                subs_url = auto_subtitles['en'][0]['url']
            else:
                # Try to find any english variant
                found = False
                for lang in subtitles:
                    if lang.startswith('en'):
                        subs_url = subtitles[lang][0]['url']
                        found = True
                        break
                if not found:
                    for lang in auto_subtitles:
                        if lang.startswith('en'):
                            subs_url = auto_subtitles[lang][0]['url']
                            found = True
                            break
                if not found:
                    raise ValueError("No English subtitles found (manual or auto-generated).")

            # Download the subtitle content
            # Since we have the URL, we can fetch it using requests (lighter than letting yt-dlp write to disk and parsing)
            import requests
            response = requests.get(subs_url)
            response.raise_for_status()
            
            # Parse JSON3 format (common for YouTube subs) or VTT/SRT
            # YouTube usually returns a custom JSON format if we use the internal API, 
            # but yt-dlp exposes standard formats in the 'url'.
            # The URL usually points to a 'srv1', 'json3', or 'vtt' format.
            # Let's try to parse it as simple text if it's VTT/SRT, or JSON if it looks like JSON.
            
            content = response.text
            
            # Simple parsing logic
            if content.strip().startswith('{'):
                # JSON format (json3)
                try:
                    data = json.loads(content)
                    events = data.get('events', [])
                    text_parts = []
                    for event in events:
                        segs = event.get('segs', [])
                        for seg in segs:
                            text_parts.append(seg.get('utf8', ''))
                    return " ".join(text_parts).strip()
                except:
                    pass
            
            # Fallback: Remove timestamps from VTT/SRT-like text
            # This is a rough heuristic
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                line = line.strip()
                if not line: continue
                if '-->' in line: continue # Timestamp
                if line.isdigit(): continue # Index
                if line.startswith('WEBVTT'): continue
                if line.startswith('Kind:'): continue
                if line.startswith('Language:'): continue
                clean_lines.append(line)
            
            return " ".join(clean_lines)

    except Exception as e:
        raise ValueError(f"yt-dlp failed: {str(e)}")
