# Yet another animation class.  This one is just a rule of which sprite to use, it doesn't apply to any one specific sprite sheet.

finished = False
print('Loading AnimRule class...')

import Main
from Main import *


class AnimRule:
    def __init__(self, frames=None):
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

    def getCurrentSprite(self, sheet, spriteStartingCoord):
        return sheet.getSprite((spriteStartingCoord[0] + self.currentSprite[0], spriteStartingCoord[1] + self.currentSprite[1]))

    def goToFrame(self, frameNum):
        # Note:
        # Make sure frameNum is one of the values in self.frames.
        if frameNum in self.frames:
            self.frameCount = frameNum
            self.currentSprite = self.frames[frameNum]

    def getSpriteAtFrame(self, sheet, spriteStartingCoord, frameNum):
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


        return sheet.getSprite((spriteStartingCoord[0] + spriteToReturn[0], spriteStartingCoord[1] + spriteToReturn[1]))

    def reset(self):
        self.frameCount = 0
        self.currentSprite = self.frames[self.frameCount]


# Insert animation rules here
SIMPLE_IDLE = AnimRule({0:(0, 0),
                        1:'goto:0'})

SIMPLE_TALK = AnimRule({0:(0, 0),
                        3:(0, 1),
                        6:'goto:0',
                        -1:'changeAnim:idle'})

ANIM_RULES = {'idle':SIMPLE_IDLE,
              'talk':SIMPLE_TALK}

print('Done loading AnimRule class')
finished = True
