# TIOM savegame tests.
import os

def txtLoad(pathList, mode):
    filePath = os.path.join(*pathList)
    if not os.path.exists(filePath):
        file = open(filePath, 'w')
        file.close()
    file = open(filePath, mode)
    return file

class SaveGame:
    def __init__(self, filename):
        self.filename = filename
        self.comments = []
        
        self.currentLevel = None
        self.playerCoord = [0,0,0]
        self.playerDirection = [0,1,0]
        self.playerStats = {
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
        self.playerBuffs = [] # Buffs, debuffs, status effects, etc.  Aura spells, energy halos, and other spells that leave effects on the player go in here.
        self.playerEquipment = {'Right Hand':None,
                                'Left Hand':None,
                                'Right Ammo':None,
                                'Left Ammo':None,
                                'Armor':None,
                                'Amulet':None}
        self.playerInventory = {}
        
        self.levelEdits = {} # A dictionary.  Each key is the name of a level and each value is a list of string commands.


    def writeToFile(self):
        # Notes to self: Don't try writing to the original save file directly.  Try writing a new save file.  If that is successful, delete the old save and rename the new save the old file's name.
        # Also, add a failsafe to prevent overwriting NewGame.sav.
        pass


    def loadFile(self):
        file = txtLoad(['..', 'Data', 'Save', self.filename], 'r')
        loading = None
        for line in file:
            line = line.strip()
            print(line)
            if line.startswith('//'):
                self.comments.append(line)
            elif line.startswith('PLAYER_STATS'):
                loading = 'PLAYER_STATS'
            elif line.startswith('INVENTORY'):
                loading = 'INVENTORY'
            elif line.startswith('EQUIPPED'):
                loading = 'EQUIPPED'
            elif line.startswith('BUFFS'):
                loading = 'BUFFS'
            elif line.startswith('POSITION'):
                loading = 'POSITION'
            elif line.startswith('PER_LEVEL'):
                loading = 'PER_LEVEL'

            # Stats
            if loading == 'PLAYER_STATS':
                if line.startswith('PLAYER_STATS'):
                    pass
                elif line.startswith('END_PLAYER_STATS'):
                    loading = None
                else:
                    splitLine = line.split('|')
                    statCategory = splitLine[0]
                    statName = splitLine[1]
                    statLevel = int(splitLine[2])
                    self.playerStats[statCategory][statName] = statLevel

            # Inventory (unfinished)
            elif loading == 'INVENTORY':
                if line.startswith('INVENTORY'):
                    pass
                elif line.startswith('END_INVENTORY'):
                    loading = None

            # Equipped (unfinished)
            elif loading == 'EQUIPPED':
                if line.startswith('EQUIPPED'):
                    pass
                elif line.startswith('EQUIPPED'):
                    loading = None

            # Buffs (unfinished)
            elif loading == 'BUFFS':
                if line.startswith('BUFFS'):
                    pass
                elif line.startswith('END_BUFFS'):
                    loading = None

            # Per-level edits (unfinished)
            elif loading == 'PER_LEVEL':
                if line.startswith('PER_LEVEL'):
                    pass
                elif line.startswith('END_PER_LEVEL'):
                    loading = None

            # Position, level, and direction
            elif loading == 'POSITION':
                if line.startswith('POSITION'):
                    pass
                elif line.startswith('END_POSITION'):
                    loading = None
                else:
                    splitLine = line.split('|')
                    if line.startswith('level'):
                        self.currentLevel = splitLine[1]
                    elif line.startswith('coordX'):
                        self.playerCoord[0] = int(splitLine[1])
                    elif line.startswith('coordY'):
                        self.playerCoord[1] = int(splitLine[1])
                    elif line.startswith('coordZ'):
                        self.playerCoord[2] = int(splitLine[1])
                    elif line.startswith('directionX'):
                        self.playerDirection[0] = int(splitLine[1])
                    elif line.startswith('directionY'):
                        self.playerDirection[1] = int(splitLine[1])
                    elif line.startswith('directionZ'):
                        self.playerDirection[2] = int(splitLine[1])

                        
    def setFilename(self, newFilename):
        self.filename = newFilename

testSave = SaveGame('NewGame.sav')
testSave.loadFile()
