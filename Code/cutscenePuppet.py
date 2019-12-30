# TIOM CutscenePuppet class.

finished = False
print('Loading CutscenePuppet class...')

import Main
from Main import *

class CutscenePuppet:
    # An object with a spritesheet and animations and such.  Load them from .pup files in the cutscene folder.
    def __init__(self, sceneName, filename):
        self.name = ''
        self.sceneName = sceneName
        self.filename = filename
        self.spriteSheet = None
        self.coord = (0,0)
        self.currentAnimation = None
        self.animFrameCounter = 0
        self.animations = {}
        self.visible = True
        self.direction = (0, 1, 0)

        self.motion = noMotion

        self.loadFromFile()

        self.sprite = DUMMY_SURFACE

    def loadFromFile(self):
        file = txtLoad(['..', 'Data', 'Cutscenes', self.sceneName, 'puppets', self.filename], 'r')
        loadingAnimations = False
        for line in file:
            line = line.strip()
            if line.startswith('VISIBLE'):
                if line.endswith('Y'):
                    self.visible = True
                else:
                    self.visible = False

            elif line.startswith('NAME'):
                self.name = line.split('=')[1]
                    
            elif line.startswith('SPRITESHEET'):
                sheetArgs = line.split('=')[1].split('|')
                self.spriteSheet = SpriteSheet(sheetArgs[0], int(sheetArgs[1]), int(sheetArgs[2]), (255, 0, 255))

            elif line.startswith('ANIMATIONS'):
                loadingAnimations = True

            if loadingAnimations:
                if line.startswith('ANIMATIONS'):
                    pass
                elif line.startswith('END_ANIMATIONS'):
                    loadingAnimations = False
                else:
                    animName = line.split('=')[0]
                    frameData = line.split('=')[1].split('|')
                    frames = {}
                    for f in frameData:
                        f = f.split(',')
                        if len(f) == 2: # Then it's a frame#,goto: sort of deal
                            frames.update({int(f[0]):f[1]})
                        elif len(f) == 3: # Then it's a frame#,x,y sort of deal
                            frames.update({int(f[0]):(int(f[1]), int(f[2]))})

                    # Create an AnimSheet object and add it to self.animations
                    animation = AnimSheet(self.spriteSheet, frames)
                    self.animations.update({animName:animation})

        file.close()

    def frameTick(self):
        self.coord[0] += self.motion(self.animFrameCounter, self.direction)[0]
        self.coord[1] += self.motion(self.animFrameCounter, self.direction)[1]
        self.sprite = self.currentAnimation.getCurrentSprite((calcDirFromVector(self.direction), 0))
        if type(self.sprite) == type(''):
            # Do something, Taipu
            #print('self.sprite is a string:  ' + self.sprite)
            if self.sprite.startswith('changeAnim'):
                newAnim = self.sprite.split(':')[1]
                self.changeAnimation(newAnim)
        self.currentAnimation.frameTick()
        self.sprite = self.currentAnimation.getCurrentSprite((calcDirFromVector(self.direction), 0))
        
        self.animFrameCounter += 1
        

    def move(self, x, y):
        self.coord = [x, y]

    def changeDirection(self, x, y, z):
        self.direction = (x, y, z)

    def changeMotion(self, newMotion):
        self.motion = newMotion
        self.animFrameCounter = 0

    def changeAnimation(self, newAnim):
        self.currentAnimation = self.animations[newAnim]
        self.currentAnimation.reset()

    def getSprite(self):
        return self.sprite

finished = True
print('Done loading CutscenePuppet class')
