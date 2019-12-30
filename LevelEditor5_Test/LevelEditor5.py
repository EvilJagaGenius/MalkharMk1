# TIOM level editor version 5.

import pygame, sys, os
from pygame import *
pygame.init()

WX = 832
WY = 640
window = pygame.display.set_mode((WX, WY), 0, 32)
pygame.display.set_caption('TIOM level editor')


def choiceBoxSurface(choices, selected):
    #choices=list, selected=int
    #Each choice will only take up one line.
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

    #All the text should be blitted, now to clean it up.
    eraser = pygame.Surface((WX-(maxX+4), y))
    eraser.fill((0,255,0))
    txtSurface.blit(eraser, (maxX+4, 0))
    txtSurface.set_colorkey((0,255,0))
    return txtSurface

def resize(matrix, newX, newY, newZ, origin=(0,0,0)): #Stuff in a 3D matrix, get out a resized 3D matrix.
    newMatrix = []
    for k in range(newZ):
        newMatrix.append([])
        for j in range(newY):
            newMatrix[k].append([])
            for i in range(newX):
                newMatrix[k][j].append(None)
    i = 0 #x
    j = 0 #y
    k = 0 #z
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
    file = txtLoad([level.folderName, level.fileName], 'w')

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
        e.writeTxtFile()
        file.write(e.fileName + '\n')
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
    file = txtLoad([folderName, folderName+'.mld'], 'r')
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
        self.entities = [] # Special, named things
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


    def setBkg(self, bkgFile, layer):
        if layer >= 0 and layer < self.levelZ:
            self.bkgFiles[layer] = bkgFile
            if bkgFile != None:
                self.bkgs[layer] = imgLoad([self.folderName, 'bkgs', bkgFile])
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
        failed = False
        for e in self.entities:
            if e.name == newEnt.name:
                failed = True
                
        if not failed:
            self.entities.append(newEnt)

    def addObject(self, newObj):
        self.objects.append(newObj)


    def getViewSurf(self, coord):

        noBkg = False

        coord = list(coord)
        lockX = False
        lockY = False

        bkgDimensions = [0, 0]
        bkgTopLeft = [0, 0]

        startCoord = [0, 0]
        endCoord = [13, 10]

        if self.levelX < 13:
            startCoord[0] = 0
            endCoord[0] = self.levelX
            lockX = True
        if self.levelY < 10:
            startCoord[1] = 0
            endCoord[1] = self.levelY
            lockY = True

        if not lockX:
            if coord[0] - 6 >= 0:
                if coord[0] + 7 <= self.levelX:
                    startCoord[0] = coord[0] - 6
                    endCoord[0] = coord[0] + 7
                else:
                    startCoord[0] = self.levelX - 13
                    endCoord[0] = self.levelX
            else:
                startCoord[0] = 0
                endCoord[0] = 13

            bkgTopLeft[0] = startCoord[0] * 64

        if not lockY:
            if coord[1] - 5 >= 0:
                if coord[1] + 5 <= self.levelY:
                    startCoord[1] = coord[1] - 5
                    endCoord[1] = coord[1] + 5
                else:
                    startCoord[1] = self.levelY - 10
                    endCoord[1] = self.levelY
            else:
                startCoord[1] = 0
                endCoord[1] = 10

            bkgTopLeft[1] = startCoord[1] * 64

        bkgDimensions[0] = (endCoord[0] - startCoord[0]) * 64
        bkgDimensions[1] = (endCoord[1] - startCoord[1]) * 64

        viewSurf = pygame.surface.Surface(bkgDimensions)

        for z in range(0, coord[2]+1):
            
            blitX = 0
            blitY = 0
            
            lvlSurf = pygame.surface.Surface(bkgDimensions)
            if self.bkgs[z] != None:
                lvlSurf.blit(self.bkgs[z].subsurface(pygame.rect.Rect(bkgTopLeft[0], bkgTopLeft[1], bkgDimensions[0], bkgDimensions[1])), (0,0))
            else:
                lvlSurf.fill((0,0,0))
                lvlSurf.set_colorkey((0,0,0))
                lvlSurf.set_alpha(50)
                noBkg = True
                
            for y in range(startCoord[1], endCoord[1]):
                for x in range(startCoord[0], endCoord[0]):
                    block = self.blockmap[z][y][x]

                    if (x, y) == (coord[0], coord[1]):
                        pygame.draw.rect(lvlSurf, (0, 255, 0), pygame.rect.Rect(blitX, blitY, 64, 64), 1)

                    for e in self.entities:
                        if e.coord[0] == x and e.coord[1] == y and e.coord[2] == z:
                            pygame.draw.rect(lvlSurf, (255, 255, 0), pygame.rect.Rect(blitX + 16, blitY + 16, 32, 32))
                            lvlSurf.blit(M_TXTFONT.render(e.name, True, (0, 0, 0)), (blitX, blitY))
                            lvlSurf.blit(M_TXTFONT.render(e.type, True, (0, 0, 0)), (blitX, blitY + 16))

                    lvlSurf.blit(self.tilesets[block.spriteLink[0]].getSprite((block.spriteLink[1], block.spriteLink[2])), (blitX, blitY))

                    if z == coord[2] and self.tints and block.type != 'Empty':
                        tintSurf = pygame.surface.Surface((64, 64))
                        if block.type == 'Tile':
                            tintSurf.fill((0,0,255))
                        elif block.type == 'Block':
                            tintSurf.fill((255,255,0))

                        if not noBkg:
                            tintSurf.set_alpha(50)
                        
                        lvlSurf.blit(tintSurf, (blitX, blitY))

                    blitX += 64
 
                blitX = 0
                blitY += 64

            viewSurf.blit(lvlSurf, (0,0))


        return viewSurf
                    
                    



    def edit(self):
        while True:
            tPress = False
            oPress = False
            ePress = False
            dPress = False
            bPress = False
            iPress = False
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
                    saveFile(self)
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
            self.sheet = imgLoad(['SpriteSheets', sheet]).convert() #Original reference image
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



    def readTxtFile(self):
        self.fileContents = []
        
        txtFile = txtLoad([self.level, 'entities', self.fileName], 'r')
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


    def writeTxtFile(self):
        txtFile = txtLoad([self.level, 'entities', self.fileName], 'w')
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






TXTFONT = pygame.font.Font(None, 24)
M_TXTFONT = pygame.font.Font(None, 16)

testLevel = loadLevel('testLevel')
testLevel.edit()

