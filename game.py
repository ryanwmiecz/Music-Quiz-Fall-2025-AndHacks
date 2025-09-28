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
title = ""
correct = False
time_from_guess = 0

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
        totalLen = player.get_length()
        if totalLen > 0:
            half = totalLen//2
            player.set_time(half)
        song_start = pygame.time.get_ticks()
        playing = True
        print ("playing")
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
        self.Buttons["start"] = Button.Button(420, 520, 240, 100, "Start Game", pygame.font.SysFont(None, 24), (0, 128, 0), (255, 255, 255)) 
        self.Buttons["return"] = Button.Button(50, 650, 100, 50, "Return to menu", pygame.font.SysFont(None, 24), (0, 128,0), (255, 255, 255))
        self.Buttons["Play"] = Button.Button(500, 500, 100, 50, "Play", pygame.font.SysFont(None, 24), (0, 128,0), (255, 255, 255))     

    def checkClickTime(self, current_time, last_click):
        if current_time - last_click > 300:
            last_click = current_time
            return True
        return False

    def run(self):
        start_path = "assets\\"
        try:
            start_image = pygame.image.load(start_path+"start.png").convert_alpha()
            start_image = pygame.transform.smoothscale(start_image, (250, 210))
            robot1_image = pygame.image.load(start_path+"robot1.png").convert_alpha()
            robot1_image = pygame.transform.smoothscale(robot1_image, (600, 480))
            happy1_image = pygame.image.load(start_path+"happy1.png").convert_alpha()
            happy1_image = pygame.transform.smoothscale(happy1_image, (600, 480))
            sad1_image = pygame.image.load(start_path+"sad1.png").convert_alpha()
            sad1_image = pygame.transform.smoothscale(sad1_image, (600, 480))

        except pygame.error as e:
            print(f"Error loading image: {e}")

        print("Starting game...")
        clock = pygame.time.Clock()  # Add FPS limiting
        input_box = pygame.Rect(200,650,680,50)
        color_inactive = pygame.Color('white')
        color_active = pygame.Color('black')
        color = color_inactive
        active = False
        global title, time_from_guess, correct
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
                        if event.key == pygame.K_RETURN and (self.screenTypes[self.screenType] == "menu" or self.screenTypes[self.screenType] == "game"):
                            print(text)
                            if (self.screenTypes[self.screenType] == "menu"):
                                updatePlaylist(text)
                                
                                tempUrl, title = getUrl()
                                print(title)
                                if tempUrl:
                                    loadAudio(tempUrl)
                                text = ''
                            elif (self.screenTypes[self.screenType] == "game"):
                                time_from_guess = pygame.time.get_ticks()

                                if (text and title):
                                    if text.lower() in title.lower() and len(text)>2:
                                        print("nice")
                                        correct = True
                                    else:
                                        correct = False
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
                self.screen.fill((5, 102, 141))
                pygame.draw.circle(self.screen,(0,0,0),(540,300),500)
                self.screen.blit(start_image, (420, 480))
                self.screen.blit(robot1_image, (250, 50))
                #self.Buttons["start"].draw(self.screen)
                pygame.draw.rect(self.screen, (235, 242, 250), (200,650,680,50))
                pygame.draw.rect(self.screen, (0,0,0), (200,650,680,50), 2)
                pygame.draw.rect(self.screen, (165, 190, 0), (400,600,280,50))
                pygame.draw.rect(self.screen, (0,0,0), (400,600,280,50), 2)
                txt_surface = font.render("Insert Playlist Link Below", True, (0,0,0))
                # Resize the box if the text is too long.
                # Blit the text.
                self.screen.blit(txt_surface, (410, 615))
                txt_surface = font.render(text, True, (0,0,0))
                # Resize the box if the text is too long.
                # Blit the text.
                self.screen.blit(txt_surface, (210, 665))
                # Blit the input_box rect.
                


            elif self.screenTypes[self.screenType] == "game":
                pygame.draw.rect(self.screen, (255, 0, 0), (140, 20, 800, 500))
                self.screen.fill((50, 50, 50))
                self.Buttons["return"].draw(self.screen)
                self.Buttons["Play"].draw(self.screen)
                pygame.draw.rect(self.screen, (235, 242, 250), (200,650,680,50))
                pygame.draw.rect(self.screen, (0,0,0), (200,650,680,50), 2)
                pygame.draw.rect(self.screen, (165, 190, 0), (400,600,280,50))
                pygame.draw.rect(self.screen, (0,0,0), (400,600,280,50), 2)
                txt_surface = font.render("Put Your Guess Here", True, (0,0,0))
                self.screen.blit(txt_surface, (410, 615))
                txt_surface = font.render(text, True, (0,0,0))
                # Resize the box if the text is too long.
                # Blit the text.
                self.screen.blit(txt_surface, (210, 665))
                
                

                # Show loading status
                if loading_audio:
                    font = pygame.font.SysFont(None, 36)
                    loading_text = font.render("Loading audio...", True, (255, 255, 255))
                    self.screen.blit(loading_text, (400, 300))

            # Audio management logic
            if pygame.time.get_ticks() - song_start >= 20000 and player != "" and playing:
                if player:
                    player.stop()
                player = ""
                playing = False

            # Load new audio if needed (only if not already loading)
            if player == "" and testing_playlist != "" and not loading_audio:
                tempUrl, title = getUrl()
                print(title)
                if tempUrl:
                    loadAudio(tempUrl)
            
            if pygame.time.get_ticks() - time_from_guess <= 5000 and pygame.time.get_ticks() > 5001:
                if correct == True:
                    self.screen.blit(happy1_image, (250, 50))
                else:
                    self.screen.blit(sad1_image, (250, 50))
            pygame.display.update()
            clock.tick(60)  # Limit to 60 FPS
        
        pygame.quit()


