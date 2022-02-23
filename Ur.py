# Mason Reck
# 2/22/2022
# Game of Ur with the intention of creating a neural network AI to play against


import pygame
import random

# Initiate game engine
pygame.init()

# Screen
screenWidth = 512
screenHeight = 400
screen = pygame.display.set_mode((screenWidth, screenHeight))

# Clock
FPS = 60
fpsClock = pygame.time.Clock()

# Title and Icon
pygame.display.set_caption("The Royal Game of Ur")
icon = pygame.image.load('sprites/icon.png')
pygame.display.set_icon(icon)

# Game Variables
font = pygame.font.Font('freesansbold.ttf', 32)
font2 = pygame.font.Font('freesansbold.ttf', 16)
numDarkTokensHome = 7
numLightTokensHome = 7
numDarkTokensScored = 0
numLightTokensScored = 0


# Game Tiles Object
class Tile:
    def __init__(self, x, y, isReroll, isImmortal, isOccupiedByLight, isOccupiedByDark, image):
        self.x = x
        self.y = y
        self.isReroll = isReroll
        self.isImmortal = isImmortal
        self.isOccupiedByLight = isOccupiedByLight
        self.isOccupiedByDark = isOccupiedByDark
        self.image = image
        self.imageLightTok = pygame.image.load('sprites/lightToken.png')
        self.imageDarkTok = pygame.image.load('sprites/darkToken.png')


tileType = [
    # Row 1
    pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlankBlank.png'), pygame.image.load('sprites/tileBlankBlank.png'),
    pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileBlank.png'),
    # Row 2
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileReroll.png'),
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileBlank.png'),
    # Row 3
    pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlank.png'), pygame.image.load('sprites/tileBlank.png'),
    pygame.image.load('sprites/tileBlankBlank.png'), pygame.image.load('sprites/tileBlankBlank.png'),
    pygame.image.load('sprites/tileReroll.png'), pygame.image.load('sprites/tileBlank.png')]

numTiles = 24
tileLength = 64
tile = []
# Tile Settings (These shouldn't change)
for i in range(numTiles):
    tileX = 0  # Tile's X Coordinate
    tileY = 0  # Tile's Y Coordinate
    if i < 8:  # Upper Row
        tileX = i * tileLength
        tileY = 0
    elif i < 16:  # Middle Row
        tileX = (i - 8) * tileLength
        tileY = tileLength
    elif i < 24:  # Lower Row
        tileX = (i - 16) * tileLength
        tileY = tileLength * 2

    tile.append(Tile(tileX, tileY, False, False, False, False, tileType[i]))

###### Tile Layout #######
# 0  1  2  3  4  5  6  7
# 8  9  10 11 12 13 14 15
# 16 17 18 19 20 21 22 23
##########################
# Add the reroll Tiles and the Immortal Square
tile[0].isReroll = True
tile[6].isReroll = True
tile[11].isReroll = True
tile[16].isReroll = True
tile[22].isReroll = True
tile[11].isImmortal = True  # Tile 11 is the IMMORTAL square
tile[4].isOccupiedByLight = True
tile[20].isOccupiedByDark = True


# 50/50 Dice Object
class Die:
    def __init__(self, dieX, dieY, color, value):
        self.x = dieX
        self.y = dieY
        self.color = color
        self.value = value
        self.image = []
        if color is "light":
            self.image.append(pygame.image.load('sprites/lightDie0.png'))
            self.image.append(pygame.image.load('sprites/lightDie1.png'))
        if color is "dark":
            self.image.append(pygame.image.load('sprites/darkDie0.png'))
            self.image.append(pygame.image.load('sprites/darkDie1.png'))


# Initialize Dice
numDice = 4
lightDice = []
darkDice = []
lightRoll = 0
darkRoll = 0
for i in range(numDice):
    # Initiate Light Dice
    dieX = i * tileLength
    dieY = 3 * tileLength
    lightDice.append(Die(dieX, dieY, "light", 0))
    # Initiate Dark Dice
    dieX = (4 * tileLength) + (i * tileLength)
    dieY = 3 * tileLength
    darkDice.append(Die(dieX, dieY, "dark", 0))


def draw_tile(tile):
    screen.blit(tile.image, (tile.x, tile.y))
    if tile.isOccupiedByLight:
        screen.blit(tile.imageLightTok, (tile.x, tile.y))
    elif tile.isOccupiedByDark:
        screen.blit(tile.imageDarkTok, (tile.x, tile.y))


def draw_dice(die):
    screen.blit(die.image[die.value], (die.x, die.y))

def draw_game_state():
    text = font.render(gameState, True, (0, 0, 0))
    textRect = text.get_rect()
    screen.blit(text, (textRect.x + 5, textRect.y + 360))

def draw_light_info():
    out = "Home: " + str(numLightTokensHome) + "   Score: " + str(numLightTokensScored)
    text = font2.render(out, True, (0, 0, 0))
    textRect = text.get_rect()
    screen.blit(text, (textRect.x + 15, textRect.y + 250))

def draw_dark_info():
    out = "Home: " + str(numDarkTokensHome) + "   Score: " + str(numDarkTokensScored)
    text = font2.render(out, True, (0, 0, 0))
    textRect = text.get_rect()
    screen.blit(text, (textRect.x + 275, textRect.y + 250))



###### Tile Layout #######
# 0  1  2  3  4  5  6  7
# 8  9  10 11 12 13 14 15
# 16 17 18 19 20 21 22 23
##########################
pathLen = 16
lightPath = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5]  # Path that player 1 has to take to score
darkPath = [20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21]  # Path that player 2 has to take to score
def advanceLightToken(tileToAdvanceFrom):
    global gameState
    global numDarkTokensHome
    global numLightTokensHome
    global numLightTokensScored
    bonusMovement = 0
    for i in range(pathLen):
        if tileToAdvanceFrom == lightPath[i] and i + lightRoll < pathLen:
            tileToLandOn = lightPath[i + lightRoll]
            if tile[tileToLandOn].isOccupiedByLight \
                    and tileToLandOn != lightPath[pathLen-1] \
                    and lightRoll != 0:    # Can't land on your own piece unless scoring
                continue

            if tile[tileToLandOn].isOccupiedByDark:  # If you land on an enemy piece, you send it home
                # If you land on an opponent on an immortal square, you cannot send their piece home
                # But you can jump an extra space to go past them
                if tile[tileToLandOn].isImmortal:
                    bonusMovement = 1
                else:
                    tile[tileToLandOn].isOccupiedByDark = False
                    tile[darkPath[0]].isOccupiedByDark = True
                    numDarkTokensHome += 1

            tile[tileToAdvanceFrom].isOccupiedByLight = False
            tile[tileToLandOn + bonusMovement].isOccupiedByLight = True
            # If advancing from home, subtract a token from home
            if tileToAdvanceFrom == lightPath[0] and lightRoll != 0:
                numLightTokensHome -= 1
                if numLightTokensHome > 0:
                    tile[tileToAdvanceFrom].isOccupiedByLight = True

            # Score if you get a token to the finish
            if tileToLandOn == lightPath[pathLen - 1] and lightRoll != 0:
                numLightTokensScored += 1
            if tile[tileToLandOn + bonusMovement].isReroll and lightRoll != 0:
                gameState = "lights reroll"
            return True
    return False

def advanceDarkToken(tileToAdvanceFrom):
    global gameState
    global numDarkTokensHome
    global numDarkTokensScored
    global numLightTokensHome
    bonusMovement = 0
    for i in range(pathLen):
        if tileToAdvanceFrom == darkPath[i] and i + darkRoll < pathLen:
            tileToLandOn = darkPath[i + darkRoll]
            if tile[tileToLandOn].isOccupiedByDark \
                    and tileToLandOn != darkPath[pathLen-1] \
                    and darkRoll != 0:    # Can't land on your own piece unless you roll a 0
                continue
            # If you land on enemy piece, you send it home
            if tile[tileToLandOn].isOccupiedByLight:
                if tile[tileToLandOn].isImmortal:
                    bonusMovement = 1
                else:
                    tile[tileToLandOn].isOccupiedByLight = False
                    tile[lightPath[0]].isOccupiedByLight = True
                    numLightTokensHome += 1

            tile[tileToAdvanceFrom].isOccupiedByDark = False
            tile[tileToLandOn + bonusMovement].isOccupiedByDark = True
            # If advancing from home, subtract a token from home
            if tileToAdvanceFrom == darkPath[0] and darkRoll != 0:
                numDarkTokensHome -= 1
                if numDarkTokensHome > 0:
                    tile[tileToAdvanceFrom].isOccupiedByDark = True

            # Score if you get a token to the finish
            if tileToLandOn == darkPath[pathLen-1] and darkRoll != 0:
                numDarkTokensScored += 1
            if tile[tileToLandOn + bonusMovement].isReroll and darkRoll != 0:
                gameState = "darks reroll"
            return True
    return False

def isMoveLockedLight():
    global lightRoll
    if lightRoll == 0:
        return False
    for i in range(0, pathLen - 1, 1):
        if i + lightRoll > pathLen-1:
            print("Light Cannot play a move")
            return True
        tileToAdvanceFrom = lightPath[i]
        tileToLandOn = lightPath[i + lightRoll]

        # If you move a light token to a spot that doesn't have a light token or is the last tile
        # Then it is a legal move, and therefore you are not move locked
        if tile[tileToAdvanceFrom].isOccupiedByLight and \
                (not tile[tileToLandOn].isOccupiedByLight or tileToLandOn == lightPath[pathLen-1]):
            # print("Light can play " + str(lightPath[i]) + " to " + str(lightPath[i + lightRoll]))
            return False

def isMoveLockedDark():
    global darkRoll
    if darkRoll == 0:
        return False
    for i in range(0, pathLen - 1, 1):  # No need to check first and final as they are always able to be landed on
        if i + darkRoll > pathLen - 1:
            print("Dark Cannot play a move")
            return True
        tileToAdvanceFrom = darkPath[i]
        tileToLandOn = darkPath[i + darkRoll]
        if tile[tileToAdvanceFrom].isOccupiedByDark and not tile[tileToLandOn].isOccupiedByDark:
            # print("Dark can play " + str(darkPath[i]) + " to " + str(darkPath[i + darkRoll]))
            return False

# Game Loop
running = True
gameState = "lights roll"  # Other Options: "lights move", "darks roll", "darks move"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ### Game Inputs ###
    if event.type == pygame.MOUSEBUTTONUP:
        pos = pygame.mouse.get_pos()

        # Mouse Tile Collisions
        if gameState is "lights move" or gameState is "darks move":
            tileClicked = -1
            for i in range(numTiles):
                distanceX = pos[0] - tile[i].x
                distanceY = pos[1] - tile[i].y
                if 0 < distanceX < 64 and 0 < distanceY < 64:
                    tileClicked = i
                    # print('Clicked Tile: ' + str(tileClicked))

                    # Advance Token
                    if tile[tileClicked].isOccupiedByLight and gameState is "lights move":
                        if isMoveLockedLight():  # Check to see if you can't move
                            gameState = "darks roll"
                            break
                        if advanceLightToken(tileClicked):
                            if gameState is not "lights move":  # Check for reroll
                                gameState = "lights roll"
                            else:
                                gameState = "darks roll"
                            break
                    if tile[tileClicked].isOccupiedByDark and gameState is "darks move":
                        if isMoveLockedDark():  # Check to see if you can't move
                            gameState = "lights roll"
                            break
                        if advanceDarkToken(tileClicked):
                            if gameState is not "darks move":  # Check for reroll
                                gameState = "darks roll"
                            else:
                                gameState = "lights roll"
                            break

    # Press A Key to Roll Dice
    if event.type == pygame.KEYUP:
        if gameState is "lights roll":
            lightRoll = 0
            for i in range(numDice):  # Roll The Light Dice
                lightDice[i].value = random.randint(0, 1)
                lightRoll += lightDice[i].value
            gameState = "lights move"
        if gameState is "darks roll":
            darkRoll = 0
            for i in range(numDice):  # Roll The Dark Dice
                darkDice[i].value = random.randint(0, 1)
                darkRoll += darkDice[i].value
            gameState = "darks move"

    # Game Checks
    if numLightTokensScored == 7:
        gameState = "Light Tokens Win!"
    if numDarkTokensScored == 7:
        gameState = "Dark Tokens Win!"

    ### Draw Graphics ###
    screen.fill((200, 180, 150))
    for i in range(numTiles):
        draw_tile(tile[i])
    for i in range(numDice):
        draw_dice(lightDice[i])
        draw_dice(darkDice[i])
    draw_game_state()
    draw_light_info()
    draw_dark_info()

    pygame.display.update()
    fpsClock.tick(FPS)
