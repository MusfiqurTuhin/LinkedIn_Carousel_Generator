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
    
    try:
        # Method 1: Try the standard static method (most common usage)
        # This automatically looks for 'en' (manual then generated)
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript_list])
        except AttributeError:
            # If static method doesn't exist (version mismatch), proceed to instance method
            pass
        except Exception as e:
            # If get_transcript fails (e.g. translation needed), try list_transcripts
            print(f"Standard get_transcript failed: {e}")
            pass

        # Method 2: Use list_transcripts (Instance or Static depending on version)
        # We try to instantiate first as we saw earlier it might be a class
        try:
            ytt = YouTubeTranscriptApi()
            if hasattr(ytt, 'list_transcripts'):
                transcript_list = ytt.list_transcripts(video_id)
            else:
                # Try static
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception:
            # Fallback for older versions or static-only
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Iterate to find the best transcript
        transcript = None
        
        # 1. Try Manual English
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            pass
            
        # 2. Try Generated English
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                pass
        
        # 3. Try Any English (Translated?)
        if not transcript:
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                pass

        # 4. Fallback: Take the first available and translate to English
        if not transcript:
            try:
                # Just get the first one
                first_transcript = next(iter(transcript_list))
                # Translate to English
                transcript = first_transcript.translate('en')
            except Exception as e:
                print(f"Translation failed: {e}")
                # If translation fails, just use the original
                transcript = next(iter(transcript_list))

        # Fetch the data
        # Note: In some versions fetch() returns objects, in others dicts.
        # We handle both.
        data = transcript.fetch()
        
        full_text = ""
        for item in data:
            if isinstance(item, dict):
                full_text += item['text'] + " "
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
