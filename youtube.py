# youtube.py
from googleapiclient.discovery import build
import re

# Your YouTube API key
YOUTUBE_API_KEY = ""

def iso8601_duration_to_seconds(duration):
    """
    Convert ISO 8601 duration (e.g., PT3M15S) to seconds
    """
    pattern = re.compile(
        r'P(?:(?P<days>\d+)D)?T?(?:(?P<hours>\d+)H)?'
        r'(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?'
    )
    match = pattern.match(duration)
    if not match:
        return 0
    time_data = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    total_seconds = (
        time_data['days'] * 86400 +
        time_data['hours'] * 3600 +
        time_data['minutes'] * 60 +
        time_data['seconds']
    )
    return total_seconds

def search_youtube(song_name, song_author):
    """
    Search YouTube for a song and return a link that starts at halfway through the video
    using the youtu.be short link format.
    
    Args:
        song_name (str): Song title
        song_author (str): Artist name
        
    Returns:
        tuple: (video_url_with_halfway, video_title) or (None, None) if not found
    """
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    # Search query
    query = f"{song_name} {song_author}"
    
    search_request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    search_response = search_request.execute()
    
    if not search_response.get('items'):
        return None, None
    
    video_id = search_response['items'][0]['id']['videoId']
    video_title = search_response['items'][0]['snippet']['title']
    
    # Get actual video duration
    video_request = youtube.videos().list(
        part="contentDetails",
        id=video_id
    )
    video_response = video_request.execute()
    
    # Default start at 0s if duration not found
    halfway_seconds = 0
    if video_response.get('items'):
        duration_iso = video_response['items'][0]['contentDetails']['duration']
        duration_seconds = iso8601_duration_to_seconds(duration_iso)
        halfway_seconds = duration_seconds // 2
    
    # Use youtu.be short link format with t=XX seconds
    video_url_with_halfway = f"https://youtu.be/{video_id}?t={halfway_seconds}"
    
    return video_url_with_halfway, video_title
