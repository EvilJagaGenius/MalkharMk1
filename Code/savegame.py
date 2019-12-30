# TIOM class for saved game data.

finished = False
print('Loading SaveGame class...')

import Main
from Main import *

# Insert class here
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

    def getLevelChanges(self, level):
        print('Calling getLevelChanges')
        # Call this every time you exit a level and every time you save your game
        self.currentLevel = level.name
        if level.name not in self.levelEdits:
            self.levelEdits.update({level.name:[]})
        self.levelEdits[level.name] = []
        comparisonLevel = loadLevel(level.name)

        # Objects
        for o in comparisonLevel.objects:
            if o not in level.objects:
                obj = o[0]
                # Add a note to remove that object
                self.levelEdits[level.name].append('removeObjectAt~' + str(obj.coord[0]) + '|' + str(obj.coord[1]) + '|' + str(obj.coord[2]))
        for o in level.objects:
            if o not in comparisonLevel.objects:
                # Add a note to add that object
                self.levelEdits[level.name].append('addObject~' + obj.getSaveString() + '~' + str(o[1]))

        # Entities
        for e in level.entities:
            if e != 'Player':
                if e not in comparisonLevel.entities:
                    ent = level.entities[e]
                    # Add a note to add the entity
                    # Where to move it, how long it's been there, etc, etc... have a getSaveString() function for entities.
                    # Really, I'm thinking this should only be called if someone uses a spell like Ice Clone or Earth Clone, or there's an enemy that spawns lots of little versions of itself.
                    # Basically, Entities that can be created in the level, but aren't loaded from their own files.
                    self.levelEdits[level.name].append('addEntity~' + ent.getSaveString())
                else:
                    ent = level.entities[e]
                    compEnt = comparisonLevel.entities[e]
                    if ent.coord != compEnt.coord:
                        # Add note to move entity
                        self.levelEdits[level.name].append('moveEntity~' + ent.name + '|' + str(ent.coord[0]) + '|' + str(ent.coord[1]) + '|' + str(ent.coord[2]))
                    if ent.direction != compEnt.direction:
                        # Add note to change entity direction
                        self.levelEdits[level.name].append('changeEntityDirection~' + ent.name + '|' + str(ent.direction[0]) + '|' + str(ent.direction[1]) + '|' + str(ent.direction[2]))
                    if ent.canTalk:
                        if ent.conversation != compEnt.conversation:
                            # Ooooh boy.  Write code to go through the conversation and record the changes.
                            # Theoretically we could just have the NPC record changes made to it as we make changes, then have it barf those changes back out to us...
                            for change in ent.conversationChanges:
                                self.levelEdits[level.name].append(change)
                    # Tack on stuff for combat when you get to it.

        for e in comparisonLevel.entities:
            if e not in level.entities:
                print(e + ' not in current level entities')
                self.levelEdits[level.name].append('removeEntity~' + e)

    def addLevelChange(self, levelName, change):
        print('Adding change to ' + levelName + ': ' + change)
        if levelName not in self.levelEdits:
            self.levelEdits.update({levelName:[]})
        self.levelEdits[levelName].append(change)


    def getPlayerChanges(self, player):
        # Call every time you save your game
        self.playerCoord = player.coord
        self.playerDirection = player.direction
        self.playerStats = player.stats
        self.playerBuffs = player.buffs
        self.playerEquipment = player.equipment
        self.inventory = player.inventory
        

    def writeToFile(self):
        print('Saving game...')
        # Notes to self: Don't try writing to the original save file directly.  Try writing a new save file.  If that is successful, delete the old save and rename the new save the old file's name.
        # Also, add a failsafe to prevent overwriting NewGame.sav.
        filename = self.filename
        if self.filename == 'NewGame.sav':
            filename = 'Continue.sav'
        file = txtLoad(['..', 'Data', 'Save', filename], 'w')
        
        # Comments
        for c in self.comments:
            file.write(c + '\n')
        file.write('\n')

        # Stats
        file.write('PLAYER_STATS\n')
        for category in self.playerStats:
            for stat in self.playerStats[category]:
                file.write(category + '|' + stat + '|' + str(self.playerStats[category][stat]) + '\n')
        file.write('END_PLAYER_STATS\n\n')

        # Inventory (unfinished)
        file.write('INVENTORY\n')
        # Insert loop to go through the inventory here
        for obj in self.playerInventory:
            file.write(obj.getSaveString() + '|' + str(self.playerInventory[obj]) + '\n')
        file.write('END_INVENTORY\n\n')

        # Equipment
        file.write('EQUIPPED\n')
        for e in self.playerEquipment:
            objString = 'X'
            if self.playerEquipment[e] != None:
                objString = self.playerEquipment[e].saveString
            file.write(e + '|' + objString + '\n')
        file.write('END_EQUIPPED\n\n')

        # Buffs (unfinished)
        file.write('BUFFS\n')
        # Insert code here
        file.write('END_BUFFS\n\n')

        # Position
        file.write('POSITION\n')
        file.write('level|' + self.currentLevel + '\n')
        file.write('coordX|' + str(self.playerCoord[0]) + '\n')
        file.write('coordY|' + str(self.playerCoord[1]) + '\n')
        file.write('coordZ|' + str(self.playerCoord[2]) + '\n')
        file.write('directionX|' + str(self.playerDirection[0]) + '\n')
        file.write('directionY|' + str(self.playerDirection[1]) + '\n')
        file.write('directionZ|' + str(self.playerDirection[2]) + '\n')
        file.write('END_POSITION\n\n')

        # Per-level edits (unfinished)
        file.write('PER_LEVEL\n')
        for level in self.levelEdits:
            for edit in self.levelEdits[level]:
                file.write(level + ':' + edit + '\n')
        file.write('END_PER_LEVEL\n\n')

        # Close file
        file.close()

        

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

            # Inventory
            elif loading == 'INVENTORY':
                if line.startswith('INVENTORY'):
                    pass
                elif line.startswith('END_INVENTORY'):
                    loading = None
                else:
                    (obj, amt) = createObject(line)
                    self.playerInventory.update({obj:amt})

            # Equipment
            elif loading == 'EQUIPPED':
                if line.startswith('EQUIPPED'):
                    pass
                elif line.startswith('END_EQUIPPED'):
                    loading = None
                else:
                    splitLine = line.split('|')
                    self.playerEquipment[splitLine[0]] = createObject(splitLine[1])

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
                else:
                    splitLine = line.split(':')
                    print(splitLine)
                    if splitLine[0] not in self.levelEdits:
                        self.levelEdits.update({splitLine[0]:[]})
                    self.levelEdits[splitLine[0]].append(splitLine[1])

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

        file.close()

                        
    def setFilename(self, newFilename):
        self.filename = newFilename


print('Done loading SaveGame class')
finished = True
