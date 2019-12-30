# TIOM GFX class and derived classes.

finished = False
print('Loading GFX classes...')

import Main
from Main import *

class GFX:
    def __init__(self, level, startCoord):
        self.surface = DUMMY_SURFACE
        self.coord = startCoord
        self.level = level
        self.motion = noMotion
        self.frameCounter = 0

    def getSurface(self):
        return self.surface

    def getCoord(self):
        return self.coord

    def setMotion(self, newMotion):
        self.motion = newMotion

    def frameTick(self): # Override for each derived class.
        pass

class FadeIn(GFX):
    def __init__(self, level, startCoord):
        GFX.__init__(self, level, startCoord)
        self.surface = pygame.Surface((WX, WY))
        self.surface.fill((0,0,0))

    def frameTick(self):
        if self.frameCounter < 17:
            self.surface.set_alpha(255 - (16 * self.frameCounter))
            self.frameCounter += 1
        else:
            self.level.removeGFX(self)
        

class FadeOut(GFX):
    def __init__(self, level, startCoord):
        GFX.__init__(self, level, startCoord)
        self.surface = pygame.Surface((WX, WY))
        self.surface.fill((0,0,0))

    def frameTick(self):
        if self.frameCounter < 17:
            self.surface.set_alpha((16 * self.frameCounter) + 1)
            self.frameCounter += 1
        else:
            self.level.removeGFX(self)

print('Done loading GFX classes')
finished = True
