# TIOM level editor version 5.

import pygame, sys, os
from pygame import *
pygame.init()

WX = 832
WY = 640
window = pygame.display.set_mode((WX, WY), 0, 32)
pygame.display.set_caption('TIOM level editor')


def choiceBoxSurface(choices, selected):
    # choices=list, selected=int
    # Each choice will only take up one line.
    maxX = 0
    txtSurface = pygame.Surface((WX, (TXTFONT.get_height()+4)*len(choices)))
    y = 0
    txtSurface.fill((100,100,100))
    for c in choices:
        txt = c
        color = (255,255,255) #Normally white
        if c == choices[selected]:
            color = (0,0,255) #Highlighted blue
        txtSurface.blit(TXTFONT.render(txt, True, color), (0, y))
        y += TXTFONT.get_height()+4
        if TXTFONT.size(txt)[0] > maxX:
            maxX = TXTFONT.size(txt)[0]

    # All the text should be blitted, now to clean it up.
    eraser = pygame.Surface((WX-(maxX+4), y))
    eraser.fill((0,255,0))
    txtSurface.blit(eraser, (maxX+4, 0))
    txtSurface.set_colorkey((0,255,0))
    return txtSurface

def resize(matrix, newX, newY, newZ, origin=(0,0,0)): # Stuff in a 3D matrix, get out a resized 3D matrix.
    newMatrix = []
    for k in range(newZ):
        newMatrix.append([])
        for j in range(newY):
            newMatrix[k].append([])
            for i in range(newX):
                newMatrix[k][j].append(None)
    i = 0 # x
    j = 0 # y
    k = 0 # z
    while k < newZ and k + origin[2] < len(matrix):
        while j < newY and j + origin[1] < len(matrix):
            while i < newX and i + origin[0] < len(matrix):
                newMatrix[k][j][i] = matrix[k + origin[2]][j + origin[1]][i + origin[0]]
                i += 1
            j += 1
            i = 0
        k += 1
        j = 0
        i = 0
        

    return newMatrix


def matrix_getAt(matrix, coord): # An (x,y,z) coord
    return matrix[coord[2]][coord[1]][coord[0]]

def matrix_setAt(matrix, coord, thing):
    matrix[coord[2]][coord[1]][coord[0]] = thing


def imgLoad(pathList): # pathList is a list of files/folders ending in the filename you want.
    filePath = os.path.join(*pathList)
    returnFile = pygame.image.load(filePath)
    return returnFile

def txtLoad(pathList, mode):
    filePath = os.path.join(*pathList)
    if not os.path.exists(filePath):
        file = open(filePath, 'w')
        file.close()
    file = open(filePath, mode)
    return file

def saveFile(level):
    folderPath = os.path.join('..', 'Data', 'Rooms', level.folderName)
    bkgPath = os.path.join('..', 'Data', 'Rooms', level.folderName, 'bkgs')
    entPath = os.path.join('..', 'Data', 'Rooms', level.folderName, 'entities')
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
        os.makedirs(bkgPath)
        os.makedirs(entPath)
        
    file = txtLoad(['..', 'Data', 'Rooms', level.folderName, level.fileName], 'w')

    file.write('NAME=' + level.name + '\n')

    file.write('DIMENSIONS\n')
    file.write('levelX=' + str(level.levelX) + '\n')
    file.write('levelY=' + str(level.levelY) + '\n')
    file.write('levelZ=' + str(level.levelZ) + '\n')
    file.write('END_DIMENSIONS\n')
    
    # Saving the backgrounds
    file.write('BKGS\n')
    for b in level.bkgFiles:
        if b == None:
            file.write('X\n')
        else:
            file.write(str(b) + '\n')
    file.write('END_BKGS\n')

    # Saving the tilesets
    file.write('TILESETS=' + str(len(level.tilesets)) + '\n')
    for t in level.tilesetFiles:
        file.write(t + '\n')
    file.write('END_TILESETS\n')

    # Saving the blockmap
    file.write('BLOCKMAP\n')
    for k in range(level.levelZ):
        for j in range(level.levelY):
            for i in range(level.levelX):
                block = matrix_getAt(level.blockmap, (i,j,k))
                file.write(block.string)
                file.write(',')
            file.write('\n')

        file.write('NEXTLAYER\n')
    file.write('END_BLOCKMAP\n')


    #Saving the entities:
    file.write('ENTITIES=' + str(len(level.entities)) + '\n')
    for e in level.entities:
        ent = level.entities[e]
        ent.writeTxtFile()
        file.write(ent.fileName + '\n')
    file.write('END_ENTITIES\n')

    #Saving the objects:
    file.write('OBJECTS\n')
    for o in level.objects:
        file.write(o.string + '\n')
    file.write('END_OBJECTS\n')

    #Saving the mode
    file.write('MODE=' + str(level.mode) + '\n')

    file.close()
        

def loadLevel(folderName):
    file = txtLoad(['..', 'Data', 'Rooms', folderName, folderName+'.mld'], 'r')
    loading = None
    level = None
    counter = 0
    layer = 0
    row = 0
    
    for line in file:
        line = line.strip()

        # Get the name
        if line.startswith('NAME='):
            name = line.strip('NAME=')

        # Get the dimensions
        if line.startswith('DIMENSIONS'):
            loading = 'DIMENSIONS'
            pass
        
        if (loading == 'DIMENSIONS'):
            if line.startswith('END_DIMENSIONS'):
                loading = None
                level = Level(levelX, levelY, levelZ, name)
                pass
            elif line.startswith('levelX='):
                levelX = int(line.strip('levelX='))
            elif line.startswith('levelY='):
                levelY = int(line.strip('levelY='))
            elif line.startswith('levelZ='):
                levelZ = int(line.strip('levelZ='))

        # Get the background images
        if line.startswith('BKGS'):
            loading = 'BKGS'
            counter = 0
            pass

        if (loading == 'BKGS'):
            if line.startswith('END_BKGS'):
                loading = None
                pass
            elif line.startswith('BKGS'):
                pass
            elif (line == 'X'):
                level.setBkg(None, counter)
                counter += 1
            else:
                level.setBkg(line, counter)
                counter += 1
                

        # Get the tilesets
        if line.startswith('TILESETS='):
            loading = 'TILESETS'
            pass
        
        if loading == 'TILESETS':
            if line.startswith('END_TILESETS'):
                loading = None
                pass
            elif line.startswith('TILESETS'):
                pass
            else:
                level.addTileset(line)

        # Get the blockmap
        if line.startswith('BLOCKMAP'):
            loading = 'BLOCKMAP'
            layer = 0
            pass

        if loading == 'BLOCKMAP':
            if line.startswith('END_BLOCKMAP'):
                loading = None
                pass
            elif line.startswith('BLOCKMAP'):
                pass
            elif line.startswith('NEXTLAYER'):
                layer += 1
                pass
            else:
                rowOfBlocks = line.split(',')
                for x in range(levelX):
                    blockData = rowOfBlocks[x].split('|')
                    block = Block(blockData[0], (int(blockData[1]), int(blockData[2]), int(blockData[3])))
                    level.setBlockAt((x, row, layer), block)
                row += 1

        # Get the entities
        if line.startswith('ENTITIES'):
            loading = 'ENTITIES'
            pass

        if loading == 'ENTITIES':
            if line.startswith('END_ENTITIES'):
                loading = None
                pass
            elif line.startswith('ENTITIES'):
                pass
            else:
                newEnt = Entity(folderName)
                newEnt.fileName = line
                newEnt.readTxtFile()
                level.addEntity(newEnt)
                

        # Get the mode
        if line.startswith('MODE='):
            level.setMode(int(line.strip('MODE=')))

        


    file.close()
    return level


def generateEntSprite(entity):
    sprite = pygame.surface.Surface((64, 64))
    sprite.set_colorkey((0, 0, 0, 0))
    pygame.draw.rect(sprite, (255, 255, 0), pygame.Rect(16, 16, 16, 16))
    sprite.blit(M_TXTFONT.render(entity.name, False, (0, 0, 255)), (0, 0))
    sprite.blit(M_TXTFONT.render(entity.type, False, (0, 0, 255)), (0, M_TXTFONT.get_height()))
    sprite.blit(M_TXTFONT.render(str(entity.coord), False, (0, 0, 255)), (0, M_TXTFONT.get_height()*2))

    return sprite





class Level: #a.k.a the room.
    def __init__(self, x, y, z, name, mode=0):

        self.name = name
        self.folderName = name
        self.fileName = name + '.mld'
        
        self.levelX = x
        self.levelY = y
        self.levelZ = z

        self.tilesetFiles = ['blankSheet.png']
        self.tilesets = [SpriteSheet('blankSheet.png', 64, 64, (0,0,0))]

        self.bkgFiles = [None] * self.levelZ
        self.bkgs = [None] * self.levelZ
        
        self.blockmap = [] # Blocks, Empties and Tiles
        self.entities = {} # Special, named things
        self.objects = []  # Common, unnamed things
        
        for a in range(z):
            self.blockmap.append([])
            for b in range(y):
                self.blockmap[a].append([])
                for c in range(x):
                    self.blockmap[a][b].append(Block('Empty'))

        self.mode = mode

        self.tints = False
        self.cursorCoord = [0,0,0]
        self.setBlock = 'Tile'

        self.blitOrder = []


    def getBlitOrder(self):
        # So.  We need to determine what order we're blitting entities in.  So that the player isn't standing on top of an NPC's head or something.
        # Lower y-coords go first, higher goes last.
        self.blitOrder = []
        for i in range(self.levelZ):
            self.blitOrder.append([])
        for e in self.entities:
            ent = self.entities[e]
            layer = self.blitOrder[ent.coord[2]]
            if len(layer) == 0:
                layer.append(e)
            else:
                for i in range(len(layer)):
                    if ent.coord[1] <= self.entities[layer[i]].coord[1]:
                        layer.insert(i, e)
                        break
                    elif i == len(layer) - 1 and ent.coord[1] > self.entities[layer[i]].coord[1]:
                        layer.append(e)
                        break

    def setBkg(self, bkgFile, layer):
        if layer >= 0 and layer < self.levelZ:
            self.bkgFiles[layer] = bkgFile
            if bkgFile != None:
                self.bkgs[layer] = imgLoad(['..', 'Data', 'Rooms', self.folderName, 'bkgs', bkgFile])
            else:
                self.bkgs[layer] = None

    def setMode(self, newMode):
        self.mode = newMode

    def addTileset(self, newTilesetFile):
        if newTilesetFile not in self.tilesetFiles:
            self.tilesetsFile.append(newTilesetFile)
            self.tilesets.append(SpriteSheet(newTilesetFile, 64, 64))

    def changeBlock(self):
        choice = input('''
1. Empty
2. Tile
3. Block
''')
        if choice == '1':
            print('Switching to Empty')
            self.setBlock = "Empty"
        elif choice == '2':
            print('Switching to Tile')
            self.setBlock = "Tile"
        elif choice == '3':
            print('Switching to Block')
            self.setBlock = "Block"
        else:
            print('Switch failed, please try again')

    def setBlockAt(self, coord, newBlock):
        if (coord[2] >= 0 and coord[2] < self.levelZ) and (coord[1] >= 0 and coord[1] < self.levelY) and (coord[0] >= 0 and coord[0] < self.levelX):
            self.blockmap[coord[2]][coord[1]][coord[0]] = newBlock

    def addEntity(self, newEnt):
        if newEnt.name not in self.entities:
            self.entities.update({newEnt.name:newEnt})


            
    def addObject(self, newObj):
        self.objects.append(newObj)


    # Replace this version of getViewSurf with the level.py version
    # Then add stuff for entities and tints and stuff
    def getViewSurf(self, focusCoord, offset=[0,0]):
        self.getBlitOrder()
        
        offset = list(offset)
        focusCoord = list(focusCoord)

        # Adjust offset and focusCoord
        while offset[0] >= TILE_SIZE:
            offset[0] -= TILE_SIZE
            focusCoord[0] += 1
        while offset[0] <= -TILE_SIZE:
            offset[0] += TILE_SIZE
            focusCoord[0] -= 1
        while offset[1] >= TILE_SIZE:
            offset[1] -= TILE_SIZE
            focusCoord[1] += 1
        while offset[1] <= -TILE_SIZE:
            offset[1] += TILE_SIZE
            focusCoord[1] -= 1
    
        viewSurf = pygame.Surface((VIEWSURF_PLUS_BUFFER, VIEWSURF_PLUS_BUFFER))
        
        verticalDifference = 0 - focusCoord[2]
        # Each layer is supposed to appear 32 pixels (y-axis) different from the previous one.
        # The player is always supposed to be smack in the exact center of the screen, the layer below will start 32 pixels below them, and the layer above will start 32 pixels above them.

        for z in range(self.levelZ): # For each layer
            
            layerSurf = pygame.surface.Surface((VIEWSURF_PLUS_BUFFER, VIEWSURF_PLUS_BUFFER), SRCALPHA) # Get a blank surface to blit onto
            layerSurf.fill((255, 0, 255, 0)) # Fill with magenta
            layerSurf.set_colorkey((255, 0, 255)) # Turn magenta invisible
            
            startCoord = [focusCoord[0] - 12, (focusCoord[1] - 12) + verticalDifference]
            endCoord = [focusCoord[0] + 14, (focusCoord[1] + 14) + verticalDifference]

            tileRect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

            blitRect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE) # The rect to blit stuff onto the viewing screen.

            layerBkg = self.bkgs[z] # Get the bkg image for that layer
            cuttingRect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE) # The rect that cuts pieces out of the layer bkg.
            
            

            # Blit the background/tiles
            for y in range(startCoord[1], endCoord[1]):
                for x in range(startCoord[0], endCoord[0]):
                    # Check to see if the coord's on-screen
                    if x >= 0 and x < self.levelX and y >= 0 and y < self.levelY:

                        # Get the position we're going to blit to
                        blitRect.top = (y - startCoord[1]) * TILE_SIZE
                        blitRect.left = (x - startCoord[0]) * TILE_SIZE

                        # Do stuff with the bkg
                        if layerBkg != None:
                            # Adjust cuttingRect
                            cuttingRect.top = y * TILE_SIZE
                            cuttingRect.left = x * TILE_SIZE
                            # Blit that chunk of bkg
                            layerSurf.blit(layerBkg, blitRect, cuttingRect)
                            
                        
                        # Blit the block's sprite at that position
                        block = self.blockmap[z][y][x]
                        if block.spriteLink[0] != 0: # If it's not a link to the blank sheet
                            tileSheet = self.tilesets[block.spriteLink[0]].sheet
                            tileRect.top = block.spriteLink[2] * TILE_SIZE
                            tileRect.left = block.spriteLink[1] * TILE_SIZE
                            layerSurf.blit(tileSheet, blitRect, tileRect)
                        if self.tints and z == focusCoord[2]:
                            if block.type == 'Block':
                                # Draw yellow
                                tintSurf = pygame.surface.Surface((32, 32))
                                tintSurf.fill((255,255,0))
                                tintSurf.set_alpha(127)
                                layerSurf.blit(tintSurf, blitRect)
                            elif block.type == 'Tile':
                                # Draw blue
                                tintSurf = pygame.surface.Surface((32, 32))
                                tintSurf.fill((0,0,255))
                                tintSurf.set_alpha(127)
                                layerSurf.blit(tintSurf, blitRect)

                        if [x, y, z] == focusCoord:
                            pygame.draw.rect(layerSurf, (0, 255, 0), blitRect, 1)



                
            for e in self.blitOrder[z]:
                ent = self.entities[e]
                
                entSprite = ent.sprite
                
                entBlitRect = pygame.Rect((ent.coord[0] - startCoord[0]) * TILE_SIZE, (ent.coord[1] - startCoord[1]) * TILE_SIZE, 32, 32) # Fill this in later
                
                layerSurf.blit(entSprite, entBlitRect)
                        
                        
            viewSurf.blit(layerSurf, (0, 0))
            verticalDifference += 1

            

        croppingRect = pygame.Rect(TILE_SIZE, TILE_SIZE, VIEWPORT_SIZE, VIEWPORT_SIZE)
        croppingRect.top += offset[1]
        croppingRect.left += offset[0]
        croppedViewSurf = viewSurf.subsurface(croppingRect)
    
        return croppedViewSurf
                    
                    



    def edit(self):
        while True:
            tPress = False
            oPress = False
            ePress = False
            dPress = False
            bPress = False
            iPress = False
            vPress = False
            upPress = False
            downPress = False
            leftPress = False
            rightPress = False
            plusPress = False
            minusPress = False
            escPress = False

            layer = self.cursorCoord[2]
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    saveFile(self)  # Comment this out when testing.  Don't want to corrupt a perfectly good level.
                    pygame.quit()
                    sys.exit()
                if event.type == KEYUP:
                    if event.key == ord('t'):
                        tPress = True
                    if event.key == ord('o'):
                        oPress = True
                    if event.key == ord('e'):
                        ePress = True
                    if event.key == ord('d'):
                        dPress = True
                    if event.key == ord('b'):
                        bPress = True
                    if event.key == ord('v'):
                        vPress = True
                    if event.key == ord('i'):
                        iPress = True
                    if event.key == ord('='):
                        plusPress = True
                    if event.key == ord('-'):
                        minusPress = True
                    
                    if event.key == K_UP:
                        upPress = True
                    if event.key == K_DOWN:
                        downPress = True
                    if event.key == K_LEFT:
                        leftPress = True
                    if event.key == K_RIGHT:
                        rightPress = True
                    if event.key == K_ESCAPE:
                        escPress = True

            if tPress:
                self.tints = not self.tints

            if bPress:
                self.setBlockAt(self.cursorCoord, Block(self.setBlock))

            if vPress:
                self.changeBlock()

            if iPress:
                bkgFilename = input("What bkg to add to layer " + str(self.cursorCoord[2]) + "? (Enter X to cancel)  ")
                if bkgFilename != 'X':
                    self.setBkg(bkgFilename, self.cursorCoord[2])

            if ePress:
                entName = input("New entity's name: ")
                entType = input("New entity's type: ")
                newEnt = Entity(self.name, self.cursorCoord.copy(), entType, entName)
                self.addEntity(newEnt)
                print()

            if upPress and self.cursorCoord[1] > 0:
                self.cursorCoord[1] -= 1
            if downPress and self.cursorCoord[1] < self.levelY - 1:
                self.cursorCoord[1] += 1
            if leftPress and self.cursorCoord[0] > 0:
                self.cursorCoord[0] -= 1
            if rightPress and self.cursorCoord[0] < self.levelX - 1:
                self.cursorCoord[0] += 1
            if plusPress and self.cursorCoord[2] < self.levelZ - 1:
                self.cursorCoord[2] += 1
            if minusPress and self.cursorCoord[2] > 0:
                self.cursorCoord[2] -= 1

                
            
            window.fill((0,0,0))
            viewSurf = self.getViewSurf(self.cursorCoord)
            viewSurf.blit(TXTFONT.render('Cursor Coord = ' + str(self.cursorCoord), True, (0,0,255)), (0,0))

            window.blit(viewSurf, (0,0))


            pygame.display.update()


    
            
    
    
class SpriteSheet: #CLONE!
    def __init__(self, sheet, spriteX, spriteY, colorkey=None, name='Unknown'):  #All sprites must have the same dimensions
        self.spriteX = spriteX
        self.spriteY = spriteY
        if sheet != None:
            self.sheet = imgLoad(['..', 'Data', 'Sprites', sheet]).convert() #Original reference image
        else:
            self.sheet = pygame.surface.Surface((spriteX, spriteY))
            self.sheet.fill((0,0,0))
        self.name = name
        self.filename = sheet
        if colorkey != None:
            self.sheet.set_colorkey(colorkey)


        #Generate a matrix of sprites
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
                


    def getSprite(self, coord): #x and y are the x and y positions of the sprite.  So, getSprite(3, 2) would return the third sprite in the second row of sprites.
        if coord[0] >= 0 and coord[1] >= 0:
            return self.matrix[coord[1]-1][coord[0]-1]
            
    def getSprite_GUI(self, level=None): #getSprite() refined.
        cursorCoord = [0, 0]
        while True:
            enterPress = False
            rightPress = False
            leftPress = False
            upPress = False
            downPress = False
            escPress = False
            
            
            window.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    if level != None:
                        saveFile(level)
                    pygame.quit()
                    sys.exit()

                if event.type == KEYUP:
                    if event.key == K_RETURN:
                        enterPress = True
                    if event.key == K_UP:
                        upPress = True
                    if event.key == K_DOWN:
                        downPress = True
                    if event.key == K_LEFT:
                        leftPress = True
                    if event.key == K_RIGHT:
                        rightPress = True
                    if event.key == K_ESCAPE:
                        escPress = True

            if leftPress and cursorCoord[0] > 0:
                cursorCoord[0] -= 1
            if rightPress and cursorCoord[0] < int(self.sheet.get_width() / self.spriteX):
                cursorCoord[0] += 1
            if upPress and cursorCoord[1] > 0:
                cursorCoord[1] -= 1
            if downPress and cursorCoord[1] < int(self.sheet.get_height() / self.spriteY):
                cursorCoord[1] += 1

            if enterPress:
                return [self.name, cursorCoord[0] + 1, cursorCoord[1] + 1]

            if escPress:
                return None

            window.blit(self.sheet, (0,0))
            pygame.draw.rect(window, (0,255,0), pygame.Rect(cursorCoord[0] * self.spriteX, cursorCoord[1] * self.spriteY, self.spriteX, self.spriteY), 1)
            
            pygame.display.update()



class Block:
    def __init__(self, blockType, spriteLink=[0, 0, 0]):
        self.type = blockType
        self.spriteLink = spriteLink
        self.string = ''

        self.updateString()

    def updateString(self):
        self.string = self.type + '|' + str(self.spriteLink[0]) + '|' + str(self.spriteLink[1]) + '|' + str(self.spriteLink[2])

class Entity:
    def __init__(self, level, coord=[0,0,0], eType='Entity', name='Unknown'):
        self.level = level
        self.name = name
        self.coord = coord
        self.type = eType

        self.fileName = name + '.ent'
        self.fileContents = []

        self.sprite = generateEntSprite(self)



    def readTxtFile(self):
        self.fileContents = []
        
        txtFile = txtLoad(['..', 'Data', 'Rooms', self.level, 'entities', self.fileName], 'r')
        for line in txtFile:
            self.fileContents.append(line)
            line = line.strip()
            
            if line.startswith('name'):
                splitLine = line.split('~')
                self.name = splitLine[1]
            elif line.startswith('coord'):
                splitLine = line.split('~')
                self.coord = eval(splitLine[1])
            elif line.startswith('type'):
                splitLine = line.split('~')
                self.type = splitLine[1]

        txtFile.close()
        self.sprite = generateEntSprite(self)


    def writeTxtFile(self):
        txtFile = txtLoad(['..', 'Data', 'Rooms', self.level, 'entities', self.fileName], 'w')
        if self.fileContents != []:
            for line in self.fileContents:

                # These lines will update the entity's name, coord, and type in the .ent file.
                # If it was an empty file before, fileContents will be blank.
                if line.strip().startswith('name~'):
                    txtFile.write('name~'+self.name+' \n')
                elif line.strip().startswith('coord~'):
                    txtFile.write('coord~'+str(self.coord)+' \n')
                elif line.strip().startswith('type~'):
                    txtFile.write('type~'+self.type+' \n')
                else:
                    txtFile.write(line)

        else:

            txtFile.write('name~'+self.name+' \n')
            txtFile.write('coord~'+str(self.coord)+' \n')
            txtFile.write('type~'+self.type+' \n')

        txtFile.close()





# Symbolic constants and the like
TXTFONT = pygame.font.Font(None, 24)
M_TXTFONT = pygame.font.Font(None, 16)

TILE_SIZE = 32
VIEWPORT_SIZE = 768
VIEWSURF_PLUS_BUFFER = VIEWPORT_SIZE + (TILE_SIZE * 2)



print('''
Options:
1) New level
2) Edit existing level
''')
choice = input('Your choice:  ')
if choice == '1':
    levelX = int(input('X:  '))
    levelY = int(input('Y:  '))
    levelZ = int(input('Z:  '))
    name = input('Level name:  ')
    level = Level(levelX, levelY, levelZ, name)
elif choice == '2':
    levelName = input('Level name:  ')
    level = loadLevel(levelName)


level.edit()

