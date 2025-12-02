from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
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
    # fail?
    return None

def get_transcript_text(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    try:
        # Instantiate the API
        ytt_api = YouTubeTranscriptApi()
        
        # Use the fetch method which is a shortcut for list().find().fetch()
        # It defaults to ['en']
        transcript_data = ytt_api.fetch(video_id)
        
        # The fetch method returns a FetchedTranscript object? 
        # Help says -> FetchedTranscript. 
        # But usually fetch() returns the list of dicts directly in older versions.
        # Let's check if it returns a list or object. 
        # The help says "-> FetchedTranscript".
        # But the example says "print(transcript.fetch())" which usually prints the list.
        # Let's assume it returns the list of dicts based on standard behavior, 
        # or if it returns an object, we might need to access .data or similar.
        # Wait, the help says: "Retrieves the transcript... This is just a shortcut for calling ... .fetch()"
        # And .fetch() on a Transcript object returns the list of dicts.
        # So ytt_api.fetch(video_id) should return the list of dicts.
        
        # Combine text
        # In this version, it returns objects with .text attribute
        full_text = " ".join([t.text for t in transcript_data])
        return full_text

    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None
