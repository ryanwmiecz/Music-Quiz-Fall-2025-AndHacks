
import pygame
import button as Button
import yt_dlp
import vlc
import spotify_test
from youtube import search_youtube
import time
import random
import threading
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


class ScreenType(Enum):
    MENU = 0
    GAME = 1


class FeedbackState(Enum):
    NONE = 0
    CORRECT = 1
    INCORRECT = 2


@dataclass
class GameColors:
    BACKGROUND = (5, 102, 141)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 128, 0)
    INPUT_BOX = (235, 242, 250)
    LABEL_BOX = (165, 190, 0)
    DARK_GRAY = (50, 50, 50)
    RED = (255, 0, 0)
    COLOR_INACTIVE = pygame.Color('white')
    COLOR_ACTIVE = pygame.Color('black')


@dataclass
class GameSettings:
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 720
    FPS = 60
    SONG_DURATION = 20000  # 20 seconds
    FEEDBACK_DURATION = 5000  # 5 seconds
    CLICK_COOLDOWN = 300  # milliseconds
    MIN_GUESS_LENGTH = 2
    SPOTIFY_CLIENT_ID = "018027c623224686a56a98aedf98f7c4"
    SPOTIFY_CLIENT_SECRET = "d2249486472948a3883e671bdc685ba6"


class AudioManager:
    def __init__(self):
        self.player: Optional[vlc.MediaPlayer] = None
        self.song_start = 0
        self.playing = False
        self.loading_audio = False
        self.title = ""
        self.current_playlist_url = ""
        self.playlist_songs: List = []
        
        # Initialize Spotify extractor
        self.extractor = spotify_test.SpotifyPlaylistExtractor(
            GameSettings.SPOTIFY_CLIENT_ID, 
            GameSettings.SPOTIFY_CLIENT_SECRET
        )
    
    def load_audio(self, url: str) -> None:
        """Load audio in background thread"""
        if self.loading_audio:
            return
            
        self.loading_audio = True
        thread = threading.Thread(target=self._load_audio_background, args=(url,), daemon=True)
        thread.start()
    
    def _load_audio_background(self, url: str) -> None:
        """Background thread function for loading audio"""
        try:
            ydl_opts = {
                'format': 'bestaudio',
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
            
            self.player = vlc.MediaPlayer(audio_url)
            print("Audio loaded successfully")
            
        except Exception as e:
            print(f"Error loading audio: {e}")
            self.player = None
        finally:
            self.loading_audio = False
    
    def play_audio(self) -> bool:
        """Play the loaded audio starting from the middle"""
        if not self.player:
            print("No audio loaded to play")
            return False
        
        try:
            self.player.play()
            
            # Wait a moment for the player to initialize
            time.sleep(0.1)
            
            # Get total length and jump to middle
            total_length = self.player.get_length()
            if total_length > 0:
                middle_time = total_length // 2
                self.player.set_time(middle_time)
            
            self.song_start = pygame.time.get_ticks()
            self.playing = True
            print("Playing audio from middle")
            return True
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def stop_audio(self) -> None:
        """Stop the current audio"""
        if self.player:
            try:
                self.player.stop()
            except:
                pass
        self.playing = False
    
    def update_playlist(self, playlist_url: str) -> bool:
        """Update the current playlist URL and load songs"""
        self.current_playlist_url = playlist_url
        try:
            self.playlist_songs = self.extractor.get_songs(playlist_url)
            return True
        except Exception as e:
            print(f"Error loading playlist: {e}")
            self.playlist_songs = []
            return False
    
    def get_random_song(self) -> Optional[object]:
        """Get a random song from the current playlist"""
        if not self.playlist_songs:
            return None
        
        choice = random.choice(self.playlist_songs)
        self.playlist_songs.remove(choice)
        return choice
    
    def get_next_song_url(self) -> Tuple[Optional[str], Optional[str]]:
        """Get URL and title for the next random song"""
        song = self.get_random_song()
        if song:
            try:
                vid_url, vid_title = search_youtube(song.name, song.author)
                self.title = vid_title
                return vid_url, vid_title
            except Exception as e:
                print(f"Error searching YouTube: {e}")
        
        return None, None
    
    def should_load_new_song(self) -> bool:
        """Check if we should load a new song"""
        return (not self.player and 
                self.current_playlist_url and 
                not self.loading_audio)
    
    def is_song_finished(self) -> bool:
        """Check if current song has exceeded duration limit"""
        return (pygame.time.get_ticks() - self.song_start >= GameSettings.SONG_DURATION and 
                self.player and self.playing)


class FeedbackManager:
    def __init__(self):
        self.state = FeedbackState.NONE
        self.feedback_start_time = 0
    
    def show_feedback(self, is_correct: bool) -> None:
        """Start showing feedback for a guess"""
        self.state = FeedbackState.CORRECT if is_correct else FeedbackState.INCORRECT
        self.feedback_start_time = pygame.time.get_ticks()
    
    def is_showing_feedback(self) -> bool:
        """Check if feedback should be displayed"""
        if self.state == FeedbackState.NONE:
            return False
        
        elapsed = pygame.time.get_ticks() - self.feedback_start_time
        if elapsed >= GameSettings.FEEDBACK_DURATION:
            self.state = FeedbackState.NONE
            return False
        
        return True
    
    def get_feedback_state(self) -> FeedbackState:
        """Get current feedback state"""
        return self.state if self.is_showing_feedback() else FeedbackState.NONE


class InputHandler:
    def __init__(self):
        self.input_box = pygame.Rect(200, 650, 680, 50)
        self.active = False
        self.text = ""
        self.font = pygame.font.Font(None, 32)
        
        # Initialize clipboard
        try:
            pygame.scrap.init()
            pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)
        except pygame.error:
            print("Clipboard functionality not available")
    
    def handle_click(self, pos: Tuple[int, int]) -> None:
        """Handle mouse click on input box"""
        self.text = ""
        self.active = self.input_box.collidepoint(pos)
    
    def handle_keydown(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard input, return text if Enter was pressed"""
        if not self.active:
            return None
        
        if event.key == pygame.K_RETURN:
            result = self.text
            self.text = ""  # Clear input after submission
            return result
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
            self._handle_paste()
        else:
            self.text += event.unicode
        
        return None
    
    def _handle_paste(self) -> None:
        """Handle Ctrl+V paste operation"""
        try:
            if pygame.scrap.get_init():
                pasted_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                if pasted_text:
                    try:
                        pasted_text = pasted_text.decode('utf-8', errors='ignore').replace('\x00', '')
                        self.text += pasted_text
                    except UnicodeDecodeError:
                        self.text += pasted_text.decode('latin-1')
        except Exception as e:
            print(f"Paste operation failed: {e}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the input box and text"""
        # Draw input box
        pygame.draw.rect(screen, GameColors.INPUT_BOX, self.input_box)
        pygame.draw.rect(screen, GameColors.BLACK, self.input_box, 2)
        
        # Draw text
        txt_surface = self.font.render(self.text, True, GameColors.BLACK)
        screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 15))


class ImageManager:
    def __init__(self):
        self.images = {}
        self._load_images()
    
    def _load_images(self) -> None:
        """Load and cache all game images"""
        start_path = "assets\\"
        image_configs = [
            ("start", "start.png", (250, 210)),
            ("robot1", "robot1.png", (600, 480)),
            ("happy1", "happy1.png", (600, 480)),
            ("sad1", "sad1.png", (600, 480))
        ]
        
        for name, filename, size in image_configs:
            try:
                img = pygame.image.load(f"{start_path}{filename}").convert_alpha()
                self.images[name] = pygame.transform.smoothscale(img, size)
            except pygame.error as e:
                print(f"Error loading image {filename}: {e}")
                # Create placeholder
                placeholder = pygame.Surface(size)
                placeholder.fill(GameColors.GREEN if name == "start" else GameColors.RED)
                self.images[name] = placeholder
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get cached image by name"""
        return self.images.get(name)


class Game:
    def __init__(self):
        pygame.init()
        
        # Initialize display
        self.screen = pygame.display.set_mode((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        pygame.display.set_caption("Music Guessing Game")
        
        # Game state
        self.running = True
        self.screen_type = ScreenType.MENU
        self.last_click = 0
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.audio_manager = AudioManager()
        self.input_handler = InputHandler()
        self.feedback_manager = FeedbackManager()
        self.image_manager = ImageManager()
        self.buttons = self._init_buttons()
        
        # Fonts (cache them)
        self.font = pygame.font.Font(None, 32)
        self.loading_font = pygame.font.SysFont(None, 36)
        
        # Pre-render static text surfaces
        self.static_texts = self._create_static_texts()
    
    def _init_buttons(self) -> dict:
        """Initialize all game buttons"""
        return {
            "start": Button.Button(420, 520, 240, 100, "Start Game", 
                                 pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "return": Button.Button(50, 650, 100, 50, "Return to menu", 
                                  pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "Play": Button.Button(500, 500, 100, 50, "Play", 
                                pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "Short": Button.Button(50, 200, 100, 50, "Short", 
                                pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "Medium": Button.Button(50,300, 100, 50, "Medium", 
                                pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "Long": Button.Button(50, 400, 100, 50, "Long", 
                                pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE),
            "Skip": Button.Button(50, 500, 100, 50, "Skip", 
                                pygame.font.SysFont(None, 24), GameColors.GREEN, GameColors.WHITE)
        }
    
    def _create_static_texts(self) -> dict:
        """Pre-render static text surfaces for better performance"""
        return {
            "playlist_label": self.font.render("Insert Playlist Link Below", True, GameColors.BLACK),
            "guess_label": self.font.render("Put Your Guess Here", True, GameColors.BLACK),
            "loading": self.loading_font.render("Loading audio...", True, GameColors.WHITE)
        }
    
    def _can_click(self) -> bool:
        """Check if enough time has passed since last click"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click > GameSettings.CLICK_COOLDOWN:
            self.last_click = current_time
            return True
        return False
    
    def _check_guess(self, guess: str, title: str) -> bool:
        """Check if the guess is correct"""
        if not guess or not title or len(guess) <= GameSettings.MIN_GUESS_LENGTH:
            return False
        return guess.lower() in title.lower()
    
    def _handle_events(self) -> None:
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.input_handler.handle_click(event.pos)
                self._handle_button_clicks(event)
            
            elif event.type == pygame.KEYDOWN:
                entered_text = self.input_handler.handle_keydown(event)
                if entered_text:
                    self._handle_text_input(entered_text)
    
    def _handle_button_clicks(self, event: pygame.event.Event) -> None:
        """Handle button click events"""
        if not self._can_click():
            return
        
        if self.screen_type == ScreenType.MENU:
            if self.buttons["start"].is_clicked(event):
                self.screen_type = ScreenType.GAME
        
        elif self.screen_type == ScreenType.GAME:
            if self.buttons["Play"].is_clicked(event):
                self.audio_manager.play_audio()
            elif self.buttons["return"].is_clicked(event):
                self.screen_type = ScreenType.MENU
            elif self.buttons["Short"].is_clicked(event):
                GameSettings.SONG_DURATION = 10000
            elif self.buttons["Medium"].is_clicked(event):
                GameSettings.SONG_DURATION = 30000
            elif self.buttons["Long"].is_clicked(event):
                GameSettings.SONG_DURATION = 50000
            elif self.buttons["Skip"].is_clicked(event):
                self.audio_manager.stop_audio()
                self.audio_manager.player = None
                self._update_audio()
    
    def _handle_text_input(self, text: str) -> None:
        """Handle text input based on current screen"""
        if self.screen_type == ScreenType.MENU:
            if self.audio_manager.update_playlist(text):
                url, title = self.audio_manager.get_next_song_url()
                if url:
                    self.audio_manager.load_audio(url)
        
        elif self.screen_type == ScreenType.GAME:
            is_correct = self._check_guess(text, self.audio_manager.title)
            self.feedback_manager.show_feedback(is_correct)
            if is_correct:
                print(f"Correct guess: '{text}' matches '{self.audio_manager.title}'")
            else:
                print(f"Incorrect guess: '{text}' doesn't match '{self.audio_manager.title}'")
    
    def _update_audio(self) -> None:
        """Update audio state and load new songs as needed"""
        # Stop song if it's been playing too long
        if self.audio_manager.is_song_finished():
            self.audio_manager.stop_audio()
            self.audio_manager.player = None
        
        # Load new song if needed
        if self.audio_manager.should_load_new_song():
            url, title = self.audio_manager.get_next_song_url()
            if url:
                self.audio_manager.load_audio(url)
    
    def _draw_common_elements(self) -> None:
        """Draw elements common to both screens"""
        # Draw label box
        pygame.draw.rect(self.screen, GameColors.LABEL_BOX, (400, 600, 280, 50))
        pygame.draw.rect(self.screen, GameColors.BLACK, (400, 600, 280, 50), 2)
        
        # Draw input box
        self.input_handler.draw(self.screen)
    
    def _draw_menu(self) -> None:
        """Draw the menu screen"""
        self.screen.fill(GameColors.BACKGROUND)
        
        # Draw background circle
        pygame.draw.circle(self.screen, GameColors.BLACK, (540, 300), 500)
        
        # Draw images
        robot_img = self.image_manager.get_image("robot1")
        start_img = self.image_manager.get_image("start")
        
        if robot_img:
            self.screen.blit(robot_img, (250, 50))
        if start_img:
            self.screen.blit(start_img, (420, 480))
        
        # Draw common elements
        self._draw_common_elements()
        
        # Draw label text (use pre-rendered surface)
        self.screen.blit(self.static_texts["playlist_label"], (410, 615))
    
    def _draw_game(self) -> None:
        """Draw the game screen"""
        self.screen.fill(GameColors.DARK_GRAY)
        
        # Draw main game area
        pygame.draw.rect(self.screen, GameColors.RED, (140, 20, 800, 500))
        
        # Draw appropriate character based on feedback
        feedback_state = self.feedback_manager.get_feedback_state()
        if feedback_state == FeedbackState.CORRECT:
            happy_img = self.image_manager.get_image("happy1")
            if happy_img:
                self.screen.blit(happy_img, (250, 50))
        elif feedback_state == FeedbackState.INCORRECT:
            sad_img = self.image_manager.get_image("sad1")
            if sad_img:
                self.screen.blit(sad_img, (250, 50))
        
        # Draw buttons
        self.buttons["return"].draw(self.screen)
        self.buttons["Play"].draw(self.screen)
        self.buttons["Short"].draw(self.screen)
        self.buttons["Medium"].draw(self.screen)
        self.buttons["Long"].draw(self.screen)
        self.buttons["Skip"].draw(self.screen)
        
        # Draw common elements
        self._draw_common_elements()
        
        # Draw label text (use pre-rendered surface)
        self.screen.blit(self.static_texts["guess_label"], (410, 615))
        
        # Show loading status
        if self.audio_manager.loading_audio:
            self.screen.blit(self.static_texts["loading"], (400, 300))
    
    def run(self) -> None:
        """Main game loop"""
        print("Starting game...")
        
        while self.running:
            self._handle_events()
            self._update_audio()
            
            # Render based on current screen
            if self.screen_type == ScreenType.MENU:
                self._draw_menu()
            else:  # GAME screen
                self._draw_game()
            
            pygame.display.flip()  # More efficient than update()
            self.clock.tick(GameSettings.FPS)
        
        # Cleanup
        self.audio_manager.stop_audio()
        pygame.quit()