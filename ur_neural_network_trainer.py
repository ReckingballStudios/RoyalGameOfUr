# Mason Reck
# 2/22/2022
# Game of Ur with the intention of creating a neural network AI to play against

# This file is intended to have numerous neural networks play against each other and improve
# The plan is to use Neural Evolution through Augmenting Topologies


import pygame
import util.screen
import util.game
import random


# Initialize
pygame.init()

font = pygame.font.Font('freesansbold.ttf', 32)
trainingState = "Training"
trainingData = open("data/NEAT.txt", "r")
generation = int(trainingData.read())
trainingData.close()
numGames = 50
volatility = 0.001
screen = util.screen.Screen(512, 400, 60)

def initializeGames():
    answer = []
    for i in range(numGames):
        answer.append(util.game.Game(True, True, i * 2))  # GameID will always be an even number
    return answer
games = initializeGames()

def drawGen():
    pixelX = 300
    pixelY = 360
    out = "Gen: " + str(generation)
    text = font.render(out, True, (10, 10, 10))
    textRect = text.get_rect()
    screen.screen.blit(text, (textRect.x + pixelX, textRect.y + pixelY))

def advanceGeneration():
    global generation
    generation += 1
    winningNN = []
    losingNN = []
    for i in range(numGames):
        ran = random.randint(0, 1)
        if games[i].gameState == "Light Tokens Win!":
            winningNN.append(games[i].light.neuralNetwork.fileName)
            losingNN.append(games[i].dark.neuralNetwork.fileName)
        elif games[i].gameState == "Dark Tokens Win!":
            winningNN.append(games[i].dark.neuralNetwork.fileName)
            losingNN.append(games[i].light.neuralNetwork.fileName)
        # TODO delete random winner selection
        elif ran == 0:
            winningNN.append(games[i].light.neuralNetwork.fileName)
            losingNN.append(games[i].dark.neuralNetwork.fileName)
        else:
            winningNN.append(games[i].dark.neuralNetwork.fileName)
            losingNN.append(games[i].light.neuralNetwork.fileName)

    for i in range(numGames):
        winFile = open(winningNN[i], "r")
        winningWeights = []
        for j in range(2418):
            winningWeights.append(float(winFile.readline()))
        winFile.close()

        # Mutate new weights
        newWeights = []
        for j in range(2418):
            newWeight = winningWeights[j] + (volatility * (2*random.random()-1))
            if newWeight > 1:
                newWeight = 1
            if newWeight < -1:
                newWeight = -1
            newWeights.append(newWeight)

        # Find a random losing neural network and write the new weights
        newNNScramble = scramble()
        mutatedFile = open(losingNN[newNNScramble[i]], "w")
        for j in range(2418):
            mutatedFile.write(str(newWeights[j]) + "\n")
        mutatedFile.close()

def scramble():
    numbers = []
    for i in range(numGames):
        numbers.append(i)
    answer = []
    while len(numbers) > 0:
        answer.append(numbers.pop(random.randint(0, len(numbers)-1)))
    return answer

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            trainingData.close()
            running = False


    for i in range(numGames):
        games[i].update()

    # Check to see if most all the games are finished
    numGamesFinished = 0
    for i in range(numGames):
        if games[i].gameState == "Light Tokens Win!" or games[i].gameState == "Dark Tokens Win!":
            numGamesFinished += 1

        if i == numGames - 1 and not trainingState == "Generation Finished!" and numGamesFinished == numGames:
            trainingState = "Generation Finished!"
            print(trainingState + " Games Finished: " + str(numGamesFinished))
            trainingData = open("data/NEAT.txt", "w")
            trainingData.write(str(generation+1))
            trainingData.close()


    # If the generation is finished playing, move to the next generation (destroy unfit networks, breed fit networks)
    if trainingState == "Generation Finished!":
        advanceGeneration()
        trainingState = "Training"
        numGamesFinished = 0
        games.clear()
        games = initializeGames()


    games[0].draw(screen.screen)
    drawGen()
    pygame.display.update()
    screen.fpsClock.tick(screen.FPS)

