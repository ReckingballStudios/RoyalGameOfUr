
# File containing all variables for the screen

import pygame

# fontLarge = pygame.font.Font('freesansbold.ttf', 32)
# fontSmall = pygame.font.Font('freesansbold.ttf', 16)

class Screen:
    def __init__(self, width, height, FPS):
        self.width = width
        self.height = height
        self.FPS = FPS
        self.fpsClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        icon = pygame.image.load('sprites/icon.png')
        pygame.display.set_caption("The Royal Game of Ur")
        pygame.display.set_icon(icon)


