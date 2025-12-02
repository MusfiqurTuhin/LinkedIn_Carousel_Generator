from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """
    Extracts video ID from various YouTube URL formats.
    """
    if not url: return None
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def get_transcript_text(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    transcript_data = None
    
    try:
        # Strategy 1: Try Standard Static Method (Common in v0.6.x)
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception:
                pass # Fall through to next strategy

        # Strategy 2: Try Instance Methods (Found in v1.2.3)
        if not transcript_data:
            try:
                ytt = YouTubeTranscriptApi()
                
                # Check for 'list' method (v1.2.3)
                if hasattr(ytt, 'list'):
                    transcript_list = ytt.list(video_id)
                    # Try to find English or first available
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        # If find_transcript fails or doesn't exist, iterate
                        if hasattr(transcript_list, 'find_transcript'):
                             try:
                                 transcript = transcript_list.find_transcript(['en'])
                             except:
                                 transcript = next(iter(transcript_list))
                        else:
                             # If transcript_list is just a list/iterable
                             transcript = next(iter(transcript_list))
                    
                    # Fetch
                    if hasattr(transcript, 'fetch'):
                        transcript_data = transcript.fetch()
                    else:
                        transcript_data = transcript # Maybe it's already data?
                
                # Check for 'fetch' shortcut (v1.2.3)
                elif hasattr(ytt, 'fetch'):
                    transcript_data = ytt.fetch(video_id)
                
            except Exception as e:
                print(f"Instance method failed: {e}")
                pass

        # Strategy 3: Try Static list_transcripts (Newer Standard)
        if not transcript_data and hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    transcript = next(iter(transcript_list))
                transcript_data = transcript.fetch()
            except Exception:
                pass

        if not transcript_data:
            raise ValueError("Could not retrieve transcript using any known method.")

        # Process Data (Handle dicts vs objects)
        full_text = ""
        # Ensure it's iterable
        if not isinstance(transcript_data, (list, tuple)):
            # If it's a single object, maybe it has text?
            if hasattr(transcript_data, 'text'):
                 return transcript_data.text
            else:
                 # Maybe it's a string?
                 return str(transcript_data)

        for item in transcript_data:
            if isinstance(item, dict):
                full_text += item.get('text', '') + " "
            elif hasattr(item, 'text'):
                full_text += item.text + " "
            else:
                full_text += str(item) + " "
                
        return full_text.strip()

    except TranscriptsDisabled:
        raise ValueError("Subtitles are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript found for this video.")
    except Exception as e:
        raise ValueError(f"Could not fetch transcript: {str(e)}")
