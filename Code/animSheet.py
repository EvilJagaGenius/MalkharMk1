# TIOM animated spritesheet class.
# It's like an animation, but applied to an entire sheet of sprites.

finished = False
print('Loading AnimSheet class...')

import Main
from Main import *

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

    def frameTick(self, advFrame=True):
        if advFrame:
            self.frameCount += 1
        if self.frames != None:
            if self.frameCount in self.frames:
                self.currentSprite = self.frames[self.frameCount]
                # Do something, Taipu
                if type(self.currentSprite) == type(''):
                    if self.currentSprite.startswith('goto'):
                        splitLine = self.frames[self.frameCount].split(':')
                        desiredFrame = int(splitLine[1])
                        self.goToFrame(desiredFrame)
                else: # If it's not a string then it's an (x, y) or [x, y] coord.
                    self.currentSprite = self.frames[self.frameCount]

    def getCurrentSprite(self, spriteStartingCoord):
        if type(self.currentSprite) == type(''):
            return self.currentSprite
        else:
            return self.sheet.getSprite((spriteStartingCoord[0] + self.currentSprite[0], spriteStartingCoord[1] + self.currentSprite[1]))

    def goToFrame(self, frameNum):
        # Note: Make sure frameNum is one of the values in self.frames.
        if frameNum in self.frames:
            self.frameCount = frameNum
            self.currentSprite = self.frames[frameNum]

    def getSpriteAtFrame(self, spriteStartingCoord, frameNum):
        # Basically:
        # Loop through the frames, follow along with the instructions and all
        # Return the resulting sprite coord
        # Copied from the Animation() class
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


        return self.sheet.getSprite((spriteStartingCoord[0] + spriteToReturn[0], spriteStartingCoord[1] + spriteToReturn[1]))

    def reset(self):
        self.frameCount = 0
        self.currentSprite = self.frames[self.frameCount]



finished = True
print('Done loading AnimSheet class')
