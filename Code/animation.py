# Animation class.

finished = False
print("Loading Animation class...")

import Main
from Main import *

# Animation stuff
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

    def reset(self):
        self.frameCount = 0
        self.currentSprite = self.frames[self.frameCount]

finished = True
print("Done loading Animation class")
