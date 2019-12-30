# TIOM Object class and possibly derived classes as well.
# Objects are like Entities, except where Entities can be referenced by name, Objects have no names and can only be referenced by coordinate.

finished = False
print('Loading Object classes...')

import Main
from Main import *

OVERWORLD_OBJECT_SHEET = SpriteSheet('OverworldObjectSheet.png', 32, 32)
INVENTORY_ICON_SHEET = SpriteSheet('InventoryIconSheet.png', 32, 32)

class TIOM_Object:
    def __init__(self, coord=[0,0,0]):
        self.canPickUp = False # Stuff like grenades and landmines are objects too, and you DON'T want to be stuffing those in your pack.  Though it might be funny...
        self.canHold = False
        self.coord = coord
        self.tags = []
        self.overworldSpriteCoord = (0,0)
        self.visible = False

    def APTick(self): # Each point of AP that passes, call this function.
        pass

    def getSprite(self): # For Objects, getSprite() will give you the overworld sprite.
        return OVERWORLD_OBJECT_SHEET.getSprite(self.overworldSpriteCoord)

    def getSaveString(self):
        return ''
    

class InventoryItem(TIOM_Object):
    def __init__(self, coord=[0,0,0]):
        TIOM_Object.__init__(self, coord)
        self.canPickUp = True # All InventoryItems can be picked up and put into your pack, thus this variable is True.
        self.visible = True
        self.saveString = ''
        self.screenName = ''
        self.inventoryIconCoord = (0,0)
        self.tags.append('InventoryItem')

    def getInventoryIcon(self):
        return INVENTORY_ICON_SHEET.getSprite(inventoryIconCoord)
        

class TestItem(InventoryItem):
    def __init__(self, coord=[0,0,0]):
        InventoryItem.__init__(self, coord)
        self.screenName = 'Test Item'

    def getSaveString(self):
        return 'TestItem|' + str(self.coord[0]) + '|' + str(self.coord[1]) + '|' + str(self.coord[2])

print('Done loading Object classes')
finished = True
