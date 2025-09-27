import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import re
import random


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
        """Extract playlist ID from Spotify URL"""
        match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
        return match.group(1) if match else playlist_url
    
    def random_song(self, songs_dict):
        """Randomly select a song from the dictionary"""
        if not songs_dict:
            print("❌ No songs available!")
            return None
        
        random_key = random.choice(list(songs_dict.keys()))
        selected_song = songs_dict[random_key]
        
        return random_key, selected_song
    
    def get_songs(self, playlist_url):
        """Get songs from playlist URL and store in dictionary"""
        token = self.get_access_token()
        if not token:
            print("❌ Could not get access token")
            return {}
        
        playlist_id = self.extract_playlist_id(playlist_url)
        
        try:
            # Get playlist tracks
            url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            req = urllib.request.Request(
                url, 
                headers={'Authorization': f'Bearer {token}'}
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            songs_dict = {}
            for i, item in enumerate(data['items'], 1):
                track = item.get('track')
                if track:
                    song_info = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track.get('preview_url')
                    }
                    songs_dict[i] = song_info
            
            return songs_dict
            
        except Exception as e:
            print(f"❌ Error getting songs: {e}")
            return {}


# Simple usage
def main():
    # Your Spotify credentials
    extractor = SpotifyPlaylistExtractor(
        client_id="018027c623224686a56a98aedf98f7c4",
        client_secret="0068d7bd972b454da81de17f6e3193d6"
    )
    
    # Get playlist URL from user
    playlist_url = input("Enter Spotify playlist URL: ")
    
    # Get songs as dictionary
    songs_dict = extractor.get_songs(playlist_url)
    
    if songs_dict:
        print(f"\n🎵 Found {len(songs_dict)} songs and added to dictionary!")
        print("-" * 50)
        
        # Display all songs
        for key, song in songs_dict.items():
            print(f"{key}. {song['name']} - {song['artist']}")
        
        # Ask to randomly select
        print("\n" + "="*50)
        choice = input("Randomly select a song? (y/n): ").lower()
        
        if choice == 'y':
            song_number, selected_song = extractor.random_song(songs_dict)
            print(f"\n🎲 RANDOMLY SELECTED SONG:")
            print(f"#{song_number}: {selected_song['name']} - {selected_song['artist']}")
            
            if selected_song['preview_url']:
                print(f"🎧 Preview: {selected_song['preview_url']}")
            else:
                print(f"❌ No preview available")
        
    else:
        print("❌ No songs found!")


if __name__ == "__main__":
    main()