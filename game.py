import pygame
import button as Button
import tkinter as tk
import pygame
import yt_dlp
import vlc
import time

# Your YouTube link
url = "https://www.youtube.com/watch?t=107&v=hHUbLv4ThOo&feature=youtu.be"

# Use yt_dlp to get the direct audio stream URL (no download)
ydl_opts = {'format': 'bestaudio'}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    audio_url = info['url']  # direct link to audio

# Pass the URL to VLC
player = vlc.MediaPlayer(audio_url)








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
        if current_time - last_click > 300:  # 300 milliseconds debounce time
            last_click = current_time
            return True
        return False


    def run(self):
        print("Starting game...")

        while self.running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Game logic and drawing goes here
            if (self.screenTypes[self.screenType] == "menu"):
                self.screen.fill((0, 0, 0)) # Clear screen with black
                self.Buttons["start"].draw(self.screen)
                if self.Buttons["start"].is_clicked(event):
                    if self.checkClickTime(current_time, self.last_click):
                        self.last_click = current_time
                        self.screenType = 1 # Switch to game screen


            elif (self.screenTypes[self.screenType] == "game"):
                self.screen.fill((0, 255, 0)) # Clear screen with blac
                self.Buttons["return"].draw(self.screen)
                self.Buttons["Play"].draw(self.screen)
                if self.Buttons["Play"].is_clicked(event):
                    if self.checkClickTime(current_time, self.last_click):
                        self.last_click = current_time
                        player.play()
                        player.set_time(70000)

                pygame.draw.rect(self.screen, (255, 0, 0), (140, 20, 800, 500)) # Draw a red square
                if self.Buttons["return"].is_clicked(event):
                    if self.checkClickTime(current_time, self.last_click):
                        self.last_click = current_time
                        self.screenType = 0 # Switch to game screen

            
            pygame.display.update() # Update the display
        pygame.quit()


