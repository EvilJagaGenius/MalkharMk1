# TIOM Entity class.  This file may contain derived classes as well.

finished = False
print("Loading Entity classes...")

import Main
from Main import *

class Entity:
    def __init__(self, file):
        self.fileName = file
        self.name = 'Unnamed'
        self.body = [[0,0,0]]
        self.coord = [0,0,0]
        self.type = 'NoType'
        self.solid = False
        self.visible = False
        self.visState = ['idle', S, 0]
        self.spriteOffset = (0, 0)
        self.sprite = DUMMY_SURFACE
        self.level = None
        self.canTalk = False
        self.canExamine = False
        self.rect = pygame.rect.Rect(0, 0, 0, 0)
        self.direction = [0, 1, 0]

        self.moving = False
        self.animFrameCounter = 0
        self.offsetFormula = noOffset

    def setName(self, newName):
        self.name = newName

    def getName(self):
        return self.name

    def moveByDelta(self, delta, changeDirection=False): # Move the entity so many units in each direction.  delta is a list or tuple, like so: [deltaX, deltaY, deltaZ]
        self.coord[0] += delta[0]
        self.coord[1] += delta[1]
        self.coord[2] += delta[2]
        for i in self.body:
            i[0] += delta[0]
            i[1] += delta[1]
            i[2] += delta[2]

        if changeDirection:
            self.direction = delta

    def moveToCoord(self, newCoord, changeDirection=False): # Move the entity to a new coordinate.
        delta = (newCoord[0] - self.coord[0], newCoord[1] - self.coord[1], newCoord[2] - self.coord[2])
        self.coord[0] += delta[0]
        self.coord[1] += delta[1]
        self.coord[2] += delta[2]
        for i in self.body:
            i[0] += delta[0]
            i[1] += delta[1]
            i[2] += delta[2]

        if changeDirection:
            self.direction = delta

    def getCoord(self):
        return self.coord

    def getBody(self):
        copyBody = []
        for i in self.body:
            copyBody.append(i.copy())
        return copyBody

    def getSprite(self): # Meant to be overriden
        return self.sprite

    def getSpriteOffset(self): # Meant to be overriden
        return self.offsetFormula(self, self.animFrameCounter)

    def setLevel(self, level): # Override if necessary
        self.level = level

    def getTalkativity(self):
        return self.canTalk

    def calcRect(self):
        self.rect.left = self.coord[0] * TILE_SIZE
        self.rect.top = (self.coord[1]) * TILE_SIZE - (self.coord[2] * TILE_SIZE) # Factor in vertical distance
        spriteWidth = self.sprite.get_width()
        spriteHeight = self.sprite.get_height()
        self.rect.height = spriteHeight
        self.rect.width = spriteWidth
        self.rect.top -= spriteHeight - TILE_SIZE
        self.rect.left -= (spriteWidth - TILE_SIZE) / 2

    def frameTick(self):
        pass

    def resetAnimation(self):
        pass

    def changeDirection(self, newDirection):
        pass

    def changeOffsetForm(self, newOffsetForm):
        if newOffsetForm == 'noOffset':
            self.offsetFormula = noOffset
        elif newOffsetForm == 'simpleMovement':
            self.offsetFormula = simpleMovementOffset


# Derived classes
class SpawnPt(Entity):
    def __init__(self, file):
        Entity.__init__(self, file)
        self.name = 'Unnamed'
        self.coord = [0,0,0]
        self.type = 'SpawnPt'

class ExitPt(Entity):
    def __init__(self, file):
        Entity.__init__(self, file)
        self.name = 'Unnamed'
        self.coord = [0,0,0]
        self.type = 'ExitPt'
        self.targetMap = 'NoMap'
        self.targetSpawn = 'NoSpawn'

    def setTargetMap(self, newTarget):
        self.targetMap = newTarget

    def setTargetSpawn(self, newTarget):
        self.targetSpawn = newTarget

class PressurePlate(Entity):
    def __init__(self, file):
        Entity.__init__(self, file)
        self.type = 'PressurePlate'
        self.targetEntity = 'NoTarget'
        self.triggerType = 'NoTriggerType'
        self.triggeredBy = None

    def setTargetEntity(self, newEnt):
        self.targetEntity = newEnt

    def setTriggerType(self, newTriggerType):
        self.triggerType = newTriggerType

    def setTriggeredBy(self, triggeredBy):
        self.triggeredBy = triggeredBy

    def trigger(self, source): # Source is the entity or object that triggered the plate
        if source.type == self.triggeredBy:
            if self.triggerType == 'Talk':
                self.level.entities[self.targetEntity].talk()
                self.level.conversation.paused = False

finished = True
print("Done loading Entity classes")
