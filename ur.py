
# Mason Reck
# 2/22/2022
# Game of Ur with the intention of creating a neural network AI to play against

import pygame
import random
import math
import util.screen
import util.game


# Initialize
pygame.init()
game = util.game.Game(True, False)
screen = util.screen.Screen(512, 400, 60)

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handleInput(event)

    game.update()
    game.draw(screen.screen)
    pygame.display.update()
    screen.fpsClock.tick(screen.FPS)
