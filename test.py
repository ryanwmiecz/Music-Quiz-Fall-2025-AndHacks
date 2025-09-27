# test.py
from spotify_test import SpotifyPlaylistExtractor
from youtube import search_youtube
import random

# --- Spotify credentials ---
SPOTIFY_CLIENT_ID = "018027c623224686a56a98aedf98f7c4"
SPOTIFY_CLIENT_SECRET = "0068d7bd972b454da81de17f6e3193d6"

def main():
    # 1️⃣ Prompt user for Spotify playlist link
    playlist_url = input("Enter Spotify playlist URL: ")

    # 2️⃣ Extract songs from Spotify
    extractor = SpotifyPlaylistExtractor(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    songs_dict = extractor.get_songs(playlist_url)

    if not songs_dict:
        print("❌ No songs found in the playlist.")
        return

    # 3️⃣ Randomly select a song
    song_number, selected_song = extractor.random_song(songs_dict)
    print(f"\n🎵 Randomly selected song: {selected_song['name']} - {selected_song['artist']}")

    # 4️⃣ Search YouTube for the song and get halfway link
    video_url, video_title = search_youtube(selected_song['name'], selected_song['artist'])

    # 5️⃣ Display YouTube link
    if video_url:
        print(f"\nYouTube video: {video_title}")
        print(f"Link (starts halfway): {video_url}")
    else:
        print("❌ No YouTube video found for this song.")

if __name__ == "__main__":
    main()
