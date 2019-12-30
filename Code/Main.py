# The Isle Of Malkhar
# This file is meant to join all the other code files together, so functions and variables can be easily shared across the program.

import pygame, sys, os, math, random, radius, bresenham
from math import *
from pygame import *
pygame.init()


def imgLoad(pathList): # pathList is a list of files/folders ending in the filename you want.
    filePath = os.path.join(*pathList)
    returnFile = pygame.image.load(filePath)
    return returnFile

def txtLoad(pathList, mode):
    filePath = os.path.join(*pathList)
    if not os.path.exists(filePath):
        file = open(filePath, 'w')
        file.close()
    file = open(filePath, mode)
    return file


def matrix_getAt(matrix, coord): # An (x,y,z) coord
    return matrix[coord[2]][coord[1]][coord[0]]

def matrix_setAt(matrix, coord, thing):
    matrix[coord[2]][coord[1]][coord[0]] = thing


def txtToSurface(startSurface, txt, font, color): # This function covers a pygame.Surface with text.
    surface = startSurface.copy()
    xLimit = surface.get_width()
    yLimit = surface.get_height()
    spaceLength = font.size(' ')[0]
    x = spaceLength
    y = 0
    fontHeight = font.get_height()
    
    ignoreLine = False

    txt = txt.split(' ') # txt is now a list.

    # NTS, have newlines as their own word.
    for word in txt:
        if word == '\n': # If there's a newline char
            if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                y += fontHeight + 2
                x = spaceLength
            else:
                break
        else: # For any other word
            if x + font.size(word)[0] <= xLimit: # If the word fits on the surface
                surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                x += font.size(word)[0]
                if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period or similar thingus
                    x += spaceLength * 2 # Add a double space
                else: # Otherwise
                    x += spaceLength # Add a single space
            else: # BUT if it doesn't fit...
                if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                    y += fontHeight + 2
                    x = spaceLength
                    surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                    x += font.size(word)[0]
                    if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period
                        x += spaceLength * 2 # Add a double space
                    else: # Otherwise
                        x += spaceLength # Add a single space
                else:
                    break

    return surface # Et voila, a text-covered surface!

def choiceBoxSurface(choices, selected, font, color=(255,255,255)):
    # choices=list, selected=int
    # Each choice will only take up one line.
    maxX = 0
    txtSurface = pygame.Surface((WX, (font.get_height()+8)*len(choices)))
    y = 4
    txtSurface.fill((100,100,100))
    arrowSpaceLength = font.size(' > ')[0]
    spaceLength = font.size(' ')[0]
    for c in choices:
        txt = c + ' '
        if c == choices[selected]:
            txt = ' > ' + txt
            txtSurface.blit(font.render(txt, True, color), (0, y))
        else:
            txtSurface.blit(font.render(txt, True, color), (arrowSpaceLength, y))
            
        y += font.get_height()+4
        if font.size(c)[0] + arrowSpaceLength + spaceLength > maxX:
            maxX = font.size(c)[0] + arrowSpaceLength + spaceLength

    # All the text should be blitted, now to clean it up.
    eraser = pygame.Surface((WX-(maxX+4), y+4))
    eraser.fill((0,255,0))
    txtSurface.blit(eraser, (maxX+4, 0))
    txtSurface.set_colorkey((0,255,0))
    return txtSurface

def basicChoiceBoxSurface(choices, font, color=(255,255,255)):
    # Copy of ChoiceBoxSurface() without the code dealing with the selected choice.  Should help with saving processing power.
    maxX = 0
    txtSurface = pygame.Surface((WX, (font.get_height()+8)*len(choices)))
    y = 4
    txtSurface.fill((127,127,127))
    arrowSpaceLength = font.size(' > ')[0]
    spaceLength = font.size(' ')[0]
    for c in choices:
        txt = c + ' '
        txtSurface.blit(font.render(txt, True, color), (arrowSpaceLength, y))
            
        y += font.get_height()+4
        if font.size(c)[0] + arrowSpaceLength + spaceLength > maxX:
            maxX = font.size(c)[0] + arrowSpaceLength + spaceLength

    y += 4

    # All the text should be blitted, now to clean it up.
    eraser = pygame.Surface((WX-(maxX+4), y+4))
    eraser.fill((0,255,0))
    txtSurface.blit(eraser, (maxX+4, 0))
    txtSurface.set_colorkey((0,255,0))
    return txtSurface

def loadLevel(folderName): # Generate a Level object from a given folder name in "Data/Rooms".
    file = txtLoad(['..', 'Data', 'Rooms', folderName, folderName+'.mld'], 'r')
    loading = None
    level = None
    counter = 0
    layer = 0
    row = 0
    
    for line in file:
        line = line.strip()

        # Get the name
        if line.startswith('NAME='):
            name = line.strip('NAME=')

        # Get the dimensions
        if line.startswith('DIMENSIONS'):
            loading = 'DIMENSIONS'
            pass
        
        if (loading == 'DIMENSIONS'):
            if line.startswith('END_DIMENSIONS'):
                loading = None
                level = Level(levelX, levelY, levelZ, name)
                pass
            elif line.startswith('levelX='):
                levelX = int(line.strip('levelX='))
            elif line.startswith('levelY='):
                levelY = int(line.strip('levelY='))
            elif line.startswith('levelZ='):
                levelZ = int(line.strip('levelZ='))

        # Get the background images
        if line.startswith('BKGS'):
            loading = 'BKGS'
            counter = 0
            pass

        if (loading == 'BKGS'):
            if line.startswith('END_BKGS'):
                loading = None
                pass
            elif line.startswith('BKGS'):
                pass
            elif (line == 'X'):
                level.setBkg(None, counter)
                counter += 1
            else:
                level.setBkg(line, counter)
                counter += 1
                

        # Get the tilesets
        if line.startswith('TILESETS='):
            loading = 'TILESETS'
            pass
        
        if loading == 'TILESETS':
            if line.startswith('END_TILESETS'):
                loading = None
                pass
            elif line.startswith('TILESETS'):
                pass
            else:
                level.addTileset(line)

        # Get the blockmap
        if line.startswith('BLOCKMAP'):
            loading = 'BLOCKMAP'
            layer = 0
            pass

        if loading == 'BLOCKMAP':
            if line.startswith('END_BLOCKMAP'):
                loading = None
                pass
            elif line.startswith('BLOCKMAP'):
                pass
            elif line.startswith('NEXTLAYER'):
                layer += 1
                pass
            else:
                rowOfBlocks = line.split(',')
                for x in range(levelX):
                    blockData = rowOfBlocks[x].split('|')
                    block = Block(blockData[0], (int(blockData[1]), int(blockData[2]), int(blockData[3])))
                    level.setBlockAt((x, row, layer), block)
                row += 1

        # Get entities
        if line.startswith('ENTITIES='):
            loading = 'ENTITIES'
            pass
        
        if loading == 'ENTITIES':
            if line.startswith('END_ENTITIES'):
                loading = None
                pass
            elif line.startswith('ENTITIES'):
                pass
            else:
                print('Adding entity')
                entity = createEntity(level.name, line.strip())
                level.addEntity(entity)

        # Get objects
        if line.startswith('OBJECTS'):
            loading = 'OBJECTS'
            pass

        if loading == 'OBJECTS':
            if line.startswith('END_OBJECTS'):
                loading = None
                pass
            elif line.startswith('OBJECTS'):
                pass
            else:
                print('Adding object')
                objAndAmt = createObject(line.strip())
                level.addObject(objAndAmt[0], objAndAmt[1])

        # Get the mode
        if line.startswith('MODE='):
            level.setMode(int(line.strip('MODE=')))

        


    file.close()
    return level

def bodiesCollide(body1, body2): # Check to see if one list of 3D coords intersects with another list of 3D coords.
    for i in body1:
        for j in body2:
            if tuple(i) == tuple(j):
                return True
    return False


def createEntity(levelName, fileName): # Create an Entity object from a .ent file in "Data/Rooms/levelName/entities".
    txtFile = txtLoad(['..', 'Data', 'Rooms', levelName, 'entities', fileName], 'r')
    entity = None
    entType = None
    entName = None
    entCoord = None
    entBody = None
    entVisible = None
    for line in txtFile:
        line = line.strip()
        
        if line.startswith('name'):
            splitLine = line.split('~')
            entName = splitLine[1]
        elif line.startswith('coord'):
            splitLine = line.split('~')
            entCoord = eval(splitLine[1])
        elif line.startswith('body'):
            splitLine = line.split('~')
            entBody = eval(splitLine[1])
        elif line.startswith('visible'):
            if line.endswith('Y'):
                entVisible = True
            elif line.endswith('N'):
                entVisible = False
        elif line.startswith('type'):
            splitLine = line.split('~')
            entType = splitLine[1]
            if entType == 'SpawnPt':
                entity = SpawnPt(fileName)
            elif entType == 'ExitPt':
                entity = ExitPt(fileName)
            elif entType == 'NPC':
                entity = NPC(fileName)
            elif entType == 'PressurePlate':
                entity = PressurePlate(fileName)
        

        # Insert code to deal with each specific type of entity here
        if entType == 'ExitPt':
            print('Ent is ExitPt')
            if line.startswith('type'):
                pass
            elif line.startswith('targetLevel'):
                splitLine = line.split('~')
                entity.setTargetMap(splitLine[1])
                print('Setting target map: ' + splitLine[1])
            elif line.startswith('targetSpawn'):
                splitLine = line.split('~')
                entity.setTargetSpawn(splitLine[1])
                print('Setting target spawn pt: ' + splitLine[1])

        if entType == 'PressurePlate':
            if line.startswith('type'):
                pass
            elif line.startswith('targetEntity'):
                splitLine = line.split('~')
                entity.setTargetEntity(splitLine[1])
            elif line.startswith('triggerType'):
                splitLine = line.split('~')
                entity.setTriggerType(splitLine[1])
            elif line.startswith('triggeredBy'):
                splitLine = line.split('~')
                entity.setTriggeredBy(splitLine[1])
            
    if entBody != None:
        entity.body = entBody
    if entVisible != None:
        entity.visible = entVisible
    entity.setName(entName)
    entity.moveToCoord(entCoord)
    txtFile.close()
    return entity

def createObject(string):
    # Fill this in later/as you add more Objects
    if string == 'X':
        return None
    elif string.startswith('TestItem'):
        splitText = string.split('|')
        print(string)
        print(splitText)
        obj = TestItem([int(splitText[1]), int(splitText[2]), int(splitText[3])])
        amt = int(splitText[4])
        return (obj, amt)

def getKeybinds():
    configFile = open('config.cfg', 'r')
    for line in configFile:
        line = line.strip()
        splitLine = line.split('~')
        action = splitLine[0]
        binds = splitLine[1].split('|')
        KEYBINDS.update({action:binds})

def getInput(): # Find what actions are currently being pressed down.
    keyPresses = pygame.key.get_pressed()
    inputs = []
    for i in KEYBINDS:
        for j in KEYBINDS[i]:
            if j.startswith('K_'):
                key = int(j.strip('K_'))
                if keyPresses[key]:
                    inputs.append(i)
                    
    return inputs

def keyUp(action, currentInput, lastInput):
    return ((action in lastInput) and (action not in currentInput))

def keyDown(action, currentInput, lastInput):
    return ((action in currentInput) and (action not in lastInput))

def calcDirFromVector(vector):
    x = vector[0]
    y = vector[1]
    quadrant = 0

    # First do a quick determination if we have a vertical/horizontal vector
    if x == 0:
        if y >= 0:
            return S # Face south by default
        else:
            return N

    if y == 0:
        if x > 0:
            return E
        elif x < 0:
            return W

    # If the quick determinations didn't work
    # Get the tangent
    tangent = y / x
    # Calculate the angle
    angle = atan(tangent)
    if angle < 0: # If it's negative
        angle += (2 * pi) # Convert it to its positive form

    # Apply necessary corrections if in the second or third quadrants
    if x < 0:
        if y > 0:
            angle -= pi
        elif y < 0:
            angle += pi
        
    # Calculate which direction we're facing.
    # 45 degrees = pi/4 radians.
    if (angle > (15 * pi / 8) and angle <= (2 * pi)) or (angle >= 0 and angle <= (pi / 8)): # E = 15pi/8 to pi/8
        return E
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # SE = pi/8 to 3pi/8
        return SE
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # S = 3pi/8 to 5pi/8
        return S
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # SW = 5pi/8 to 7pi/8
        return SW
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return W
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # NW = 9pi/8 to 11pi/8
        return NW
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # N = 11pi/8 to 13pi/8
        return N
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # NE = 13pi/8 to 15pi/8
        return NE



def calcDirFromAngle(angle):
    # Takes in angle (in radians) and returns a string like "N" or "SE"
    # Calculate which direction we're facing.
    # 45 degrees = pi/4 radians.
    if (angle > (15 * pi / 8) and angle <= (2 * pi)) or (angle >= 0 and angle <= (pi / 8)): # E = 15pi/8 to pi/8
        return E
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # NE = pi/8 to 3pi/8
        return SE
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # N = 3pi/8 to 5pi/8
        return S
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # NW = 5pi/8 to 7pi/8
        return SW
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return W
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # SW = 9pi/8 to 11pi/8
        return NW
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # S = 11pi/8 to 13pi/8
        return N
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # SE = 13pi/8 to 15pi/8
        return NE


def startMenu():
    # Let's do simple text-based stuff for now
    print("""
***  THE ISLE OF MALKHAR  ***
(demo 1)

1. New Game
2. Load Game""")
    choice = int(input('Your choice:  '))
    if choice == 1:
        saveFile = 'NewGame.sav'
    elif choice == 2:
        saveFile = 'Continue.sav'
    else:
        print('Invalid choice, exiting program...')
        pygame.quit()
        sys.exit()
        
    print()
    return saveFile

WX = 1024
WY = 768
WINDOW = pygame.display.set_mode((WX, WY), 0, 32)
pygame.display.set_caption('The Isle Of Malkhar [v.0.1]')

# Symbolic constants
TILE_SIZE = 32
VIEWPORT_SIZE = 768
VIEWSURF_PLUS_BUFFER = VIEWPORT_SIZE + (TILE_SIZE * 2)
FRAMES_PER_SECOND = 30 # I think 30 fps is the most we can squeeze out of Python and Pygame, but if it's set to 60 I can see how far I can stretch that.

# Symbolic direction constants
DIRECTION_NUMBERS = {"N":4, "NW":5, "W":6, "SW":7, "S":0, "SE":1, "E":2, "NE":3}
N = DIRECTION_NUMBERS["N"]
S = DIRECTION_NUMBERS["S"]
E = DIRECTION_NUMBERS["E"]
W = DIRECTION_NUMBERS["W"]
NE = DIRECTION_NUMBERS["NE"]
NW = DIRECTION_NUMBERS["NW"]
SE = DIRECTION_NUMBERS["SE"]
SW = DIRECTION_NUMBERS["SW"]

V_COLOR = (0, 255, 0)   # moVement
M_COLOR = (255, 0, 0)   # Magic
I_COLOR = (0, 0, 255)   # Interaction
D_COLOR = (255, 255, 0) # Defense

# Surfaces and corresponding Rects
VIEWSURF = pygame.Surface((768, 768))
VIEWRECT = pygame.Rect(0, 0, 768, 768)
HUDSURF = pygame.Surface((256, 768))
HUDRECT = pygame.Rect(768, 0, 256, 768)

DUMMY_SURFACE = pygame.Surface((0, 0))

TXT_TEMPLATE_SURFACE = pygame.surface.Surface((768, 128))
TXT_TEMPLATE_SURFACE.fill((127, 127, 127))

CHRONO = pygame.time.Clock()
KEYBINDS = {}
getKeybinds()

TXTFONT = pygame.font.Font('cour.ttf', 36)
TXTFONT.set_bold(True)
M_TXTFONT = pygame.font.Font('cour.ttf', 16)
M_TXTFONT.set_bold(True)
DEFAULT_FONT = pygame.font.Font(None, 24)
DEFAULT_FONT_COLOR = (255, 255, 255)
# NTS, find some better fonts
# ...and give them better names

# Import files
import offsetFunctions
from offsetFunctions import *

import dialogBox
from dialogBox import *

import block
from block import *

import spriteSheet
from spriteSheet import *

import animation
from animation import *

import animSheet
from animSheet import *

import gfx
from gfx import *

import tiom_object
from tiom_object import *

import entity
from entity import *

import npc
from npc import *

import action
from action import *

import player
from player import *

import hud
from hud import *

import level
from level import *

import savegame
from savegame import *

# Wait until all files are loaded before starting the game
if (level.finished and spriteSheet.finished and block.finished and animation.finished and animSheet.finished and player.finished and entity.finished and action.finished and hud.finished and dialogBox.finished and npc.finished and savegame.finished and tiom_object.finished and gfx.finished):  # Add to this line as necessary as you add more files
    startingSaveFile = startMenu()
    SAVEGAME = SaveGame(startingSaveFile)
    SAVEGAME.loadFile()
    PLAYER = Player('DummyFileName')
    PLAYER.loadFromSave(SAVEGAME)
    levelName = SAVEGAME.currentLevel
    spawnPt = None
    while True:
        currentLevel = loadLevel(levelName)
        levelName, spawnPt = currentLevel.play(spawnPt, PLAYER, SAVEGAME)

    
    # testLevel = loadLevel('testLevel')
    # testLevel.play("Spawn1", PLAYER)
