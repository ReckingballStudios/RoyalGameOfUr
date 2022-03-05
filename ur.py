
# Mason Reck
# 2/22/2022
# Game of Ur with the intention of creating a neural network AI to play against

import pygame
import util.screen
import util.game


# Initialize
pygame.init()
# Change these values to turn the neural network on for each respective player
isLightAIEnabled = True
isDarkAIEnabled = False
game = util.game.Game(isLightAIEnabled, isDarkAIEnabled, 0)
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
