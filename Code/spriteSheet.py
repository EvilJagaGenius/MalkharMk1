# SpriteSheet class.
finished = False
print ("Loading SpriteSheet class...")

import Main
from Main import *

class SpriteSheet:
    def __init__(self, sheet, spriteX, spriteY, colorkey=None):  # All sprites must have the same dimensions
        self.spriteX = spriteX
        self.spriteY = spriteY
        if sheet != None:
            self.sheet = imgLoad(['..', 'Data', 'Sprites', sheet]).convert() # Original reference image
        else:
            self.sheet = pygame.Surface((spriteX, spriteY))
            self.sheet.fill((0,0,0))
        
        self.filename = sheet
        if colorkey != None:
            self.sheet.set_colorkey(colorkey)


        # Generate a matrix of sprites
        self.matrix = []
        x = 0
        y = 0
        row = 0
        while y <= self.sheet.get_height() - self.spriteY:
            self.matrix.append([])
            while x <= self.sheet.get_width() - self.spriteX:
                spriteRect = pygame.rect.Rect(x, y, self.spriteX, self.spriteY)
                spriteImg = self.sheet.subsurface(spriteRect)
                self.matrix[row].append(spriteImg)
                
                x += self.spriteX
                
            x = 0
            y += self.spriteY
            row += 1


    def getSprite(self, coord): # x and y are the x and y positions of the sprite.  So, getSprite(3, 2) would return the third sprite in the second row of sprites.
        if coord[0] >= 0 and coord[1] >= 0:
            return self.matrix[coord[1]][coord[0]]

    def setColorkey(self, newColorkey):
        self.sheet.set_colorkey(newColorkey)

    def setColorkeyByCoord(self, coord):
        self.sheet.set_colorkey(self.sheet.get_at(coord))

finished = True
print("Done loading SpriteSheet class")
