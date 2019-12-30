# Running some tests for the animation code.

import pygame, sys, os, math
from pygame import *
from math import *
pygame.init()

CHRONO = pygame.time.Clock()
FONT = pygame.font.Font(None, 20)
FRAMES_PER_SECOND = 30
DIRECTION_NUMBERS = {"N":0, "NW":1, "W":2, "SW":3, "S":4, "SE":5, "E":6, "NE":7}

WX = 800
WY = 600
window = pygame.display.set_mode((WX, WY), 0, 32)

class SpriteSheet:
    def __init__(self, sheet, spriteX, spriteY, colorkey=None):  # All sprites must have the same dimensions
        self.spriteX = spriteX
        self.spriteY = spriteY
        if sheet != None:
            self.sheet = imgLoad(['..', 'Data', 'Sprites', sheet]).convert() # Original reference image
        else:
            self.sheet = pygame.Surface((spriteX, spriteY))
            self.sheet.fill((0,0,0))
        
        self.filename = sheet
        if colorkey != None:
            self.sheet.set_colorkey(colorkey)


        # Generate a matrix of sprites
        self.matrix = []
        x = 0
        y = 0
        row = 0
        while y <= self.sheet.get_height() - self.spriteY:
            self.matrix.append([])
            while x <= self.sheet.get_width() - self.spriteX:
                spriteRect = pygame.rect.Rect(x, y, self.spriteX, self.spriteY)
                spriteImg = self.sheet.subsurface(spriteRect)
                self.matrix[row].append(spriteImg)
                
                x += self.spriteX
                
            x = 0
            y += self.spriteY
            row += 1

                
    def getSprite(self, coord): # x and y are the x and y positions of the sprite.  So, getSprite(3, 2) would return the third sprite in the second row of sprites.
        if coord[0] >= 0 and coord[1] >= 0:
            return self.matrix[coord[1]][coord[0]]


class AnimSheet:
    def __init__(self, sheet, frames=None):
        self.sheet = sheet
        self.frames = frames
        self.frameCount = 0
        self.currentSprite = (0, 0)

    def setFrames(self, frames):
        # self.frames is supposed to be a dictionary, like so:
        # self.frames = {frameNum:spriteCoord, frameNum2:spriteCoord2, ... frameNumN:spriteCoordN}
        # Also, instead of spriteCoord being an (x, y) or [x, y] coord, it could be a statement like 'goto:frameNum'.
        self.frames = frames

    def frameTick(self):
        self.frameCount += 1
        if self.frames != None:
            if self.frameCount in self.frames:
                # Do something, Taipu
                if type(self.frames[self.frameCount]) == type(''):
                    # Then it's probably a goto statement or something similar.  Fill in later.
                    if self.frames[self.frameCount].startswith('goto'):
                        splitLine = self.frames[self.frameCount].split(':')
                        desiredFrame = int(splitLine[1])
                        self.goToFrame(desiredFrame)
                else: # If it's not a string then it's an (x, y) or [x, y] coord.
                    self.currentSprite = self.frames[self.frameCount]

    def getCurrentSprite(self, spriteStartingCoord):
        return self.sheet.getSprite((spriteStartingCoord[0] + self.currentSprite[0], spriteStartingCoord[1] + self.currentSprite[1]))

    def goToFrame(self, frameNum):
        # Note:
        # Make sure frameNum is one of the values in self.frames.
        if frameNum in self.frames:
            self.frameCount = frameNum
            self.currentSprite = self.frames[frameNum]

    def getSpriteAtFrame(self, spriteStartingCoord, frameNum):
        # Basically:
        # Loop through the frames, follow along with the instructions and all
        # Return the resulting sprite coord
        pass


class Animation:  # A chain of sprites and frame numbers.
    def __init__(self, sheet, frames=None):
        # frames should be a dictionary.  Like so: {0:sprite, frameNum:sprite}
        # Or you could have something like 'goto:frameNum', just make sure that frameNum is an index in frames
        self.frames = frames
        self.frameCount = 0
        self.currentSprite = self.frames[self.frameCount]

    def setFrames(self, frames):
        self.frames = frames

    def getSpriteAtFrame(self, frameNum):
        # Loop through the frames in the animation and return the sprite at the desired frame number
        counter = 0
        for i in range(frameNum):
            if counter in self.frames:
                if type(self.frames[counter]) == type(''): # If the thing at that frame number isn't a sprite, but a string
                    if self.frames[counter].startswith('goto:'): # If it's goto:frameNum
                        a = self.frames[counter]
                        b = a.split(':')
                        c = int(b[1])
                        counter = c

                else:
                    spriteToReturn = self.frames[counter]

            counter += 1


        return self.sheet.getSprite(spriteToReturn)

    def frameTick(self):
        # Increment the Animation's frame counter and change the current sprite, if necessary
        self.frameCount += 1
        if self.frames != None:
            if self.frameCount in self.frames:
                if type(self.frames[self.frameCount]) == type('string'): # If the thing at that frame number isn't a sprite, but a string
                    if self.frames[self.frameCount].startswith('goto:'): # If it's goto:frameNum
                        a = self.frames[self.frameCount]
                        b = a.split(':')
                        c = int(b[1])
                        self.frameCount = c
                else:
                    self.currentFrame = self.frames[self.frameCount]

    def getCurrentSprite(self):
        # Return the current sprite
        return self.currentSprite

# That should be it for custom classes.

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

def calcVector(vector):
    x = vector[0]
    y = vector[1]
    quadrant = 0

    # First do a quick determination if we have a vertical/horizontal vector
    if x == 0:
        if y > 0:
            return "N"
        else:
            return "S" # Face south by default

    if y == 0:
        if x > 0:
            return "E"
        elif x < 0:
            return "W"

    
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
        return "E"
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # NE = pi/8 to 3pi/8
        return "NE"
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # N = 3pi/8 to 5pi/8
        return "N"
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # NW = 5pi/8 to 7pi/8
        return "NW"
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return "W"
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # SW = 9pi/8 to 11pi/8
        return "SW"
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # S = 11pi/8 to 13pi/8
        return "S"
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # SE = 13pi/8 to 15pi/8
        return "SE"

def calcAngle(angle):
    # Takes in angle (in radians) and returns a string like "N" or "SE"
    # Calculate which direction we're facing.
    # 45 degrees = pi/4 radians.
    if (angle > (15 * pi / 8) and angle <= (2 * pi)) or (angle >= 0 and angle <= (pi / 8)): # E = 15pi/8 to pi/8
        return "E"
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # NE = pi/8 to 3pi/8
        return "NE"
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # N = 3pi/8 to 5pi/8
        return "N"
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # NW = 5pi/8 to 7pi/8
        return "NW"
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return "W"
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # SW = 9pi/8 to 11pi/8
        return "SW"
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # S = 11pi/8 to 13pi/8
        return "S"
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # SE = 13pi/8 to 15pi/8
        return "SE"


testSheet = SpriteSheet('TestSpriteSheet.png', 64, 64)

testAnimSheet = AnimSheet(testSheet)
testFrames = {0:(0, 0),
              5:(0, 1),
              10:(0, 2),
              15:(0, 3),
              20:'goto:0'}
testAnimSheet.setFrames(testFrames)


# Main loop goes here
while True:
    window.fill((0,0,0))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Blit sprites
    for i in range(8):
        window.blit(testAnimSheet.getCurrentSprite((i, 0)), (i*64, 0))

    testAnimSheet.frameTick()
    
    

    window.blit(FONT.render(str(int(CHRONO.get_fps())), True, (255, 255, 255)), (200, 200))

    pygame.display.update()
    CHRONO.tick(FRAMES_PER_SECOND)

    


