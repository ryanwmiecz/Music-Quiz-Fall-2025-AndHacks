import pygame
import button as Button




class Game():
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.running = True
        self.screenType = 0
        self.last_click = 0
        self.screenTypes = ["menu", "game"]
        self.Buttons = {}
        self.initButtons()

    def initButtons(self):
        self.Buttons["start"] = Button.Button(300, 500, 100, 50, "Start Game", pygame.font.SysFont(None, 24), (0, 128, 0), (255, 255, 255)) 
        self.Buttons["return"] = Button.Button(300, 500, 100, 50, "Return to menu", pygame.font.SysFont(None, 24), (0, 128,0), (255, 255, 255))     
    

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
                if self.Buttons["return"].is_clicked(event):
                    if self.checkClickTime(current_time, self.last_click):
                        self.last_click = current_time
                        self.screenType = 0 # Switch to game screen

            
            pygame.display.update() # Update the display
        pygame.quit()


