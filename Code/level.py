finished = False
print("Loading Level class...")

import Main
from Main import *

AIM_SHEET = SpriteSheet('AimSheetSTNI.png', 32, 32, (0, 0, 0))  # I do intend to make my own sprite sheet for this, but the S:TNI sprites make awesome placeholders.

class Level:  # Note: Levels are stored in the "Data/Rooms" folder.
    def __init__(self, x, y, z, name, mode=0):
        # NTS: move most of this to the play() function, so that we don't load this until absolutely necessary

        self.save = None

        self.name = name
        self.folderName = name
        self.fileName = name + '.mld'
        
        self.levelX = x
        self.levelY = y
        self.levelZ = z

        self.tilesetFiles = ['BlankSheet.png']
        self.tilesets = [SpriteSheet('BlankSheet.png', 64, 64, (0,0,0))]

        self.bkgFiles = [None] * self.levelZ
        self.bkgs = [None] * self.levelZ
        
        self.blockmap = [] # Blocks, Empties and Tiles
        self.entities = {} # Special, named things
        self.objects = [] # Common, unnamed things
                
        for a in range(z):
            self.blockmap.append([])
            for b in range(y):
                self.blockmap[a].append([])
                for c in range(x):
                    self.blockmap[a][b].append(Block('Empty'))

        self.mode = mode

        # Variables used when playing the level
        self.currentInput = []
        self.lastInput = []
        self.thingInControl = None
        self.cursorCoord = [0, 0, 0]
        self.aiming = False
        self.actionToPerform = None
        self.targets = []
        self.currentTarget = 0
        self.blitOrder = [[]] * self.levelZ
        self.dialogBoxes = []
        self.conversation = None

        self.viewScreenRect = pygame.rect.Rect(0, 0, 768, 768)

        # Animation stuff
        self.animCommands = {}
        self.animating = False
        self.pauseForAnimation = False
        self.animFrameCounter = 0

        self.gfx = []

    def loadFromSave(self, savegame):
        print('Loading from save')
        if self.name in savegame.levelEdits:
            # Load stuff
            for edit in savegame.levelEdits[self.name]:
                command = edit.split('~')
                if command[0] == 'removeObjectAt':
                    print('Reading removeObjectAt command')
                    splitText = command[1].split('|')
                    self.removeObjsAtCoord((int(splitText[0]), int(splitText[1]), int(splitText[2])))
                elif command[0] == 'addObjectAt':
                    obj = createObject(command[1])
                    amt = int(command[2])
                    self.addObject(obj, amt)
                elif command[0] == 'removeEntity':
                    print('Removing entity: ' + command[1])
                    self.removeEntity(command[1])

                # Add more commands as you get to them
                    
                
        
    def setBkg(self, bkgFile, layer):
        if layer >= 0 and layer < self.levelZ:
            self.bkgFiles[layer] = bkgFile
            if bkgFile != None:
                self.bkgs[layer] = imgLoad(['..', 'Data', 'Rooms', self.folderName, 'bkgs', bkgFile]).convert()
            else:
                self.bkgs[layer] = None

    def setMode(self, newMode):
        self.mode = newMode

    def setBlockAt(self, coord, newBlock):
        if (coord[2] >= 0 and coord[2] < self.levelZ) and (coord[1] >= 0 and coord[1] < self.levelY) and (coord[0] >= 0 and coord[0] < self.levelX):
            self.blockmap[coord[2]][coord[1]][coord[0]] = newBlock

    def getBlockAt(self, coord):
        return self.blockmap[coord[2]][coord[1]][coord[0]]

    def addTileset(self, newTilesetFile):
        if newTilesetFile not in self.tilesetFiles:
            self.tilesetFiles.append(newTilesetFile)
            self.tilesets.append(SpriteSheet(newTilesetFile, 64, 64))

    def addEntity(self, newEnt):
        for e in self.entities:
            if e == newEnt.name:
                print("Failure to add entity")
                return False
        self.entities.update({newEnt.name:newEnt})

    def removeEntity(self, entToRemove):
        if entToRemove in self.entities:
            self.entities.pop(entToRemove)

    def changeAnimation(self, entity, newAnimation):
        self.entities[entity].changeAnim(newAnimation)

    def getEntsAtCoord(self, coord):
        entsAtCoord = []
        for e in self.entities:
            ent = self.entities[e]
            if tuple(ent.coord) == tuple(coord):
                entsAtCoord.append(e)

        return entsAtCoord

    def addObject(self, obj, amt=1):
        self.objects.append((obj, amt))

    def getObjsAtCoord(self, coord):
        objs = []
        for o in self.objects:
            obj = o[0]
            if tuple(obj.coord) == tuple(coord):
                objs.append(o)
        return objs

    def removeObjsAtCoord(self, coord):
        for o in self.objects:
            obj = o[0]
            if tuple(obj.coord) == tuple(coord):
                self.objects.remove(o)


    def setConversation(self, conversation):
        self.conversation = conversation
        self.conversation.paused = False
        self.conversation.checkForFlags()

    def endConversation(self):
        print('Ending conversation')
        self.conversation.topic = self.conversation.startTopic
        self.conversation.part = self.conversation.startPart
        self.conversation.paused = True
        self.conversation = None

    def removeDialogBox(self, dialogBox):
        if dialogBox in self.dialogBoxes:
            self.dialogBoxes.remove(dialogBox)
        self.flushInput()

    def addDialogBox(self, dialogBox):
        self.dialogBoxes.append(dialogBox)
        self.flushInput()

    def addGFX(self, gfx):
        self.gfx.append(gfx)

    def removeGFX(self, gfx):
        self.gfx.remove(gfx)

    def moveToCoord(self, thing, coord): # Call moveToCoord on an entity or object
        thing.moveToCoord(coord)

    def moveByDelta(self, thing, coord): # Call moveByDelta on an entity or object
        thing.moveByDelta(coord)

    def flushInput(self): # Clear self.currentInput and self.lastInput
        self.currentInput = []
        self.lastInput = []

    def resetAnimation(self):
        self.animCommands = {}
        self.animating = False
        self.pauseForAnimation = False
        self.animFrameCounter = 0

        for e in self.entities:
            ent = self.entities[e]
            ent.resetAnimation()

    def checkIfClear(self, thing, destCoord): # See if an object or entity can fit at a destination coord
        delta = (destCoord[0] - thing.coord[0], destCoord[1] - thing.coord[1], destCoord[2] - thing.coord[2])
        destBody = thing.getBody()
        for i in destBody:
            i[0] += delta[0]
            i[1] += delta[1]
            i[2] += delta[2]
            if self.getBlockAt(i).type == "Block":
                return False
        for i in self.entities:
            ent = self.entities[i]
            if ent.solid:
                if bodiesCollide(destBody, ent.body):
                    return False
        return True

    def checkIfClearByDelta(self, thing, delta): # See if an object or entity can fit at a destination coord
        destBody = thing.getBody()
        for i in destBody:
            i[0] += delta[0]
            i[1] += delta[1]
            i[2] += delta[2]
            if self.getBlockAt(i).type == "Block":
                return False
        for i in self.entities:
            ent = self.entities[i]
            if ent.solid:
                if bodiesCollide(destBody, ent.body):
                    return False
        return True

    def addAnimCommand(self, frameNum, newAnimCommand):
        if frameNum in self.animCommands:
            self.animCommands[frameNum].append(newAnimCommand)
        else:
            self.animCommands.update({frameNum:[newAnimCommand]})


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

    def calcViewScreenRect(self, focusCoord, offset=(0,0)):
        # Determine our center.
        center = ((focusCoord[0] * TILE_SIZE) + offset[0] + (TILE_SIZE // 2), (focusCoord[1] * TILE_SIZE) - (focusCoord[2] * TILE_SIZE) + offset[1] + (TILE_SIZE // 2))
        # The rect is supposed to stretch 384 (768 / 2) pixels around that center point.
        self.viewScreenRect.top = center[1] - VIEWPORT_SIZE // 2
        self.viewScreenRect.left = center[0] - VIEWPORT_SIZE // 2
        


    def getViewSurf(self, focusCoord, offset=[0,0]):
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

        self.calcViewScreenRect(focusCoord, offset)

        listOfLayers = []

        for z in range(self.levelZ): # For each layer
            
            layerSurf = pygame.Surface((VIEWSURF_PLUS_BUFFER, VIEWSURF_PLUS_BUFFER)) # Get a blank surface to blit onto
            layerSurf.fill((255, 0, 255)) # Fill with magenta
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


                        if self.aiming:
                            vDifferenceTxt = None
                            # Remember R,G,B = 0,1,2.
                            if [x, y, z] == self.cursorCoord: # Blit the cursor coord down
                                if self.thingInControl.currentActions[self.actionToPerform].isValidTarget(self.thingInControl, self, self.cursorCoord):
                                    spriteCoord = (1, 0)
                                    color = (0, 255, 0)
                                else:
                                    spriteCoord = (0, 0)
                                    color = (255, 0, 0)
                                if verticalDifference != 0:
                                    if verticalDifference > 0:
                                        sign = '+'
                                    elif verticalDifference < 0:
                                        sign = '-'
                                    vDifferenceTxt = DEFAULT_FONT.render(sign + str(abs(verticalDifference)), False, color)
                                    
                            # Blit the aiming area down, only on the entity's current layer.
                            elif ([x, y, z] in self.thingInControl.currentActions[self.actionToPerform].getTargetArea()) and (z == self.thingInControl.coord[2]):
                                spriteCoord = (2, 0)
                            else:
                                spriteCoord = None # Not in the aiming area, don't blit anything down
                                
                            if spriteCoord != None:
                                layerSurf.blit(AIM_SHEET.getSprite(spriteCoord), blitRect)
                            if vDifferenceTxt != None:
                                layerSurf.blit(vDifferenceTxt, (blitRect.left + 8, blitRect.top + 8))

            listOfLayers.append(layerSurf)
            verticalDifference += 1

        # Blit objects down
        for o in self.objects:
            obj = o[0]
            layer = obj.coord[2]
            verticalDifference = layer - focusCoord[2]
            layerStartCoord = (focusCoord[0] - 12, focusCoord[1] - 12 + verticalDifference)
            layerEndCoord = (focusCoord[0] + 14, focusCoord[1] + 14 + verticalDifference)

            objBlitRect = pygame.Rect(obj.coord[0] * TILE_SIZE, (obj.coord[1] * TILE_SIZE) - (obj.coord[2] * TILE_SIZE), TILE_SIZE, TILE_SIZE)

            if obj.visible:
                if self.viewScreenRect.colliderect(objBlitRect):
                    objSprite = obj.getSprite()
                    objBlitRect.top = (objBlitRect.top - (layerStartCoord[1] * TILE_SIZE))
                    objBlitRect.left = (objBlitRect.left - (layerStartCoord[0] * TILE_SIZE))
                    listOfLayers[layer].blit(objSprite, objBlitRect)
        
        # Blit entities down
        for layer in range(self.levelZ):
            verticalDifference = -focusCoord[2]
            layerStartCoord = (focusCoord[0] - 12, focusCoord[1] - 12 + verticalDifference)
            layerEndCoord = (focusCoord[0] + 14, focusCoord[1] + 14 + verticalDifference)

            for e in self.blitOrder[layer]:
                ent = self.entities[e]
                ent.calcRect()
                if ent.visible:
                    if self.viewScreenRect.colliderect(ent.rect):
                        entSprite = ent.getSprite()
                        entSpriteOffset = ent.getSpriteOffset()
                        entBlitRect = ent.rect.copy()
                        entBlitRect.top = (ent.rect.top - (layerStartCoord[1] * TILE_SIZE)) + entSpriteOffset[1]
                        entBlitRect.left = (ent.rect.left - (layerStartCoord[0] * TILE_SIZE)) + entSpriteOffset[0]
                        listOfLayers[layer].blit(entSprite, entBlitRect)
                        # Do stuff about changing the direction of the sprite
                        if self.aiming and ent == self.thingInControl:
                            viewingDirection = [self.cursorCoord[0] - ent.coord[0], self.cursorCoord[1] - ent.coord[1], self.cursorCoord[2] - ent.coord[2]]
                            ent.direction = viewingDirection
                ent.frameTick()
                
            verticalDifference += 1

        for layer in listOfLayers:
            viewSurf.blit(layer, (0,0))

        for g in self.gfx:
            g.frameTick()
            gfxBlitCoord = list(g.getCoord())
            gfxBlitCoord[0] -= startCoord[0] * TILE_SIZE
            gfxBlitCoord[1] -= startCoord[1] * TILE_SIZE
            viewSurf.blit(g.getSurface(), gfxBlitCoord)
            

        croppingRect = pygame.Rect(TILE_SIZE, TILE_SIZE, VIEWPORT_SIZE, VIEWPORT_SIZE)
        croppingRect.top += offset[1]
        croppingRect.left += offset[0]
        croppedViewSurf = viewSurf.subsurface(croppingRect)

        # Stuff with conversations and dialog boxes.  Always goes last.
        if self.conversation != None:
            self.conversation.frameTick()
            croppedViewSurf.blit(self.conversation.getSurface(), (0, 0))

        if len(self.dialogBoxes) > 0:
            for i in self.dialogBoxes:
                i.frameTick()
                croppedViewSurf.blit(i.getSurface(), i.getCoord())
    
        return croppedViewSurf


    def play(self, startPt, player, save):
        print('\nSTARTING LEVEL: ' + self.name)
        # Before main loop
        # Find the correct spawn point
        self.save = save
        
        # If you're loading from a save file, startPt will be None.  In that case the game will use the player's coordinate as saved in the file, and not move him to the spawn point.
        foundSpawnPt = False
        focusCoord = [0, 0, 0]
        for e in self.entities:
            ent = self.entities[e]
            ent.setLevel(self)
            
            if ent.type == "SpawnPt":
                print("Found spawn pt")
                if startPt != None:
                    if ent.name == startPt:
                        print("Found right spawn pt")
                        foundSpawnPt = True
                        focusCoord = ent.coord

        # Once you find the correct spawn point
        if startPt != None:
            if foundSpawnPt:
                # Add the player to the list of entities
                print("Adding player")
                player.moveToCoord(focusCoord.copy())
                
        print("Starting coord = " + str(player.getCoord()))
        self.addEntity(player)
        self.thingInControl = player

        # Start gathering input
        self.flushInput()

        # Create HUD
        self.hud = HUD()

        numOfTargets = 0

        # Get the blit order, to start with
        self.getBlitOrder()
        print(self.blitOrder)

        # Make sure you redraw the bkg
        self.lastFocusCoord = [-1,-1,-1]

        self.loadFromSave(self.save)
        self.addGFX(FadeIn(self, ((player.coord[0] - 12) * 32, (player.coord[1] - 12) * 32)))

        clearToMove = False
        
        # Start main loop
        while True:
            self.lastInput = self.currentInput
            self.currentInput = getInput()
            upPress = False
            downPress = False
            rightPress = False
            leftPress = False

                        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_e:
                        print(self.entities)

            if ('UP' not in self.currentInput) and ('DOWN' not in self.currentInput) and ('LEFT' not in self.currentInput) and ('RIGHT' not in self.currentInput): # Keep the player from moving if they've just entered the level and haven't let go of the arrow keys
                clearToMove = True


            if not self.pauseForAnimation:
                if self.conversation == None and len(self.dialogBoxes) == 0:
                    if self.aiming:
                        # Move the cursor if aiming
                        if keyDown('UP', self.currentInput, self.lastInput) and self.cursorCoord[1] > 0:
                            self.cursorCoord[1] -= 1
                        if keyDown('DOWN', self.currentInput, self.lastInput) and self.cursorCoord[1] < self.levelY - 1:
                            self.cursorCoord[1] += 1
                        if keyDown('RIGHT', self.currentInput, self.lastInput) and self.cursorCoord[0] < self.levelX - 1:
                            self.cursorCoord[0] += 1
                        if keyDown('LEFT', self.currentInput, self.lastInput) and self.cursorCoord[0] > 0:
                            self.cursorCoord[0] -= 1
                        for key in ['V', 'M', 'I', 'D']:
                            if keyDown(key, self.currentInput, self.lastInput) and self.thingInControl.currentActions[key] != None:
                                #print(key + ' pressed')
                                if key != self.actionToPerform:
                                    self.thingInControl.currentActions[key].perform(self.thingInControl, self, None)
                                elif key == self.actionToPerform:
                                    # Do something, Taipu, about getting a target
                                    if self.thingInControl.currentActions[key].isValidTarget(self.thingInControl, self, self.cursorCoord, self.currentTarget):
                                        self.targets.append(self.cursorCoord)
                                        self.currentTarget += 1

                    if not self.aiming:
                        # Movement
                        if clearToMove:
                            whereToMove = list(player.coord)
                            if 'UP' in self.currentInput:
                                whereToMove[1] -= 1
                            if 'DOWN' in self.currentInput:
                                whereToMove[1] += 1
                            if 'RIGHT' in self.currentInput:
                                whereToMove[0] += 1
                            if 'LEFT' in self.currentInput:
                                whereToMove[0] -= 1

                            if whereToMove != list(player.coord):
                                #print(whereToMove)
                                MOVE_ONE_STEP.perform(player, self, [whereToMove])
                                self.getBlitOrder()

                        for key in ['V', 'M', 'I', 'D']:
                            # Actions
                            if keyDown(key, self.currentInput, self.lastInput) and self.thingInControl.currentActions[key] != None:
                                numOfTargets = self.thingInControl.currentActions[key].getTargets() # Get the number of targets we need to aim at
                                self.targets = []
                                self.actionToPerform = key # Record which action we're aiming for
                                self.currentTarget = 1
                                if numOfTargets > 0:
                                    self.aiming = True
                                    self.cursorCoord = self.thingInControl.coord.copy()
                                    self.thingInControl.switchToAiming(key)
                                    self.thingInControl.currentActions[key].generateTargetArea(self.thingInControl, self.currentTarget)

                        if keyUp('MENU', self.currentInput, self.lastInput):
                            self.addDialogBox(LevelMenu(self))

                        # A button to print the inventory, for testing purposes
                        if keyUp('BACK', self.currentInput, self.lastInput):
                            print(self.thingInControl.inventory)
                            


            # Performing actions
            if self.currentTarget > numOfTargets:
                self.thingInControl.currentActions[self.actionToPerform].perform(self.thingInControl, self, self.targets)
                self.currentTarget = 0
                self.hud.getSurf(player, override=True)
                if self.aiming:
                    # Reset stuff
                    self.aiming = False
                    self.thingInControl.stopAiming()

            # Animation commands
            if self.animating:
                self.animFrameCounter += 1
                if self.animFrameCounter in self.animCommands:
                    setOfCommands = self.animCommands[self.animFrameCounter]
                    for c in setOfCommands:
                        # Fill this in later, do something for each different command.  Each command should be a string.
                        if c.startswith('Anim'):
                            splitText = c.split(':')
                            self.entities[splitText[1]].changeAnim(splitText[2])
                        elif c.startswith('changeOffsetForm'):
                            splitText = c.split(':')
                            self.entities[splitText[1]].changeOffsetForm(splitText[2])
                        elif c.startswith('exitLevel'):
                            splitText = c.split(':')
                            self.save.getLevelChanges(self)
                            return splitText[1], splitText[2]
                        elif c.startswith('reset'):
                            self.resetAnimation()

            # Check to see if the player collided with any entities
            if self.conversation == None and not self.animating:
                entsCollidingWithPlayer = self.getEntsAtCoord(player.coord)
                if entsCollidingWithPlayer != []:
                    for e in entsCollidingWithPlayer:
                        ent = self.entities[e]
                        # Exit point
                        if ent.type == 'ExitPt':
                            self.addAnimCommand(17, 'exitLevel:'+ent.targetMap+':'+ent.targetSpawn)
                            self.addGFX(FadeOut(self, ((player.coord[0] - 12) * 32, (player.coord[1] - 12) * 32)))
                            self.animating = True
                        
                        # Pressure plate
                        elif ent.type == 'PressurePlate':
                            ent.trigger(player)

                    
            self.getBlitOrder()
            viewSurf = self.getViewSurf(player.coord, player.getSpriteOffset())
            WINDOW.blit(viewSurf, (0, 0))

            # Do stuff with conversations, dialog boxes
            if self.conversation != None:
                if len(self.dialogBoxes) == 0:
                    self.conversation.takeInput(self.currentInput, self.lastInput)

            if len(self.dialogBoxes) > 0:
                self.dialogBoxes[-1].takeInput(self.currentInput, self.lastInput)

            HUDSURF.fill((128, 128, 128))
            WINDOW.blit(self.hud.getSurf(player), HUDRECT)

            WINDOW.blit(DEFAULT_FONT.render(str(player.coord), False, (0, 0, 255)), (0, 736))
            WINDOW.blit(DEFAULT_FONT.render(str(int(CHRONO.get_fps())), False, (0, 0, 255)), (128, 736))
            
            pygame.display.update()
            CHRONO.tick(FRAMES_PER_SECOND)



finished = True
print("Done loading Level class")
