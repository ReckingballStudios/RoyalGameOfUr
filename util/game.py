# File containing game variables

import pygame
import random
import math


class Game:
    ###### Tile Layout #######
    # 0  1  2  3  4  5  6  7
    # 8  9  10 11 12 13 14 15
    # 16 17 18 19 20 21 22 23
    ##########################
    # Global Variables
    pathLen = 16
    lightPath = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5]  # Path that player 1 has to take to score
    darkPath = [20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21]  # Path that player 2 has to take to score
    # Logical AI Weights (Importance of the tile the token is currently on)
    tileWeights = [0.3, 0.18, 0.17, 0.15, 0.16, 0.26, 0.3, 0.28, 0, 0.29, 0.5, 0.4, 0.45, 0.55, 0.1, 0.15]
    timerAIMax = 35

    ### INITIALIZATION ###
    def __init__(self, isLightAIEnabled, isDarkAIEnabled, gameID):
        # GameID will always be an even number, as there are 2 players per game, each needing a unique ID
        self.gameID = gameID
        self.gameState = self.getRandomStart()
        self.numTurns = 0
        self.light = Player("light", isLightAIEnabled, self.gameID)
        self.dark = Player("dark", isDarkAIEnabled, self.gameID + 1)
        self.fontLarge = pygame.font.Font('freesansbold.ttf', 32)
        self.fontSmall = pygame.font.Font('freesansbold.ttf', 16)
        self.timerAI = 0
        self.tiles = []
        self.initializeTiles()
        if isLightAIEnabled and isDarkAIEnabled:
            Game.timerAIMax = 0

    def initializeTiles(self):
        ###### Tile Layout #######
        # 0  1  2  3  4  5  6  7
        # 8  9  10 11 12 13 14 15
        # 16 17 18 19 20 21 22 23
        ##########################
        # Initialize each tile
        for i in range(Tile.numTiles):
            tileX = 0  # Tile's X Coordinate
            tileY = 0  # Tile's Y Coordinate
            if i < 8:  # Upper Row
                tileX = i * Tile.lengthPix
                tileY = 0
            elif i < 16:  # Middle Row
                tileX = (i - 8) * Tile.lengthPix
                tileY = Tile.lengthPix
            elif i < 24:  # Lower Row
                tileX = (i - 16) * Tile.lengthPix
                tileY = Tile.lengthPix * 2

            # We don't want all the games to load the image if they aren't going to use it
            tileImage = Tile.types[i]
            if self.gameID != 0:
                tileImage = -1

            self.tiles.append(Tile(tileX, tileY, False, False, False, False, tileImage, self.gameID))
            if i == 0 or i == 6 or i == 11 or i == 16 or i == 22:
                self.tiles[i].isReroll = True

        # Add specific attributes to the
        self.tiles[11].isImmortal = True  # Tile 11 is the IMMORTAL square
        self.tiles[4].isOccupiedByLight = True
        self.tiles[20].isOccupiedByDark = True

    ### GAME FUNCTIONS ###
    def update(self):
        self.updateAI()
        self.updateWin()

    def updateWin(self):
        maxTurns = 500
        winner = 1
        if self.light.numTokensScored > self.dark.numTokensScored:
            winner = 0
        if ((self.numTurns >= maxTurns and winner == 0) or self.light.numTokensScored == 7) \
                and not self.gameState == "Light Tokens Win!":
            self.gameState = "Light Tokens Win!"
            print(str(int(self.gameID/2)) + ": " + self.gameState + " Turns: " + str(self.numTurns))
        if ((self.numTurns >= maxTurns and winner == 1) or self.dark.numTokensScored == 7) \
                and not self.gameState == "Dark Tokens Win!":
            self.gameState = "Dark Tokens Win!"
            print(str(int(self.gameID/2)) + ": " + self.gameState + " Turns: " + str(self.numTurns))

    def handleInput(self, event):
        self.handleMouse(event)
        self.handleKeyboard(event)

    def handleMouse(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            # Mouse Tile Collisions
            if self.gameState == "lights move" or self.gameState == "darks move":
                for i in range(Tile.numTiles):
                    distanceX = pos[0] - self.tiles[i].x
                    distanceY = pos[1] - self.tiles[i].y
                    if 0 < distanceX < 64 and 0 < distanceY < 64:
                        tileClicked = i
                        # print('Clicked Tile: ' + str(tileClicked))

                        # Advance Token
                        if self.tiles[tileClicked].isOccupiedByLight and self.gameState == "lights move" and \
                                not self.light.isAI:
                            if self.isMoveLocked(self.light):  # Check to see if you can't move
                                self.gameState = "darks roll"
                                if self.light.isAI:
                                    self.gameState = "darks roll wait"
                                    self.timerAI = Game.timerAIMax
                                break
                            if self.advanceToken(tileClicked, self.light):
                                # if self.gameState == "lights reroll":  # Check for reroll
                                #     self.gameState = "lights roll"
                                #     if self.light.isAI:
                                #         self.gameState = "lights roll wait"
                                #         self.timerAI = Game.timerAIMax
                                # else:
                                #     self.gameState = "darks roll"
                                break
                        if self.tiles[tileClicked].isOccupiedByDark and self.gameState == "darks move" and \
                                not self.dark.isAI:
                            if self.isMoveLocked(self.dark):  # Check to see if you can't move
                                self.gameState = "lights roll"
                                if self.dark.isAI:
                                    self.gameState = "lights roll wait"
                                    self.timerAI = Game.timerAIMax
                                break
                            if self.advanceToken(tileClicked, self.dark):
                                # if self.gameState == "darks reroll":  # Check for reroll
                                #     self.gameState = "darks roll"
                                # else:
                                #     self.gameState = "lights roll"
                                break

    def handleKeyboard(self, event):
        # Press ANY Key to Roll Dice
        if event.type == pygame.KEYUP:
            if self.gameState == "lights roll" and not self.light.isAI:
                self.rollDice()
            if self.gameState == "darks roll" and not self.dark.isAI:
                self.rollDice()

    def rollDice(self):
        # Roll dice for light tokens
        if self.gameState == "lights roll":
            self.light.scrambleTimer = Player.scrambleTimerMax
            self.light.roll = 0
            for i in range(Die.numDice):  # Roll The Light Dice
                self.light.dice[i].value = random.randint(0, 1)
                self.light.roll += self.light.dice[i].value
            self.gameState = "lights move"
            if self.light.isAI:
                self.gameState = "lights move wait"
                self.timerAI = Game.timerAIMax
        # Roll dice for dark tokens
        if self.gameState == "darks roll":
            self.dark.scrambleTimer = Player.scrambleTimerMax
            self.dark.roll = 0
            for i in range(Die.numDice):  # Roll The Dark Dice
                self.dark.dice[i].value = random.randint(0, 1)
                self.dark.roll += self.dark.dice[i].value
            self.gameState = "darks move"
            if self.dark.isAI:
                self.gameState = "darks move wait"
                self.timerAI = Game.timerAIMax

    def advanceToken(self, tileToAdvanceFrom, player):
        # Retrieve the correct path
        path = Game.lightPath
        if player.name == "dark":
            path = Game.darkPath

        # Advance Token Logic
        for i in range(Game.pathLen):
            if tileToAdvanceFrom == path[i] and player.roll + i < Game.pathLen:
                tileToLandOn = path[player.roll + i]

                # If you land on an enemy piece, you send it home
                # If you land on an opponent on an immortal square, you cannot send their piece home
                # But you can jump an extra space to go past them
                if (player.name == "light" and self.tiles[tileToLandOn].isOccupiedByDark) or \
                        (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByLight):
                    if self.tiles[tileToLandOn].isImmortal:
                        tileToLandOn = path[i + player.roll + 1]

                    if not self.tiles[tileToLandOn].isImmortal and \
                            ((player.name == "light" and self.tiles[tileToLandOn].isOccupiedByDark) or
                             (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByLight)):
                        if player.name == "light":
                            self.tiles[tileToLandOn].isOccupiedByDark = False
                            self.tiles[Game.darkPath[0]].isOccupiedByDark = True
                            self.dark.numTokensHome += 1
                        elif player.name == "dark":
                            self.tiles[tileToLandOn].isOccupiedByLight = False
                            self.tiles[Game.lightPath[0]].isOccupiedByLight = True
                            self.light.numTokensHome += 1

                # Can't land on your own piece unless scoring or going home
                if (player.name == "light" and self.tiles[tileToLandOn].isOccupiedByLight) or \
                        (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByDark):
                    if tileToLandOn != path[Game.pathLen - 1] and player.roll != 0:
                        continue

                # Move the token
                if player.name == "light":
                    self.tiles[tileToAdvanceFrom].isOccupiedByLight = False
                    self.tiles[tileToLandOn].isOccupiedByLight = True
                elif player.name == "dark":
                    self.tiles[tileToAdvanceFrom].isOccupiedByDark = False
                    self.tiles[tileToLandOn].isOccupiedByDark = True

                # If advancing from home, subtract a token from home
                if tileToAdvanceFrom == path[0] and player.roll != 0:
                    player.numTokensHome -= 1
                    if player.numTokensHome > 0:
                        if player.name == "light":
                            self.tiles[tileToAdvanceFrom].isOccupiedByLight = True
                        elif player.name == "dark":
                            self.tiles[tileToAdvanceFrom].isOccupiedByDark = True

                # Score if you get a token to the finish
                if tileToLandOn == path[Game.pathLen - 1] and player.roll != 0:
                    player.numTokensScored += 1

                # Change Game State
                if player.name == "light":
                    self.gameState = "darks roll"
                    if self.dark.isAI:
                        self.timerAI = Game.timerAIMax
                        self.gameState = "darks roll wait"
                elif player.name == "dark":
                    self.gameState = "lights roll"
                    if self.light.isAI:
                        self.timerAI = Game.timerAIMax
                        self.gameState = "lights roll wait"
                # Change game state to give player another roll if they land on a reroll
                if self.tiles[tileToLandOn].isReroll and player.roll != 0:
                    self.gameState = player.name + "s roll"
                self.numTurns += 1
                return True
        return False

    def isMoveLocked(self, player):
        if player.roll == 0:
            return False
        # Retrieve the correct path
        path = Game.lightPath
        if player.name == "dark":
            path = Game.darkPath

        for i in range(0, Game.pathLen - 1, 1):
            if i + player.roll > Game.pathLen - 1:
                # print("Player Cannot Play a Move")
                return True
            tileToAdvanceFrom = path[i]
            tileToLandOn = path[i + player.roll]

            # If you move a light token to a spot that doesn't have a light token or is the last tile
            # Then it is a legal move, and therefore you are not move locked
            if player.name == "light":
                if self.tiles[tileToAdvanceFrom].isOccupiedByLight and \
                        (not self.tiles[tileToLandOn].isOccupiedByLight or tileToLandOn == path[Game.pathLen - 1]):
                    return False
            elif player.name == "dark":
                if self.tiles[tileToAdvanceFrom].isOccupiedByDark and \
                        (not self.tiles[tileToLandOn].isOccupiedByDark or tileToLandOn == path[Game.pathLen - 1]):
                    return False

    ### AI ###
    def updateAI(self):
        # print(self.timerAI)
        self.timerAI -= 1  # Decrement Timer
        if self.timerAI < 0:
            self.timerAI = 0
        if not self.light.isAI and not self.dark.isAI:
            return False
        if self.timerAI <= 0:
            if self.gameState == "lights roll wait":
                self.gameState = "lights roll"
            if self.gameState == "darks roll wait":
                self.gameState = "darks roll"
            if self.gameState == "lights move wait":
                self.gameState = "lights move"
            if self.gameState == "darks move wait":
                self.gameState = "darks move"
            if self.light.isAI:
                if self.gameState == "lights roll":
                    self.rollDice()
                if self.gameState == "lights move":
                    # self.earlyAgentMove(self.light)
                    # self.logicalAgentMove(self.light)
                    self.neuralNetworkMove(self.light)
            if self.dark.isAI:
                if self.gameState == "darks roll":
                    self.rollDice()
                if self.gameState == "darks move":
                    # self.earlyAgentMove(self.dark)
                    # self.logicalAgentMove(self.dark)
                    self.neuralNetworkMove(self.dark)

    def earlyAgentMove(self, player):
        # Retrieve the correct path
        path = Game.lightPath
        if player.name == "dark":
            path = Game.darkPath

        if self.isMoveLocked(player):
            if player.name == "light":
                self.gameState = "darks roll"
            elif player.name == "dark":
                self.gameState = "lights roll"

            if self.gameState == "lights roll" and self.light.isAI:
                self.gameState = "lights roll wait"
                self.timerAI = Game.timerAIMax
            elif self.gameState == "darks roll" and self.dark.isAI:
                self.gameState = "darks roll wait"
                self.timerAI = Game.timerAIMax
            return False

        for i in range(Game.pathLen):
            tileToAdvanceFrom = path[i]
            if (player.name == "light" and self.tiles[
                tileToAdvanceFrom].isOccupiedByLight and self.gameState == "lights move") or \
                    (player.name == "dark" and self.tiles[
                        tileToAdvanceFrom].isOccupiedByDark and self.gameState == "darks move"):
                if self.advanceToken(tileToAdvanceFrom, player):
                    self.timerAI = Game.timerAIMax
                    if self.gameState == "lights roll" and self.light.isAI:
                        self.gameState = "lights roll wait"
                    elif self.gameState == "darks roll" and self.dark.isAI:
                        self.gameState = "darks roll wait"
                    return True
        return False

    def logicalAgentMove(self, player):
        # Retrieve the correct path
        path = Game.lightPath
        if player.name == "dark":
            path = Game.darkPath
        moveScore = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        bestScore = -1
        bestTileToAdvanceFrom = 0
        if self.isMoveLocked(player):
            self.moveLockedAI(player)
            return False
        if player.roll == 0:  # This fixed a weird bug where this function would play a move when it rolled 0
            self.earlyAgentMove(player)
            return False

        # Check to see
        # 1: if you can move to the immortal square
        # 2: to see if you can capture an enemy piece
        # 3: move to a reroll
        # 4: move to safety
        for i in range(Game.pathLen):
            tileToAdvanceFrom = path[i]
            # If you don't have a token on the square it is an invalid move
            if player.name == "light" and not self.tiles[tileToAdvanceFrom].isOccupiedByLight:
                continue
            if player.name == "dark" and not self.tiles[tileToAdvanceFrom].isOccupiedByDark:
                continue
            # Assure that the tileToAdvanceTo is in range of the lightPath array
            if i + player.roll >= Game.pathLen:
                break
            tileToLandOn = path[i + player.roll]
            # You cannot land on your own piece
            if player.name == "light" and self.tiles[tileToLandOn].isOccupiedByLight:
                continue
            if player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByDark:
                continue

            # Tile 11 is the Immortal Square and is a key part of the game
            if tileToLandOn == 11:
                if (player.name == "light" and not self.tiles[tileToLandOn].isOccupiedByDark) or \
                        (player.name == "dark" and not self.tiles[tileToLandOn].isOccupiedByLight):
                    moveScore[i] = 13
                else:
                    # If there is an enemy piece on the immortal square and we land on them
                    # We jump 1 tile over them instead of capturing their token
                    tileToLandOn = path[i + player.roll + 1]
                    if (player.name == "light" and self.tiles[tileToLandOn].isOccupiedByDark) or \
                            (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByLight):
                        moveScore[i] = i + player.roll + 1
                    elif (player.name == "light" and self.tiles[tileToLandOn].isOccupiedByLight) or \
                            (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByDark):
                        moveScore[i] = -1
                    else:
                        moveScore[i] = 1
            # Prioritize capturing pieces
            elif (player.name == "light" and self.tiles[tileToLandOn].isOccupiedByDark) or \
                    (player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByLight):
                moveScore[i] = i + player.roll
            # Prioritize landing on reroll squares
            elif self.tiles[tileToLandOn].isReroll:
                moveScore[i] = 3
            # prioritize getting tokens to safety
            elif i + player.roll > 13 > i:
                moveScore[i] = 2
            # prioritize scoring because that is how you win
            elif i + player.roll == 15:
                moveScore[i] = 1
            elif i + player.roll > 12 > i:
                moveScore[i] = 1
            else:  # valid moves are assigned a value based on my opinion on how important it is to move from a tile
                moveScore[i] = Game.tileWeights[i]

            if tileToAdvanceFrom == 11:  # Punish moving off of the immortal square
                moveScore[i] -= 8
                if moveScore[i] < 0:  # Cap floor at 0 since it is still a valid move
                    moveScore[i] = 0

        # Find which move scored the highest moveScore
        for i in range(Game.pathLen):
            tileToAdvanceFrom = path[i]
            if moveScore[i] > bestScore:
                bestScore = moveScore[i]
                bestTileToAdvanceFrom = tileToAdvanceFrom

        print(str(player.name) + ": " + str(moveScore) + ", " + str(bestTileToAdvanceFrom) + ", " + str(player.roll))

        if self.advanceToken(bestTileToAdvanceFrom, player):
            self.timerAI = Game.timerAIMax
            if self.gameState == "lights roll" and self.light.isAI:
                self.gameState = "lights roll wait"
            elif self.gameState == "darks roll" and self.dark.isAI:
                self.gameState = "darks roll wait"
            return True
        else:
            self.earlyAgentMove(player)
            return False

    def neuralNetworkMove(self, player):
        # Retrieve the correct path
        path = Game.lightPath
        enemyPath = Game.darkPath
        if player.name == "dark":
            path = Game.darkPath
            enemyPath = Game.lightPath
        if self.isMoveLocked(player):
            self.moveLockedAI(player)
            return False
        if player.roll == 0:  # This fixed a weird bug where this function would play a move when it rolled 0
            self.earlyAgentMove(player)
            return False

        # Add the input values to the neural network
        player.neuralNetwork.layers[0].nodes[0].value = player.roll  # Have the first input be the roll value
        j = 1   # index of the node
        # The next input nodes are the values of if a friendly token occupies a tile
        for i in range(Game.pathLen-1):
            value = 0
            if (self.tiles[path[i]].isOccupiedByLight and player.name == "light") or \
                    (self.tiles[path[i]].isOccupiedByDark and player.name == "dark"):
                value = 1
            player.neuralNetwork.layers[0].nodes[j].value = value
            j += 1
        # The next set of input nodes are the values of if an enemy token occupies a tile
        for i in range(Game.pathLen-1):
            value = 0
            if (self.tiles[enemyPath[i]].isOccupiedByDark and player.name == "light") or \
                    (self.tiles[enemyPath[i]].isOccupiedByLight and player.name == "dark"):
                value = 1
            player.neuralNetwork.layers[0].nodes[j].value = value
            j += 1

        # Retrieve Output Perceptron Values to determine the guess of the NN
        guesses = player.neuralNetwork.makeGuessReturnsOutputValues()
        bestScore = -1
        bestTileToAdvanceFrom = 0
        for i in range(Game.pathLen):
            if not self.isPlayableMove(i, path, player):
                guesses[i] = -1

        # Find which move scored the highest moveScore
        for i in range(Game.pathLen):
            tileToAdvanceFrom = path[i]
            if guesses[i] > bestScore:
                bestScore = guesses[i]
                bestTileToAdvanceFrom = tileToAdvanceFrom

        if not self.light.isAI or not self.dark.isAI:
            print(str(player.name) + ": " + str(guesses) + ", " + str(bestTileToAdvanceFrom) + ", " + str(player.roll))
        if self.advanceToken(bestTileToAdvanceFrom, player):
            self.timerAI = Game.timerAIMax
            if self.gameState == "lights roll" and self.light.isAI:
                self.gameState = "lights roll wait"
            elif self.gameState == "darks roll" and self.dark.isAI:
                self.gameState = "darks roll wait"
            return True
        return False


    def moveLockedAI(self, player):
        if player.name == "light":
            self.gameState = "darks roll"
        elif player.name == "dark":
            self.gameState = "lights roll"

        if self.gameState == "lights roll" and self.light.isAI:
            self.gameState = "lights roll wait"
            self.timerAI = Game.timerAIMax
        elif self.gameState == "darks roll" and self.dark.isAI:
            self.gameState = "darks roll wait"
            self.timerAI = Game.timerAIMax
    def isPlayableMove(self, i, path, player):
        tileToAdvanceFrom = path[i]
        # If you don't have a token on the square it is an invalid move
        if player.name == "light" and not self.tiles[tileToAdvanceFrom].isOccupiedByLight:
            return False
        if player.name == "dark" and not self.tiles[tileToAdvanceFrom].isOccupiedByDark:
            return False
        # Assure that the tileToAdvanceTo is in range of the path array
        if i + player.roll >= Game.pathLen:
            return False
        tileToLandOn = path[i + player.roll]
        if tileToLandOn == 11 and player.name == "light" and self.tiles[11].isOccupiedByDark:
            tileToLandOn = 12
        if tileToLandOn == 11 and player.name == "dark" and self.tiles[11].isOccupiedByLight:
            tileToLandOn = 12
        # You cannot land on your own piece unless your scoring
        if not tileToLandOn == path[Game.pathLen - 1]:
            if player.name == "light" and self.tiles[tileToLandOn].isOccupiedByLight:
                return False
            if player.name == "dark" and self.tiles[tileToLandOn].isOccupiedByDark:
                return False
        return True

    ### DRAWING GRAPHICS ###
    def draw(self, screen):
        # Draw Background
        screen.fill((200, 180, 150))
        # Draw Tiles
        self.drawTiles(screen)
        # Draw Dice
        self.drawDice(screen, self.light)
        self.drawDice(screen, self.dark)
        # Draw Information
        self.drawGameState(screen)
        # Draw Player Info
        self.drawPlayerInfo(screen, self.light)
        self.drawPlayerInfo(screen, self.dark)

    def drawTiles(self, screen):
        for i in range(Tile.numTiles):
            screen.blit(self.tiles[i].image, (self.tiles[i].x, self.tiles[i].y))
            if self.tiles[i].isOccupiedByLight:
                screen.blit(self.tiles[i].imageLightTok, (self.tiles[i].x, self.tiles[i].y))
            elif self.tiles[i].isOccupiedByDark:
                screen.blit(self.tiles[i].imageDarkTok, (self.tiles[i].x, self.tiles[i].y))

    def drawDice(self, screen, player):
        color = player.name
        for i in range(Die.numDice):
            if player.scrambleTimer > 0:
                if (color == "dark" and self.gameState == "darks move") or \
                        (color == "light" and self.gameState == "lights move"):
                    player.scrambleTimer -= 1
                    screen.blit(player.dice[i].image[int(player.scrambleTimer / 10) % 2],
                                (player.dice[i].x, player.dice[i].y))
                else:
                    screen.blit(player.dice[i].image[player.dice[i].value], (player.dice[i].x, player.dice[i].y))
            else:
                screen.blit(player.dice[i].image[player.dice[i].value], (player.dice[i].x, player.dice[i].y))

    def drawGameState(self, screen):
        text = self.fontLarge.render(self.gameState, True, (0, 0, 0))
        textRect = text.get_rect()
        screen.blit(text, (textRect.x + 5, textRect.y + 360))

    def drawPlayerInfo(self, screen, player):
        pixelX = 15
        pixelY = 250
        if player.name == "dark":
            pixelX = 275
        out = "Score: " + str(player.numTokensScored)
        out += "   Home: " + str(player.numTokensHome)
        out += "   Roll: " + str(player.roll)
        text = self.fontSmall.render(out, True, (10, 10, 10))
        textRect = text.get_rect()
        screen.blit(text, (textRect.x + pixelX, textRect.y + pixelY))

    @staticmethod
    def getRandomStart():
        randomStart = random.randint(0, 1)
        if randomStart == 0:
            return "lights roll"
        else:
            return "darks roll"


class Tile:
    # These are static and final elements of the object Tile
    numTiles = 24
    lengthPix = 64
    types = [
        # Row 1
        pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tile4eyes.png'),
        pygame.image.load('sprites/tile5circles.png'), pygame.image.load('sprites/tile4eyes.png'),
        pygame.image.load('sprites/tileBlankBlank.png'), pygame.image.load('sprites/tileBlankBlank.png'),
        pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileRightCorners.png'),
        # Row 2
        pygame.image.load('sprites/tile5Crosses.png'), pygame.image.load('sprites/tile5circles.png'),
        pygame.image.load('sprites/tile4X.png'), pygame.image.load('sprites/tileReroll.png'),
        pygame.image.load('sprites/tile5circles.png'), pygame.image.load('sprites/tile4X.png'),
        pygame.image.load('sprites/tile4eyes.png'), pygame.image.load('sprites/tile5circles.png'),
        # Row 3
        pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tile4eyes.png'),
        pygame.image.load('sprites/tile5circles.png'), pygame.image.load('sprites/tile4eyes.png'),
        pygame.image.load('sprites/tileBlankBlank.png'), pygame.image.load('sprites/tileBlankBlank.png'),
        pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileRightCorners.png')]

    def __init__(self, x, y, isReroll, isImmortal, isOccupiedByLight, isOccupiedByDark, image, gameID):
        self.x = x
        self.y = y
        self.isReroll = isReroll
        self.isImmortal = isImmortal
        self.isOccupiedByLight = isOccupiedByLight
        self.isOccupiedByDark = isOccupiedByDark

        self.image = image
        if gameID == 0:
            self.imageLightTok = pygame.image.load('sprites/lightToken.png')
            self.imageDarkTok = pygame.image.load('sprites/darkToken.png')

class Die:
    # These are static and final elements of the object Die
    numDice = 4

    def __init__(self, dieX, dieY, color, value, nnID):
        self.x = dieX
        self.y = dieY
        self.color = color
        self.value = value
        self.image = []
        if color == "light" and (nnID == 0 or nnID == 1):
            self.image.append(pygame.image.load('sprites/lightDie0.png'))
            self.image.append(pygame.image.load('sprites/lightDie1.png'))
        if color == "dark" and (nnID == 0 or nnID == 1):
            self.image.append(pygame.image.load('sprites/darkDie0.png'))
            self.image.append(pygame.image.load('sprites/darkDie1.png'))

class Player:
    scrambleTimerMax = 80

    def __init__(self, name, isAI, neuralNetworkID):
        self.name = name
        self.isAI = isAI
        self.neuralNetwork = NeuralNetwork(neuralNetworkID)
        self.numTokensHome = 7
        self.numTokensScored = 0
        self.roll = 0
        self.dice = []
        self.scrambleTimer = 0

        for i in range(Die.numDice):
            dieX = 0
            if name == "light":
                dieX = i * Tile.lengthPix
            elif name == "dark":
                dieX = (4 * Tile.lengthPix) + (i * Tile.lengthPix)

            dieY = 3 * Tile.lengthPix
            self.dice.append(Die(dieX, dieY, name, 0, neuralNetworkID))

class NeuralNetwork:
    numLayers = 4
    numNodes = [31, 31, 31, 16]
    numWeights = [0, numNodes[0], numNodes[1], numNodes[2]]

    def __init__(self, networkID):
        self.networkID = networkID
        self.layers = []
        self.fileName = "data/neural_networks/nn" + str(self.networkID) + ".txt"
        self.readNeuralNetworkFromFile()

        # You only need to run these functions if you don't already have a set of neural networks
        # self.createRandomNeuralNetwork()
        # self.writeNeuralNetworkToFile()

    def makeGuessReturnsOutputValues(self):
        # Go through each value of each node in the previous layer, and find the value of the current node
        for i in range(1, NeuralNetwork.numLayers, 1):  # i is each layer
            for j in range(NeuralNetwork.numNodes[i]):  # j is each node in that layer
                self.layers[i].nodes[j].value = self.retrieveNodeValue(i, j)

        answer = []
        for i in range(NeuralNetwork.numNodes[NeuralNetwork.numLayers-1]):
            answer.append(self.layers[NeuralNetwork.numLayers-1].nodes[i].value)
        return answer

    def retrieveNodeValue(self, layerIndex, nodeIndex):
        answer = 0
        for i in range(NeuralNetwork.numWeights[layerIndex]):  # i is the position of the node/weight duo
            # Multiplying the value a node from the last layer by the weight
            answer += self.layers[layerIndex-1].nodes[i].value * self.layers[layerIndex].nodes[nodeIndex].weights[i]
        answer = NeuralNetwork.sigmoid(answer)
        return answer

    def createRandomNeuralNetwork(self):
        for i in range(NeuralNetwork.numLayers):
            layer = Layer(NeuralNetwork.numNodes[i])
            for j in range(NeuralNetwork.numNodes[i]):
                layer.nodes.append(Perceptron(NeuralNetwork.numWeights[i]))
                layer.nodes[j].assignRandomWeights()
            self.layers.append(layer)

    def writeNeuralNetworkToFile(self):
        file = open(self.fileName, "w")
        for i in range(4):
            for j in range(self.layers[i].size):
                for k in range(self.layers[i].nodes[j].size):
                    file.write(str(self.layers[i].nodes[j].weights[k]) + "\n")
        file.close()

    def readNeuralNetworkFromFile(self):
        fileWeights = open(self.fileName, "r")
        for i in range(NeuralNetwork.numLayers):
            layer = Layer(NeuralNetwork.numNodes[i])
            for j in range(NeuralNetwork.numNodes[i]):
                numWeights = NeuralNetwork.numWeights[i]
                layer.nodes.append(Perceptron(numWeights))
                weights = []
                for k in range(numWeights):
                    weights.append(float(fileWeights.readline()))

                layer.nodes[j].assignWeights(weights)
            self.layers.append(layer)
        fileWeights.close()

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1.0 + pow(math.e, -x))

class Layer:
    def __init__(self, size):
        self.size = size
        self.nodes = []

class Perceptron:
    def __init__(self, size):
        self.size = size
        self.weights = []
        self.value = 0

    def assignRandomWeights(self):
        for i in range(self.size):
            self.weights.append((random.random() * 2.0) - 1)

    def assignWeights(self, weights):
        for i in range(self.size):
            self.weights.append(weights[i])
