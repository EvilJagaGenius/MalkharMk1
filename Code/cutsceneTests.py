# TIOM cutscene tests.

import pygame, sys, os
from pygame import *
pygame.init()

def calcDirFromVector(vector):
    x = vector[0]
    y = vector[1]
    quadrant = 0

    # First do a quick determination if we have a vertical/horizontal vector
    if x == 0:
        if y >= 0:
            return S # Face south by default
        else:
            return N

    if y == 0:
        if x > 0:
            return E
        elif x < 0:
            return W

    # If the quick determinations didn't work
    # Get the tangent
    tangent = y / x
    # Calculate the angle
    angle = atan(tangent)
    if angle < 0: # If it's negative
        angle += (2 * pi) # Convert it to its positive form

    # Apply necessary corrections if in the second or third quadrants
    if x < 0:
        if y > 0:
            angle -= pi
        elif y < 0:
            angle += pi
        
    # Calculate which direction we're facing.
    # 45 degrees = pi/4 radians.
    if (angle > (15 * pi / 8) and angle <= (2 * pi)) or (angle >= 0 and angle <= (pi / 8)): # E = 15pi/8 to pi/8
        return E
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # SE = pi/8 to 3pi/8
        return SE
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # S = 3pi/8 to 5pi/8
        return S
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # SW = 5pi/8 to 7pi/8
        return SW
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return W
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # NW = 9pi/8 to 11pi/8
        return NW
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # N = 11pi/8 to 13pi/8
        return N
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # NE = 13pi/8 to 15pi/8
        return NE


def calcDirFromAngle(angle):
    # Takes in angle (in radians) and returns a string like "N" or "SE"
    # Calculate which direction we're facing.
    # 45 degrees = pi/4 radians.
    if (angle > (15 * pi / 8) and angle <= (2 * pi)) or (angle >= 0 and angle <= (pi / 8)): # E = 15pi/8 to pi/8
        return E
    elif (angle > (pi / 8) and angle <= (3 * pi / 8)): # NE = pi/8 to 3pi/8
        return SE
    elif (angle > (3 * pi / 8) and angle <= (5 * pi / 8)): # N = 3pi/8 to 5pi/8
        return S
    elif (angle > (5 * pi / 8) and angle <= (7 * pi / 8)): # NW = 5pi/8 to 7pi/8
        return SW
    elif (angle > (7 * pi / 8) and angle <= (9 * pi / 8)): # W = 7pi/8 to 9pi/8
        return W
    elif (angle > (9 * pi / 8) and angle <= (11 * pi / 8)): # SW = 9pi/8 to 11pi/8
        return NW
    elif (angle > (11 * pi / 8) and angle <= (13 * pi / 8)): # S = 11pi/8 to 13pi/8
        return N
    elif (angle > (13 * pi / 8) and angle <= (15 * pi / 8)): # SE = 13pi/8 to 15pi/8
        return NE


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

def getKeybinds():
    configFile = open('config.cfg', 'r')
    for line in configFile:
        line = line.strip()
        splitLine = line.split('~')
        action = splitLine[0]
        binds = splitLine[1].split('|')
        KEYBINDS.update({action:binds})

def getInput(): # Find what actions are currently being pressed down.
    keyPresses = pygame.key.get_pressed()
    inputs = []
    for i in KEYBINDS:
        for j in KEYBINDS[i]:
            if j.startswith('K_'):
                key = int(j.strip('K_'))
                if keyPresses[key]:
                    inputs.append(i)
                    
    return inputs

def keyUp(action, currentInput, lastInput):
    return ((action in lastInput) and (action not in currentInput))

def keyDown(action, currentInput, lastInput):
    return ((action in currentInput) and (action not in lastInput))

WX = 1024
WY = 768
WINDOW = pygame.display.set_mode((WX, WY), 0, 32)

CHRONO = pygame.time.Clock()

# Symbolic direction constants
DIRECTION_NUMBERS = {"N":4, "NW":5, "W":6, "SW":7, "S":0, "SE":1, "E":2, "NE":3}
N = DIRECTION_NUMBERS["N"]
S = DIRECTION_NUMBERS["S"]
E = DIRECTION_NUMBERS["E"]
W = DIRECTION_NUMBERS["W"]
NE = DIRECTION_NUMBERS["NE"]
NW = DIRECTION_NUMBERS["NW"]
SE = DIRECTION_NUMBERS["SE"]
SW = DIRECTION_NUMBERS["SW"]

DUMMY_SURFACE = pygame.Surface((0, 0))

DEFAULT_FONT = pygame.font.Font(None, 24)
DEFAULT_FONT_COLOR = (255, 255, 255)

TXT_TEMPLATE_SURFACE = pygame.surface.Surface((768, 128))
TXT_TEMPLATE_SURFACE.fill((127, 127, 127))

KEYBINDS = {}
getKeybinds()


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

class AnimSheet:
    def __init__(self, sheet, frames=None):
        self.sheet = sheet
        self.frames = frames
        self.frameCount = 0
        self.currentSprite = (0, 0)

    def setFrames(self, frames):
        # self.frames is supposed to be a dictionary, like so:
        # self.frames = {frameNum:spriteCoord, frameNum2:spriteCoord2, ... frameNumN:spriteCoordN}
        # Also, instead of spriteCoord being an (x, y) or [x, y] coord, it could be a statement like 'goto:frameNum'.
        self.frames = frames

    def frameTick(self, advFrame=True):
        if advFrame:
            self.frameCount += 1
        if self.frames != None:
            if self.frameCount in self.frames:
                self.currentSprite = self.frames[self.frameCount]
                # Do something, Taipu
                if type(self.currentSprite) == type(''):
                    if self.currentSprite.startswith('goto'):
                        splitLine = self.frames[self.frameCount].split(':')
                        desiredFrame = int(splitLine[1])
                        self.goToFrame(desiredFrame)
                else: # If it's not a string then it's an (x, y) or [x, y] coord.
                    self.currentSprite = self.frames[self.frameCount]

    def getCurrentSprite(self, spriteStartingCoord):
        if type(self.currentSprite) == type(''):
            return self.currentSprite
        else:
            return self.sheet.getSprite((spriteStartingCoord[0] + self.currentSprite[0], spriteStartingCoord[1] + self.currentSprite[1]))

    def goToFrame(self, frameNum):
        # Note: Make sure frameNum is one of the values in self.frames.
        if frameNum in self.frames:
            self.frameCount = frameNum
            self.currentSprite = self.frames[frameNum]

    def getSpriteAtFrame(self, spriteStartingCoord, frameNum):
        # Basically:
        # Loop through the frames, follow along with the instructions and all
        # Return the resulting sprite coord
        # Copied from the Animation() class
        counter = 0
        for i in range(frameNum):
            if counter in self.frames:
                if type(self.frames[counter]) == type(''): # If the thing at that frame number isn't a sprite, but a string
                    if self.frames[counter].startswith('goto:'): # If it's goto:frameNum
                        a = self.frames[counter]
                        b = a.split(':')
                        c = int(b[1])
                        counter = c

                else:
                    spriteToReturn = self.frames[counter]

            counter += 1


        return self.sheet.getSprite((spriteStartingCoord[0] + spriteToReturn[0], spriteStartingCoord[1] + spriteToReturn[1]))

    def reset(self):
        self.frameCount = 0
        self.currentSprite = self.frames[self.frameCount]

class DialogBox:
    def __init__(self):
        self.level = None
        self.levelName = None
        self.surface = DUMMY_SURFACE
        self.coord = (0, 0)

    def getSurface(self):
        return self.surface

    def getCoord(self):
        return self.coord

    def setLevel(self, level):
        self.level = level
        self.levelName = self.level.name

    def setLevelName(self, levelName):
        self.levelName = levelName

    def takeInput(self):
        pass

    def frameTick(self):
        pass

class Conversation(DialogBox):
    def __init__(self, file, convType='Room'):
        DialogBox.__init__(self)
        self.text = {}
        self.file = file
        self.topic = None
        self.part = None
        self.startTopic = None
        self.startPart = None
        self.currentText = None
        self.currentTextSplit = None
        self.textToDisplay = None
        self.choiceBox = None
        self.paused = True
        self.pauseFrameCounter = 0
        self.framesToPauseFor = 0
        self.font = DEFAULT_FONT
        self.color = (255, 255, 255)
        self.convType = convType

        self.participants = []

        # Animation stuff
        self.spaceLength = self.font.size(' ')[0]
        self.fontHeight = self.font.get_height()
        self.xLimit = TXT_TEMPLATE_SURFACE.get_width()
        self.yLimit = TXT_TEMPLATE_SURFACE.get_width()
        
        self.stopAnimating = False
        self.currentWordIndex = 0
        self.currentWord = None
        self.currentLetterIndex = 0
        self.currentLetter = None
        self.letterX = self.spaceLength
        self.letterY = 0
        self.letterSize = (0, 0)
        
        self.surface = TXT_TEMPLATE_SURFACE.copy()


    def addTopic(self, line):   # line being the line in the .ent file.
        line = line.strip()
        splitLine = line.split('~')
        topic = splitLine[0]
        text = splitLine[1].split('|')
        self.text.update({topic:text})

    def advance(self):  # Go to the next part in the topic, executing any flags along the way.
        self.part += 1
        self.currentText = self.text[self.topic][self.part]

        self.resetAnimationStuff()
        
        self.checkForFlags()
            
        # Once you land on actual text again:
        if not self.stopAnimating:
            self.clearSurface()
        

    def checkForFlags(self):
        # Check for flags, execute flags, etc, add code later
        while self.currentText.startswith('!') and not self.paused:
            # Do something, Taipu
            # ...depending on which kind of flag it is.

            # Exit flag
            if self.currentText.startswith('!XX:'):
                # Exit the conversation
                self.level.endConversation()
                break

            # Choice box
            if self.currentText.startswith('!CB:'):
                choiceBox = ChoiceBox(self.currentText, self.level)
                self.stopAnimating = True
                self.level.currentInput = []
                self.level.lastInput = []
                self.level.addDialogBox(choiceBox)
                break

            # Go to
            if self.currentText.startswith('!GT:'):
                splitText = self.currentText.split(':')[1].split('/')
                self.goto(splitText[0], int(splitText[1]))
                break

            # Change animation
            if self.currentText.startswith('!CA:'):
                if not self.paused:
                    splitText = self.currentText.split(':')
                    self.level.changeAnimation(splitText[1], splitText[2])
                    self.advance()
                break

            if self.currentText.startswith('!CD:'):
                splitText = self.currentText.split(':')
                self.level.changeDirection(splitText[1], int(splitText[2]), int(splitText[3]), int(splitText[4]))
                self.advance()
                    

    def goto(self, topic, part):    # Go to the desired topic and part in the conversation.
        self.topic = topic
        self.part = part
        self.currentText = self.text[topic][part]

        self.resetAnimationStuff()
        
        self.checkForFlags()
        
        # After the flags and you're on actual text again
        if not self.stopAnimating:
            self.clearSurface()
        
        

    def loadConversation(self):
        print('Loading conversation')
        fileName = self.file
        if self.convType == 'Room':
            file = txtLoad(['..', 'Data', 'Rooms', self.levelName, 'entities', fileName], 'r')
        elif self.convType == 'Cutscene':
            file = txtLoad(['..', 'Data', 'Cutscenes', self.levelName, fileName], 'r')
        loading = False
        for line in file:
            line = line.strip()
            if line.startswith('END_CONVERSATION'):
                print('Done loading conversation')
                loading = False
            if loading:
                if not line.startswith('!'):
                    self.addTopic(line)
                else:
                    if line.startswith('!setStartTopic'):
                        print('Setting starting topic')
                        splitLine = line.split(':')
                        self.startTopic = splitLine[1]
                    elif line.startswith('!setStartPart'):
                        print('Setting starting part')
                        splitLine = line.split(':')
                        self.startPart = int(splitLine[1])
                    elif line.startswith('!participants'):
                        print('Setting participants')
                        splitLine = line.split(':')
                        self.participants = splitLine[1].split(',')
                        print(self.participants)
            if line.startswith('LOAD_CONVERSATION'):
                print('Starting to load conversation')
                loading = True

        # Once we're done loading
        self.goto(self.startTopic, self.startPart)
        file.close()

    def setLevel(self, level):
        self.level = level
        self.levelName = self.level.name
        self.loadConversation()

    def resetConversation(self):
        self.goto(self.startTopic, self.startPart)

    def takeInput(self, currentInput, lastInput):
        if keyUp('V', currentInput, lastInput) and self.stopAnimating:
            self.advance()

    def frameTick(self):
        # We want to blit one letter per frame.
        if not self.stopAnimating:
            if not self.paused:
                # Blit the letter
                self.letterSize = self.font.size(self.currentLetter)
                self.surface.blit(self.font.render(self.currentLetter, True, self.color), (self.letterX, self.letterY))
                self.letterX += self.letterSize[0]
                self.currentLetterIndex += 1
                if self.currentLetterIndex >= len(self.currentWord): # If we're on the last letter
                    if self.currentWordIndex >= len(self.currentTextSplit) - 1: # If we're on the last word
                        self.stopAnimating = True
                        return
                    else: # Otherwise
                        # Go to the next word
                        if self.currentWord.endswith('.') or self.currentWord.endswith('!') or self.currentWord.endswith('?'): # If it ends with a period, exclamation point or question mark
                            self.letterX += self.spaceLength * 2 # Add a double space
                        else: # Otherwise
                            self.letterX += self.spaceLength # Add a single space
                        self.currentLetterIndex = 0

                        self.currentWordIndex += 1
                        self.currentWord = self.currentTextSplit[self.currentWordIndex]

                        while self.currentWord == '':
                            self.currentWordIndex += 1
                            self.currentWord = self.currentTextSplit[self.currentWordIndex]

                        if self.currentWord == '!SK:': # If it's a skip flag
                            self.advance()
                            return

                        elif self.currentWord.startswith('!PS:'): # If it's a pause flag
                            self.paused = True
                            self.pauseFrameCounter = 0
                            self.framesToPauseFor = int(self.currentWord.split(':')[1])
                            print('Pausing for ' + str(self.framesToPauseFor) + ' frames')

                            # Advance to the next word and letter
                            self.currentWordIndex += 1
                            self.currentWord = self.currentTextSplit[self.currentWordIndex]
                            self.currentLetterIndex = 0
                            self.currentLetter = self.currentWord[self.currentLetterIndex]
                            return

                        if self.currentWord == '\n': # If it's a newline:
                            if (self.letterY + self.fontHeight * 2 + 4) < self.yLimit: # Skip a line!
                                self.letterY += self.fontHeight + 2
                                self.letterX = self.spaceLength
                                return
                        
                        if (self.letterX + self.font.size(self.currentWord)[0] + self.spaceLength) >= self.xLimit: # If we'll go off the surface with the next word
                            if (self.letterY + self.fontHeight * 2 + 4) < self.yLimit: # Skip a line!
                                self.letterY += self.fontHeight + 2
                                self.letterX = self.spaceLength

                self.currentLetter = self.currentWord[self.currentLetterIndex]
                
            elif self.paused:
                self.pauseFrameCounter += 1
                if self.pauseFrameCounter >= self.framesToPauseFor:
                    self.paused = False

        elif self.stopAnimating: # Stop the participants' talking animations when the text is done scrolling.  Later when you have voice lines, add an and statement to wait until that finishes too.
            if self.convType == 'Room':
                for p in self.participants:
                    self.level.entities[p].currentAnim.goToFrame(-1)
            elif self.convType == 'Cutscene':
                for p in self.level.puppets:
                    puppet = self.level.puppets[p]
                    puppet.currentAnimation.goToFrame(-1)

    def resetAnimationStuff(self):
        self.stopAnimating = False
        self.currentTextSplit = self.currentText.split(' ')
        self.currentWordIndex = 0
        self.currentWord = self.currentTextSplit[self.currentWordIndex]
        self.currentLetterIndex = 0
        self.currentLetter = self.currentWord[self.currentLetterIndex]
        self.letterX = self.spaceLength
        self.letterY = 0


    def clearSurface(self):
        self.surface = TXT_TEMPLATE_SURFACE.copy()


    def getSurface(self):
        return self.surface






# Start of new code
class Cutscene:
    # Store in a folder with a .scs file (Sprite CutScene)
    def __init__(self, name):
        self.name = name
        self.puppets = {}
        self.animCommands = []
        self.animCommandCounter = 0
        self.currentCommand = ''

        self.conversation = Conversation(self.name+'.scs', 'Cutscene')
        self.conversation.setLevel(self)
        self.inConversation = False

        self.background = None
        self.foreground = None

        self.focusCoord = [0,0]
        self.dimensions = (WX, WY)

        # Load the puppets
        for filename in os.listdir(os.path.join('..', 'Data', 'Cutscenes', self.name, 'puppets')):
            puppet = CutscenePuppet(self.name, filename)
            self.puppets.update({puppet.name:puppet})

        self.loadFromFile()

        self.currentInput = []
        self.lastInput = []


    def getViewSurf(self):
        viewSurf = pygame.surface.Surface((self.dimensions))
        if self.background != None:
            viewSurf.blit(self.background, (0,0))

        for p in self.puppets:
            puppet = self.puppets[p]
            puppet.frameTick()
            if puppet.visible:
                viewSurf.blit(puppet.getSprite(), puppet.coord)

        if self.foreground != None:
            viewSurf.blit(self.foreground, (0,0))

        # Stuff with conversations
        if self.inConversation:
            viewSurf.blit(self.conversation.getSurface(), self.conversation.coord)
            
        return viewSurf
        

            
    def play(self): # Give it the same arguments as a Level but don't actually do anything with them
        animationFrameCounter = 0
        while True:
            self.lastInput = self.currentInput
            self.currentInput = getInput()
            
            WINDOW.fill((0,0,0))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            if not self.inConversation:
                while self.currentCommand.startswith(str(animationFrameCounter) + ':'):
                    print(self.currentCommand)
                    command = self.currentCommand.split(':')[1].split('|')
                    if command[0] == 'movePuppet':
                        self.puppets[command[1]].move(int(command[2]), int(command[3]))
                    elif command[0] == 'changePuppetDirection':
                        self.puppets[command[1]].changeDirection(int(command[2]), int(command[3]), int(command[4]))
                    elif command[0] == 'changePuppetMotion':
                        self.changePuppetMotion(command[1], command[2])
                    elif command[0] == 'changePuppetAnimation':
                        self.puppets[command[1]].changeAnimation(command[2])
                    elif command[0] == 'startConversation':
                        # Do something, Taipu
                        self.conversation.paused = False
                        self.inConversation = True
                        self.conversation.goto(command[1], 0)
                    elif command[0] == 'changeBackground':
                        self.background = self.images[command[1]]
                    elif command[0] == 'changeForeground':
                        self.foreground = self.images[command[1]]
                        
                    elif command[0] == 'end':
                        pygame.display.update()
                        return # Fill this in later/when you add it to the rest of the TIOM code
                    
                    self.animCommandCounter += 1
                    self.currentCommand = self.animCommands[self.animCommandCounter]

                animationFrameCounter += 1
                         

            elif self.inConversation:
                self.conversation.frameTick()
                self.conversation.takeInput(self.currentInput, self.lastInput)
                

            viewSurf = self.getViewSurf()
            WINDOW.blit(viewSurf, (0,0))
                
            pygame.display.update()
            CHRONO.tick(30)
            

    def movePuppet(self, puppetName, x, y):
        self.puppets[puppetName].coord = [x, y]

    def changeDirection(self, puppetName, x, y, z):
        self.puppets[puppetName].direction = (x, y, z)

    def changePuppetMotion(self, puppetName, motion):
        if motion == 'noMotion':
            self.puppets[puppetName].motion = noMotion
        elif motion == 'walkMotion':
            self.puppets[puppetName].motion = walkMotion

    def changeAnimation(self, puppet, newAnim):
        self.puppets[puppet].changeAnimation(newAnim)

    def loadFromFile(self):
        file = txtLoad(['..', 'Data', 'Cutscenes', self.name, self.name+'.scs'], 'r')
        loading = None
        for line in file:
            line = line.strip()
            if line.startswith('ANIM_COMMANDS'):
                loading = 'ANIM_COMMANDS'

            elif line.startswith('LOAD_IMAGES'):
                loading = 'IMAGES'

            elif line.startswith('BACKGROUND'):
                if not line.endswith('=X'):
                    self.images.update({'background':imgLoad(['..', 'Data', 'Cutscenes', self.name, 'imgs', line.split('=')[1]])})
                    self.background = self.images['background']

            elif line.startswith('FOREGROUND'):
                if not line.endswith('=X'):
                    self.images.update({'foreground':imgLoad(['..', 'Data', 'Cutscenes', self.name, 'imgs', line.split('=')[1]])})
                    self.foreground = self.images['foreground']

            if loading == 'ANIM_COMMANDS':
                if line.startswith('ANIM_COMMANDS'):
                    pass
                elif line.startswith('END_ANIM_COMMANDS'):
                    loading = None
                else:
                    self.animCommands.append(line)

            elif loading == 'IMAGES':
                if line.startswith('LOAD_IMAGES'):
                    pass
                elif line.startswith('END_IMAGES'):
                    loading = None
                else:
                    splitLine = line.split('=')
                    self.images.update({splitLine[0]:imgLoad(['..', 'Data', 'Cutscenes', self.name, 'imgs', splitLine[1]])})

        self.currentCommand = self.animCommands[self.animCommandCounter]
        file.close()

    def endConversation(self):
        self.inConversation = False
        self.conversation.paused = True

    def flushInput():
        self.currentInput = []
        self.lastInput = []


class CutscenePuppet:
    # An object with a spritesheet and animations and such.  Load them from .pup files in the cutscene folder.
    def __init__(self, sceneName, filename):
        self.name = ''
        self.sceneName = sceneName
        self.filename = filename
        self.spriteSheet = None
        self.coord = (0,0)
        self.currentAnimation = None
        self.animFrameCounter = 0
        self.animations = {}
        self.visible = True
        self.direction = (0, 1, 0)

        self.motion = noMotion

        self.loadFromFile()

        self.sprite = DUMMY_SURFACE

    def loadFromFile(self):
        file = txtLoad(['..', 'Data', 'Cutscenes', self.sceneName, 'puppets', self.filename], 'r')
        loadingAnimations = False
        for line in file:
            line = line.strip()
            if line.startswith('VISIBLE'):
                if line.endswith('Y'):
                    self.visible = True
                else:
                    self.visible = False

            elif line.startswith('NAME'):
                self.name = line.split('=')[1]
                    
            elif line.startswith('SPRITESHEET'):
                sheetArgs = line.split('=')[1].split('|')
                self.spriteSheet = SpriteSheet(sheetArgs[0], int(sheetArgs[1]), int(sheetArgs[2]), (255, 0, 255))

            elif line.startswith('ANIMATIONS'):
                loadingAnimations = True

            if loadingAnimations:
                if line.startswith('ANIMATIONS'):
                    pass
                elif line.startswith('END_ANIMATIONS'):
                    loadingAnimations = False
                else:
                    animName = line.split('=')[0]
                    frameData = line.split('=')[1].split('|')
                    frames = {}
                    for f in frameData:
                        f = f.split(',')
                        if len(f) == 2: # Then it's a frame#,goto: sort of deal
                            frames.update({int(f[0]):f[1]})
                        elif len(f) == 3: # Then it's a frame#,x,y sort of deal
                            frames.update({int(f[0]):(int(f[1]), int(f[2]))})

                    # Create an AnimSheet object and add it to self.animations
                    animation = AnimSheet(self.spriteSheet, frames)
                    self.animations.update({animName:animation})

        file.close()

    def frameTick(self):
        self.coord[0] += self.motion(self.animFrameCounter, self.direction)[0]
        self.coord[1] += self.motion(self.animFrameCounter, self.direction)[1]
        self.sprite = self.currentAnimation.getCurrentSprite((calcDirFromVector(self.direction), 0))
        if type(self.sprite) == type(''):
            # Do something, Taipu
            #print('self.sprite is a string:  ' + self.sprite)
            if self.sprite.startswith('changeAnim'):
                newAnim = self.sprite.split(':')[1]
                self.changeAnimation(newAnim)
        self.currentAnimation.frameTick()
        self.sprite = self.currentAnimation.getCurrentSprite((calcDirFromVector(self.direction), 0))
        
        self.animFrameCounter += 1
        

    def move(self, x, y):
        self.coord = [x, y]

    def changeDirection(self, x, y, z):
        self.direction = (x, y, z)

    def changeMotion(self, newMotion):
        self.motion = newMotion
        self.animFrameCounter = 0

    def changeAnimation(self, newAnim):
        self.currentAnimation = self.animations[newAnim]
        self.currentAnimation.reset()

    def getSprite(self):
        return self.sprite

# Cutscene motion functions
def noMotion(frameNum, direction):
    return (0,0)

def walkMotion(frameNum, direction):
    return (direction[0] * 7, direction[1] * 7)

testCutscene1 = Cutscene('testCutscene1')
testCutscene1.play()
