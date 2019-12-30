# TIOM Action class.  All the things an item can do and what a player can do without holding an item.  The diamonds in the HUD.
# Might also contain some derived classes, IDK

finished = False
print("Loading Action class...")

import Main
from Main import *

ICON_SHEET = SpriteSheet('IconSheet.png', 32, 32, (255, 0, 255))

class Action:
    def __init__(self):
        self.spriteCoord = None         # Coordinate of icon on ICON_SHEET
        self.color = None               # Color of the icon
        self.name = "Unnamed"           # Name of action
        self.ap = 0                     # Time it takes to perform the action, in AP
        self.rechargeTime = 0           # How long you have to wait after performing the action before you can use it again
        self.timeRemaining = 0          # How long you have to wait until you can perform the action
        self.targets = 0                # How many targets the action affects
        self.targetArea = [[0, 0, 0]]   # Where you can aim the action


    def getSpriteCoord(self):
        return self.spriteCoord

    def setSprite(self, newSpriteCoord):
        # The idea: have a sprite sheet with all the action icons on it.
        # Give the action a coordinate and it'll pull its sprite from this sprite sheet.
        self.sprite = ICON_SHEET.getSprite(newSpriteCoord)
        self.spriteCoord = newSpriteCoord

    def getName(self): # Returns the name of the action.
        return self.name

    def getTargets(self): # Returns the amt. of targets to aim at.  If you don't want the action to be aimed, set self.targets to 0 and it'll automatically perform itself
        return self.targets

    def generateTargetArea(self, source, targetNum=1):
        pass

    def getTargetArea(self, source): # Meant to be overriden, returns a dummy list of coords
        return self.targetArea

    def perform(self, source, level, targetCoords): # Meant to be overriden
        pass

    def passTime(self, timePassed): # How much time in AP has passed?
        self.timeRemaining -= timePassed
        if self.timeRemaining <= 0:
            self.timeRemaining = 0

    def isValidTarget(self, source, target, targetNum=1): # Check to see if some target coordinate will work
        return True

    def useSource(self, source): # Give the action a source, and let it adjust its icon or color or whatever to suit said source, locking itself, etc.
        pass


# Let's test some actions.

class MoveOneStep(Action):
    def __init__(self):
        Action.__init__(self)
        self.targets = -1

    def perform(self, source, level, targetCoords):
        target = targetCoords[0]
        # Check to see if it's a valid position, if it's a tile at that position, if there are any entities in the way, etc etc...
        if not level.getBlockAt(target).type == 'Tile':
            return False
        else:
            targetBodyCoords = source.getBody()
            delta = (target[0] - source.coord[0], target[1] - source.coord[1], target[2] - source.coord[2]) # Get delta
            for i in targetBodyCoords:
                i[0] += delta[0]
                i[1] += delta[1]
                i[2] += delta[2]

                if level.getBlockAt(i).type == 'Block':
                    return False
                for e in level.entities:
                    ent = level.entities[e]
                    if ent.solid:
                        for j in ent.body:
                            if j == i:
                                return False

            # Assume it's all clear at this point
            source.moveToCoord(target, True)
            # Insert animation stuff here
            source.moving = True
            source.offsetFormula = simpleMovementOffset
            source.animFrameCounter = 0
            level.addAnimCommand(simpleMovementTime(source)+1, 'reset')
            level.animating = True
            level.pauseForAnimation = True


class Jump(Action):
    def __init__(self):
        Action.__init__(self)
        self.spriteCoord = (0, 2)
        self.name = "Jump"
        self.ap = 0
        self.rechargeTime = 0
        self.timeRemaining = 0
        self.targets = 1
        self.color = V_COLOR

    def generateTargetArea(self, source, targetNum=1):
        self.targetArea = radius.getRadius2D(2, source.feet)

    def getTargetArea(self):
        return self.targetArea
        
    def perform(self, source, level, targetCoords):
        source.moveToCoord(targetCoords[0], True)
        # Later there'll be a bunch of animation stuff going on but this works for now
        source.moving = True
        source.offsetFormula = simpleJumpOffset
        source.animFrameCounter = 0
        level.addAnimCommand(simpleJumpTime(source)+1, 'reset')
        level.animating = True
        level.pauseForAnimation = True

    def isValidTarget(self, source, level, target, targetNum=1):
        # How is this going to work...
        # First of all, check to see if the target coord is in the target area.
        # If so, get the delta between the target coord and the source's coord.
        # Use the delta to get the source's body coords should it move.  So you'll have source.body and targetBodyCoords.
        # Use Bresenham's Line Algorithm to create lines that the source would move along on the way to its destination.
        # Loop through the coordinates of those lines and check if any of them pass through a Block (or solid entity).
        # IF THEY DON'T... then you can return True.

        # Fortunately, this is how most of the isValidTarget() functions are gonna work, so I can copy and paste a lot of this

        if target in self.targetArea:   # See if it's in the target area
            delta = (target[0] - source.coord[0], target[1] - source.coord[1], target[2] - source.coord[2]) # Get delta
            # Find targetBodyCoords
            targetBodyCoords = source.getBody()
            for i in targetBodyCoords:
                i[0] += delta[0]
                i[1] += delta[1]
                i[2] += delta[2]
            # Generate lines with BLA
            for i in range(len(source.body)):
                line = bresenham.getLine3D(source.body[i], targetBodyCoords[i])
                # Loop along line
                for coord in line:
                    if level.getBlockAt(coord).type == 'Block': # See if there's a block at that coord
                        return False
                    
            return True
        else:
            return False

class ChangeSpeed(Action):
    def __init__(self):
        Action.__init__(self)
        self.spriteCoord = (2, 2)
        self.name = "Walking"
        self.color = V_COLOR

    def useSource(self, source):
        if source.speed == 0:
            self.spriteCoord = (3, 1)
            self.name = 'Sneaking'
        elif source.speed == 1:
            self.spriteCoord = (2, 2)
            self.name = 'Walking'
        elif source.speed == 2:
            self.spriteCoord = (3, 2)
            self.name = 'Running'

    def perform(self, source, level, targetCoords):
        print('Changing speed from ' + str(source.speed))
        if source.speed == 0:
            source.speed = 1
            self.spriteCoord = (2, 2)
            self.name = 'Walking'
        elif source.speed == 1:
            source.speed = 2
            self.spriteCoord = (3, 2)
            self.name = 'Running'
        elif source.speed == 2:
            source.speed = 0
            self.spriteCoord = (3, 1)
            self.name = 'Sneaking'

class Talk(Action):
    def __init__(self):
        Action.__init__(self)
        self.spriteCoord = (0, 3)
        self.name = "Talk/Read"
        self.ap = 0
        self.rechargeTime = 0
        self.timeRemaining = 0
        self.targets = 1
        self.color = I_COLOR

    def generateTargetArea(self, source, targetNum=1):
        self.targetArea = radius.getRadius3D(5, source.feet)

    def getTargetArea(self):
        return self.targetArea
        
    def perform(self, source, level, targetCoords):
        targetCoord = targetCoords[0]
        for e in level.entities:
            ent = level.entities[e]
            if targetCoord in ent.body:
                target = ent
        direction = (source.coord[0] - targetCoord[0], source.coord[1] - targetCoord[1], source.coord[2] - targetCoord[2])
        target.changeDirection(direction)
        target.talk()

    def isValidTarget(self, source, level, target, targetNum=1):
        if level.getBlockAt(target).type == 'Block':
            return False
        if target in self.targetArea: # See if it's in the target area
            # For talking, all we need to do is see the other guy.
            for e in level.entities:
                ent = level.entities[e]
                if ent.canTalk:
                    if target in ent.body:
                        return True
            return False
        else:
            return False


class Pickup(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = 'Pick Up'
        self.spriteCoord = (1, 3)
        self.color = I_COLOR

    def perform(self, source, level, targetCoords):
        print('Picking up an object...')
        for o in level.objects:
            obj = o[0]
            if obj.canPickUp and tuple(obj.coord) == tuple(source.coord):
                success = source.addToInventory(o[0], o[1])
                if success:
                    level.objects.remove(o)


class AimUp(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Aim Up"
        self.spriteCoord = (0, 1)
        self.color = (0, 255, 255)

    def perform(self, source, level, targetCoords):
        if level.cursorCoord[2] < level.levelZ - 1:
            level.cursorCoord[2] += 1
        else:
            print("Can't aim further up")

class AimDown(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Aim Down"
        self.spriteCoord = (1, 1)
        self.color = (0, 255, 255)

    def perform(self, source, level, targetCoords):
        if level.cursorCoord[2] > 0:
            level.cursorCoord[2] -= 1
        else:
            print("Can't aim further down")

class Cancel(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Cancel"
        self.spriteCoord = (2, 1)
        self.color = (255, 0, 0)

    def perform(self, source, level, targetCoords):
        level.aiming = False
        source.stopAiming()

class MovementSwitch(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Movement"
        self.spriteCoord = (0, 0)
        self.color = V_COLOR

    def perform(self, source, level, targetCoords):
        if source.currentActions == source.vActions:
            source.currentActions = source.baseActions
        else:
            source.currentActions = source.vActions
        source.loopThroughActions()

class MagicSwitch(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Magic"
        self.spriteCoord = (1, 0)
        self.color = M_COLOR

    def perform(self, source, level, targetCoords):
        if source.currentActions != source.mActions:
            source.currentActions = source.mActions
        else:
            source.currentActions = source.baseActions
        source.loopThroughActions()

class InteractSwitch(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Interact"
        self.spriteCoord = (2, 0)
        self.color = I_COLOR

    def perform(self, source, level, targetCoords):
        if source.currentActions != source.iActions:
            source.currentActions = source.iActions
        else:
            source.currentActions = source.baseActions
        source.loopThroughActions()

class DefenseSwitch(Action):
    def __init__(self):
        Action.__init__(self)
        self.name = "Defense"
        self.spriteCoord = (3, 0)
        self.color = D_COLOR

    def perform(self, source, level, targetCoords):
        if source.currentActions != source.dActions:
            source.currentActions = source.dActions
        else:
            source.currentActions = source.baseActions
        source.loopThroughActions()

MOVE_ONE_STEP = MoveOneStep()


finished = True
print("Done loading Action class")
