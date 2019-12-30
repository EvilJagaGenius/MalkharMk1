# TIOM player class.
finished = False
print("Loading Player class...")

import Main
from Main import *

class Player(Entity):
    def __init__(self, dummyFile):
        Entity.__init__(self, dummyFile)
        self.body = [[0,0,0], [0,0,1]]
        self.coord = [0,0,0]
        self.type = "Player"
        self.name = "Player"
        self.control = "Player"
        self.solid = True
        self.visible = True

        self.head = self.body[1]
        self.feet = self.body[0]

        self.speed = 1  # 0 is sneaking/crawling, 1 is walking, 2 is running
        
        # Stats
        self.stats = {
            "phy":{     # Physical
                "str":1,    # Strength
                "con":1,    # Constitution
                "agi":1,    # Agility
                "dex":1,    # Dexterity
                "per":1,    # Perception
                "wil":1},   # Willpower
            "mag":{     # Magic
                "ruby":0,   # Ruby/Fire
                "emer":0,   # Emerald/Air
                "ambr":0,   # Amber/Earth
                "saph":0,   # Sapphire/Water
                "aqua":0,   # Aquamarine/Lightning
                "diam":0,   # Diamond/Ice
                "amth":0},  # Amethyst/Nature
            "pts":{     # Points
                "chp":100,  # Current HP
                "mhp":100,  # Max HP
                "cep":100,  # Current EP
                "mep":100,  # Max EP
                "cap":10,   # Current AP
                "map":10}   # Max AP
            }

        self.buffs = []
        
        self.equipment = {'Right Hand':None,
                          'Left Hand':None,
                          'Right Ammo':None,
                          'Left Ammo':None,
                          'Armor':None,
                          'Amulet':None}

        
        # Actions
        self.baseActions = {
            "V":MovementSwitch(),
            "M":MagicSwitch(),
            "I":InteractSwitch(),
            "D":DefenseSwitch(),
            }

        
        self.vActions = {
            "V":MovementSwitch(),
            "M":None,
            "I":ChangeSpeed(),
            "D":Jump(),
            }

        self.mActions = {
            "V":None,
            "M":MagicSwitch(),
            "I":None,
            "D":None,
            }

        self.iActions = {
            "V":Pickup(),
            "M":Talk(),
            "I":InteractSwitch(),
            "D":None,
            }

        self.dActions = {
            "V":None,
            "M":None,
            "I":None,
            "D":DefenseSwitch(),
            }

        self.tempActions = {
            "V":None,
            "M":None,
            "I":None,
            "D":None,
            }

        self.currentActions = self.baseActions
        self.actionsBeforeAiming = self.baseActions

        # Sprites and animation
        self.spriteSheet = SpriteSheet('PlayerSheet.png', 64, 64, (255, 0, 255))
        self.direction = [0, 1, 0]
        

        self.animations = {'idle':AnimSheet(self.spriteSheet,
                                  {0:(0, 0),
                                   1:'goto:0',
                                   -1:'goto:0'}),
                           'talk':AnimSheet(self.spriteSheet,
                                  {0:(0, 0),
                                   3:(0, 1),
                                   6:'goto:0',
                                   -1:'changeAnim:idle'})}

        self.currentAnim = self.animations['idle']
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))

        self.moving = False
        self.animFrameCounter = 0
        self.offsetFormula = noOffset

        self.inventory = {}
        self.sheaths = {'Sheath One':None,
                        'Sheath Two':None}

        
    def getSprite(self):
        return self.sprite


    def getCurrentActions(self):
        return self.currentActions


    def switchToAiming(self, actionPos): # actionPos being either V, M, I, or D
        self.tempActions[actionPos] = self.currentActions[actionPos]
        upPos = None
        downPos = None
        cancelPos = None
        if actionPos == 'V':
            upPos = 'D'
            downPos = 'I'
            cancelPos = 'M'
        elif actionPos == 'M':
            upPos = 'D'
            downPos = 'V'
            cancelPos = 'I'
        elif actionPos == 'I':
            upPos = 'D'
            downPos = 'V'
            cancelPos = 'M'
        elif actionPos == 'D':
            upPos = 'I'
            downPos = 'V'
            cancelPos = 'M'
        self.tempActions[upPos] = AimUp()
        self.tempActions[downPos] = AimDown()
        self.tempActions[cancelPos] = Cancel()

        self.actionsBeforeAiming = self.currentActions
        self.currentActions = self.tempActions


    def stopAiming(self):
        self.tempActions['V'] = None
        self.tempActions['M'] = None
        self.tempActions['I'] = None
        self.tempActions['D'] = None

        self.currentActions = self.actionsBeforeAiming
        self.actionsBeforeAiming = self.baseActions


    def loopThroughActions(self):
        for a in self.currentActions:
            action = self.currentActions[a]
            if action != None:
                action.useSource(self)

                
    def frameTick(self):
        self.loopThroughActions()
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))
        if type(self.sprite) == type(''):
            # Do something, Taipu
            #print('self.sprite is a string:  ' + self.sprite)
            if self.sprite.startswith('changeAnim'):
                newAnim = self.sprite.split(':')[1]
                self.changeAnim(newAnim)
        self.currentAnim.frameTick()
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))
        if self.moving:
            self.animFrameCounter += 1


    def changeAnim(self, newAnim): # newAnim is a string, a key in self.animations
        if newAnim in self.animations:
            # Reset current animation
            self.currentAnim.reset()
            # Switch to new animation
            self.currentAnim = self.animations[newAnim]
            self.currentAnim.reset()
            self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))


    def changeOffsetForm(self, newOffsetForm):
        self.offsetFormula = newOffsetForm


    def resetAnimation(self):
        self.offsetFormula = noOffset
        self.moving = False
        self.animFrameCounter = 0

        self.changeAnim('idle')

    def loadFromSave(self, savegame):
        self.stats = savegame.playerStats
        self.inventory = savegame.playerInventory
        self.buffs = savegame.playerBuffs
        self.moveToCoord(savegame.playerCoord)
        self.direction = savegame.playerDirection

    def addToInventory(self, obj, amt):
        if obj in self.inventory:
            self.inventory[obj] += amt
            return True
        else:
            self.inventory.update({obj:amt})
            return True

    def inventoryScreen(self, level):
        # I'm really not sure what class to put this in... so I guess this works for now?
        lastInput = []
        while True:
            WINDOW.fill((0,0,0))
            currentInput = getInput()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if keyUp("M", currentInput, lastInput):
                return

            y = 0
            for i in self.inventory:
                WINDOW.blit(i.getSprite(), (0, y))
                WINDOW.blit(DEFAULT_FONT.render(i.screenName, True, (255,255,255)), (32, y))
                y += 32
                

            pygame.display.update()
            lastInput = currentInput



finished = True
print("Done loading Player class")
