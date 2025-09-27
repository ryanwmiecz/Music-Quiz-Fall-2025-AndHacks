import pygame





class Game():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    running = True


    def run(self):
        print("Starting game...")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Game logic and drawing goes here
            self.screen.fill((0, 255, 0)) # Clear screen with black
            pygame.display.update() # Update the display
        pygame.quit()


