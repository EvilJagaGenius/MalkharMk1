# Block class.

finished = False
print("Loading Block class...")

import Main
from Main import *

class Block:
    def __init__(self, blockType, spriteLink=[0, 0, 0]):
        self.type = blockType
        self.spriteLink = spriteLink
        self.string = ''

        self.updateString()

    def updateString(self):
        self.string = self.type + '|' + str(self.spriteLink[0]) + '|' + str(self.spriteLink[1]) + '|' + str(self.spriteLink[2])

finished = True
print("Done loading Block class")
