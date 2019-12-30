#TIOM conversation tests.

import pygame, sys, os
from pygame import *
pygame.init()

WX = 768
WY = 512
WINDOW = pygame.display.set_mode((WX, WY), 0, 32)

DEFAULT_FONT = pygame.font.Font(None, 24)
DEFAULT_FONT_COLOR = (255, 255, 255)
TXT_TEMPLATE_SURFACE = pygame.surface.Surface((768, 128))
TXT_TEMPLATE_SURFACE.fill((127, 127, 127))

# Functions copied from Main.py
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

def txtToSurface(startSurface, txt, font=DEFAULT_FONT, color=DEFAULT_FONT_COLOR): # This function covers a pygame.Surface with text.
    surface = startSurface.copy()
    xLimit = surface.get_width()
    yLimit = surface.get_height()
    x = 0
    y = 0
    fontHeight = font.get_height()
    spaceLength = font.size(' ')[0]
    ignoreLine = False

    txt = txt.split(' ') # txt is now a list.

    # NTS, have newlines as their own word.
    for word in txt:
        if word != '!SK:':
            if word == '\n': # If there's a newline char
                if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                    y += fontHeight + 2
                    x = 0
                else:
                    break
            else: # For any other word
                if x + font.size(word)[0] <= xLimit: # If the word fits on the surface
                    surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                    x += font.size(word)[0]
                    if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period or similar thingus
                        x += spaceLength * 2 # Add a double space
                    else: # Otherwise
                        x += spaceLength # Add a single space
                else: # BUT if it doesn't fit...
                    if (y + fontHeight * 2 + 4) < yLimit: # Skip a line!
                        y += fontHeight + 2
                        x = 0
                        surface.blit(font.render(word, True, color), (x, y)) # Blit it on there
                        x += font.size(word)[0]
                        if word.endswith('.') or word.endswith('!') or word.endswith('?'): # If it ends with a period
                            x += spaceLength * 2 # Add a double space
                        else: # Otherwise
                            x += spaceLength # Add a single space
                    else:
                        break

    return surface # Et voila, a text-covered surface!

def choiceBoxSurface(choices, selected):
    # choices=list, selected=int
    # Each choice will only take up one line.
    maxX = 0
    txtSurface = pygame.Surface((WX, (DEFAULT_FONT.get_height()+4)*len(choices)))
    y = 0
    txtSurface.fill((100,100,100))
    for c in choices:
        txt = c
        color = (255,255,255) # Normally white
        if c == choices[selected]:
            color = (0,0,255) # Highlighted blue
        txtSurface.blit(DEFAULT_FONT.render(txt, True, color), (0, y))
        y += DEFAULT_FONT.get_height()+4
        if DEFAULT_FONT.size(txt)[0] > maxX:
            maxX = DEFAULT_FONT.size(txt)[0]

    # All the text should be blitted, now to clean it up.
    eraser = pygame.Surface((WX-(maxX+4), y))
    eraser.fill((0,255,0))
    txtSurface.blit(eraser, (maxX+4, 0))
    txtSurface.set_colorkey((0,255,0))
    return txtSurface


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

KEYBINDS = {}
getKeybinds()
print(KEYBINDS)

# End copied functions




class DummyLevel:
    # A class meant to take the place of the Level class, stripped to the bare minimum to test with.
    def __init__(self):
        self.conversation = None
        self.dialogBoxes = []
        self.currentInput = []
        self.lastInput = []

    def setConversation(self, conversation):
        self.conversation = conversation

    def endConversation(self):
        print('Ending conversation')
        self.conversation.topic = self.conversation.startTopic
        self.conversation.part = self.conversation.startPart
        self.conversation = None

    def removeDialogBox(self, dialogBox):
        if dialogBox in self.dialogBoxes:
            self.dialogBoxes.remove(dialogBox)

    def addDialogBox(self, dialogBox):
        self.dialogBoxes.append(dialogBox)

    def play(self):
        self.lastInput = []
        while True:
            
            WINDOW.fill((0,0,0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.currentInput = getInput()

            if self.conversation != None:
                WINDOW.blit(self.conversation.getSurface(), (0, 0))
                if len(self.dialogBoxes) == 0:
                    self.conversation.takeInput(self.currentInput, self.lastInput)

            if len(self.dialogBoxes) > 0:
                for i in self.dialogBoxes:
                    WINDOW.blit(i.getSurface(), i.getCoord())
                self.dialogBoxes[-1].takeInput(self.currentInput, self.lastInput)

            pygame.display.update()
            self.lastInput = self.currentInput


class Conversation:
    def __init__(self, file, level):
        self.text = {}
        self.topic = None
        self.part = None
        self.startTopic = None
        self.startPart = None
        self.currentText = None
        self.textToDisplay = None
        self.choiceBox = None
        self.txtSurface = None
        self.level = level
        self.paused = False

        self.loadConversation(file)

    def addTopic(self, line):   # line being the line in the .ent file.
        line = line.strip()
        splitLine = line.split('~')
        topic = splitLine[0]
        text = splitLine[1].split('|')
        self.text.update({topic:text})

    def advance(self):  # Go to the next part in the topic, executing any flags along the way.
        self.part += 1
        self.currentText = self.text[self.topic][self.part]
        self.textToDisplay = self.currentText
        self.checkForFlags()

        while self.currentText.endswith('!SK:'):
            self.part += 1
            self.currentText = self.text[self.topic][self.part]
            self.textToDisplay = self.currentText
            self.checkForFlags()
        
        # Once you land on actual text again:
        self.txtSurface = txtToSurface(TXT_TEMPLATE_SURFACE, self.textToDisplay)

    def checkForFlags(self):
        # Check for flags, execute flags, etc, add code later
        while self.currentText.startswith('!') and not self.paused:
            print('Doing flag loop')
            # Do something, Taipu
            # ...depending on which kind of flag it is.

            # Exit flag
            if self.currentText.startswith('!XX:'):
                # Exit the conversation
                self.level.endConversation()
                break

            # Choice box
            if self.currentText.startswith('!CB:'):
                print('Choice Box')
                choiceBox = ChoiceBox(self.currentText, self.level)
                self.textToDisplay = self.text[self.topic][self.part - 1]
                self.level.currentInput = []
                self.level.lastInput = []
                self.level.addDialogBox(choiceBox)
                break

            # Go to
            if self.currentText.startswith('!GT:'):
                splitText = self.currentText.split(':')[1].split('/')
                self.goto(splitText[0], int(splitText[1]))
                break

    def goto(self, topic, part):    # Go to the desired topic and part in the conversation.
        self.topic = topic
        self.part = part
        self.currentText = self.text[topic][part]
        self.textToDisplay = self.currentText
        self.checkForFlags()
        while self.currentText.endswith('!SK:'):
            self.part += 1
            self.currentText = self.text[self.topic][self.part]
            self.textToDisplay = self.currentText
            self.checkForFlags()
        
        # After the flags:
        self.txtSurface = txtToSurface(TXT_TEMPLATE_SURFACE, self.currentText)

    def loadConversation(self, fileName):
        file = txtLoad([fileName], 'r')
        loading = False
        for line in file:
            line = line.strip()
            if line.startswith('END_CONVERSATION'):
                loading = False
            if loading:
                if not line.startswith('!'):
                    self.addTopic(line)
                else:
                    if line.startswith('!setStartTopic'):
                        splitLine = line.split(':')
                        self.startTopic = splitLine[1]
                    elif line.startswith('!setStartPart'):
                        splitLine = line.split(':')
                        self.startPart = int(splitLine[1])
            if line.startswith('LOAD_CONVERSATION'):
                loading = True

        # Once we're done loading
        self.goto(self.startTopic, self.startPart)

    def getSurface(self):
        return self.txtSurface

    def setLevel(self, level):
        self.level = level

    def getCoord(self):
        return (0, 0)

    def takeInput(self, currentInput, lastInput):
        if keyUp('V', currentInput, lastInput):
            self.advance()





class ChoiceBox:
    def __init__(self, line, level):
        print('\n\nCREATING CHOICE BOX\n')
        self.level = level
        self.coord = (0, 256)
        self.surface = None
        self.selected = 0

        # Create the box here
        self.choices = line.split(':')[1].split('/')
        print(self.choices)

        self.choiceNames = []
        for i in self.choices:
            self.choiceNames.append(self.level.conversation.text[i][0])
        print(self.choiceNames)

        self.surface = choiceBoxSurface(self.choiceNames, self.selected)

    def getSurface(self):
        return self.surface

    def getCoord(self):
        return self.coord

    def takeInput(self, currentInput, lastInput):
        # If they pressed up or down, alter the choice box accordingly
        refreshBox = False
        if keyUp('UP', currentInput, lastInput):
            refreshBox = True
            if self.selected > 0:
                self.selected -= 1
            else:
                self.selected = len(self.choices) - 1
                
        if keyUp('DOWN', currentInput, lastInput):
            refreshBox = True
            if self.selected < len(self.choices) - 1:
                self.selected += 1
            else:
                self.selected = 0

        if refreshBox:
            self.surface = choiceBoxSurface(self.choiceNames, self.selected)

        if keyUp('V', currentInput, lastInput):
            # Do something, Taipu
            self.level.conversation.goto(self.choices[self.selected], 1)
            self.level.removeDialogBox(self)
            del self

    def setLevel(self, level):
        self.level = level



testLevel = DummyLevel()

# First: Let's create a Conversation object and make sure it loads properly.
testConversation = Conversation('testConversation.txt', testLevel)
for i in testConversation.text:
    print(i, testConversation.text[i])
print(testConversation.startTopic)
print(testConversation.startPart)

testLevel.setConversation(testConversation)

testLevel.play()



