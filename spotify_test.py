import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta




class Song:
    def __init__(self, name, author):
        self.name = name
        self.author = author

    def __str__(self):
        return f"{self.name} - {self.author}"



class SpotifyPlaylistExtractor:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None



    def get_access_token(self):
        """Get Spotify access token"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        try:
            data = urllib.parse.urlencode({
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://accounts.spotify.com/api/token',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                method='POST'
            )

            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))

            self.access_token = response_data['access_token']
            self.token_expiry = datetime.now() + timedelta(seconds=response_data['expires_in'] - 300)
            return self.access_token

        except Exception as e:
            print(f"Error getting token: {e}")
            return None

    def extract_playlist_id(self, playlist_url):
        """Extract playlist ID from URL"""
        try:
            return playlist_url.split("/")[-1].split("?")[0]
        except IndexError:
            return None

    def get_songs(self, playlist_url):
        """Get songs from playlist URL as a list of Song objects"""
        token = self.get_access_token()
        if not token:
            print("❌ Could not get access token")
            return []

        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("❌ Invalid playlist URL")
            return []

        try:
            url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {token}'}
            )

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

            songs_list = []
            for item in data['items']:
                track = item.get('track')
                if track:
                    song = Song(track['name'], track['artists'][0]['name'])
                    songs_list.append(song)

            return songs_list

        except Exception as e:
            print(f"❌ Error getting songs: {e}")
            return []

