import pygame
import button as Button
import pygame
import yt_dlp
import vlc
import spotify_test
from youtube import search_youtube
import time
import random
import threading

song_start = 0
SPOTIFY_CLIENT_ID = "018027c623224686a56a98aedf98f7c4"
SPOTIFY_CLIENT_SECRET = ""
extractor = spotify_test.SpotifyPlaylistExtractor(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
testing_playlist = "https://open.spotify.com/playlist/0Gmd6cuTndpDwVEdJsPAvW"
player = ""
playing = False
loading_audio = False  # New flag to prevent multiple loading attempts

def loadAudio(url):
    global player, loading_audio
    loading_audio = True
    
    def _load_in_background():
        global player, loading_audio
        try:
            ydl_opts = {'format': 'bestaudio', 'quiet': True}  # Added quiet mode
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
            
            # Pass the URL to VLC
            player = vlc.MediaPlayer(audio_url)
            print("Audio loaded successfully")
        except Exception as e:
            print(f"Error loading audio: {e}")
            player = ""
        finally:
            loading_audio = False
    
    # Start loading in background thread
    thread = threading.Thread(target=_load_in_background, daemon=True)
    thread.start()

def playAudio():
    global player, song_start, playing
    if player and player != "":
        player.play()
        song_start = pygame.time.get_ticks()
        playing = True
    else:
        print("No audio loaded to play")

def getPlayList() -> list:
    global testing_playlist
    print (testing_playlist, "getPlayList")
    return extractor.get_songs(testing_playlist)

def updatePlaylist(value: str):
    global testing_playlist
    print ("Teae")
    testing_playlist = value

def getRandomSong(playlist: list) -> object:
    if not playlist:
        return None
    choice = random.choice(playlist)
    playlist.remove(choice)
    return choice

def searchYoutube(selected_song: object) -> str:
    return search_youtube(selected_song.name, selected_song.author)

def getUrl():
    playList = getPlayList()
    randomSong = getRandomSong(playList)
    if randomSong:
        vid_url, vid_title = searchYoutube(randomSong)
        return vid_url, vid_title
    return None, None

class Game():
    def __init__(self):
        pygame.init()
        self.screen_width = 1080
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.running = True
        self.screenType = 0
        self.last_click = 0
        self.screenTypes = ["menu", "game"]
        self.Buttons = {}
        self.initButtons()
        self.playList = {}

    def initButtons(self):
        self.Buttons["start"] = Button.Button(300, 500, 100, 50, "Start Game", pygame.font.SysFont(None, 24), (0, 128, 0), (255, 255, 255)) 
        self.Buttons["return"] = Button.Button(300, 600, 100, 50, "Return to menu", pygame.font.SysFont(None, 24), (0, 128,0), (255, 255, 255))
        self.Buttons["Play"] = Button.Button(500, 600, 100, 50, "Play", pygame.font.SysFont(None, 24), (0, 128,0), (255, 255, 255))     

    def checkClickTime(self, current_time, last_click):
        if current_time - last_click > 300:
            last_click = current_time
            return True
        return False

    def run(self):
        print("Starting game...")
        clock = pygame.time.Clock()  # Add FPS limiting
        input_box = pygame.Rect(700, 600, 100, 50)
        color_inactive = pygame.Color('white')
        color_active = pygame.Color('black')
        color = color_inactive
        active = False
        text = ''
        font = pygame.font.Font(None, 32)
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
        while self.running:
            global player, playing, loading_audio
           
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    # Change the current color of the input box.
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            print(text)
                            
                            updatePlaylist(text)
                            text = ''
                            
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        elif (event.key == pygame.K_v) and (event.mod & pygame.KMOD_CTRL): # Check for Ctrl+V
                            if pygame.scrap.get_init(): # Ensure scrap module is initialized
                                pasted_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                                if pasted_text:
                                    
                                    try:
                                        pasted_text = pasted_text.decode('utf-8', errors='ignore').replace('\x00', '')
                                        text += pasted_text
                                    except UnicodeDecodeError:
                                        text += pasted_text.decode('latin-1')
                        else:
                            text += event.unicode
                if self.screenTypes[self.screenType] == "menu":
                    if self.Buttons["start"].is_clicked(event):
                        if self.checkClickTime(current_time, self.last_click):
                            self.last_click = current_time
                            self.screenType = 1

                elif self.screenTypes[self.screenType] == "game":
                    if self.Buttons["Play"].is_clicked(event):
                        if self.checkClickTime(current_time, self.last_click):
                            self.last_click = current_time
                            playAudio()

                    if self.Buttons["return"].is_clicked(event):
                        if self.checkClickTime(current_time, self.last_click):
                            self.last_click = current_time
                            self.screenType = 0

            # Screen rendering
            if self.screenTypes[self.screenType] == "menu":
                self.screen.fill((0, 0, 0))
                self.Buttons["start"].draw(self.screen)

            elif self.screenTypes[self.screenType] == "game":
                self.screen.fill((0, 255, 0))
                self.Buttons["return"].draw(self.screen)
                self.Buttons["Play"].draw(self.screen)
                pygame.draw.rect(self.screen, (255, 0, 0), (140, 20, 800, 500))
                

                # Show loading status
                if loading_audio:
                    font = pygame.font.SysFont(None, 36)
                    loading_text = font.render("Loading audio...", True, (255, 255, 255))
                    self.screen.blit(loading_text, (400, 300))

            # Audio management logic
            if pygame.time.get_ticks() - song_start >= 5000 and player != "" and playing:
                if player:
                    player.stop()
                player = ""
                playing = False

            # Load new audio if needed (only if not already loading)
            if player == "" and testing_playlist != "" and not loading_audio:
                tempUrl, tempTitle = getUrl()
                if tempUrl:
                    loadAudio(tempUrl)
            txt_surface = font.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            # Blit the text.
            self.screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            # Blit the input_box rect.
            pygame.draw.rect(self.screen, color, input_box, 2)
            pygame.display.update()
            clock.tick(60)  # Limit to 60 FPS
        
        pygame.quit()


