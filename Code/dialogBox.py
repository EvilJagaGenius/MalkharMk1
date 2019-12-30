# TIOM dialog box class, and some derived classes.

print('Loading DialogBox classes...')
finished = False

import Main
from Main import *

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
            print('Checking for flags...')
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

            # Change direction
            if self.currentText.startswith('!CD:'):
                splitText = self.currentText.split(':')
                self.level.changeDirection(splitText[1], int(splitText[2]), int(splitText[3]), int(splitText[4]))
                self.advance()

            # Remove entity
            if self.currentText.startswith('!RE:'):
                splitText = self.currentText.split(':')
                if splitText[1] == self.level.name:
                    self.level.removeEntity(splitText[2])
                else: # Otherwise write it to the save file's changelog
                    self.level.save.addLevelChange(splitText[1], 'removeEntity~'+splitText[2])
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
            print('Advancing')
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

                    
                    
            



class ChoiceBox(DialogBox):
    def __init__(self, line, level, font=DEFAULT_FONT, color=(255,255,255)):
        DialogBox.__init__(self)
        self.coord = (0, 256)
        self.surface = None
        self.selected = 0
        self.setLevel(level)
        self.font = font
        self.color = color

        # Create the box here
        self.choices = line.split(':')[1].split('/')

        self.choiceNames = []
        for i in self.choices:
            self.choiceNames.append(self.level.conversation.text[i][0])

        self.boxSurface = basicChoiceBoxSurface(self.choiceNames, self.font, self.color)
        self.arrow = self.font.render(' > ', True, self.color)
        
        self.surface = self.boxSurface.copy() # Copy original surface
        arrowCoord = 4 + ((self.font.get_height() + 4) * self.selected) # Calculate arrow position
        self.surface.blit(self.arrow, (0, arrowCoord)) # Blit arrow

    def getSurface(self): # Keeping this here in case I need to override it later
        return self.surface


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
            self.surface = self.boxSurface.copy() # Copy original surface
            arrowCoord = 4 + ((self.font.get_height() + 4) * self.selected) # Calculate arrow position
            self.surface.blit(self.arrow, (0, arrowCoord)) # Blit arrow

        if keyUp('V', currentInput, lastInput):
            # Do something, Taipu
            self.level.conversation.goto(self.choices[self.selected], 1)
            self.level.removeDialogBox(self)
            self.level.flushInput()
            del self


class LevelMenu(DialogBox):
    def __init__(self, level, font=DEFAULT_FONT, color=(255,255,255)):
        DialogBox.__init__(self)
        self.coord = (0, 0)
        self.surface = None
        self.selected = 0
        self.setLevel(level)
        self.font = font
        self.color = color

        self.choices = ['Resume', 'Save Game', 'View Inventory']
        self.choiceNames = self.choices.copy()

        self.boxSurface = basicChoiceBoxSurface(self.choiceNames, self.font, self.color)
        self.arrow = self.font.render(' > ', True, self.color)
        
        self.surface = self.boxSurface.copy() # Copy original surface
        arrowCoord = 4 + ((self.font.get_height() + 4) * self.selected) # Calculate arrow position
        self.surface.blit(self.arrow, (0, arrowCoord)) # Blit arrow

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
            self.surface = self.boxSurface.copy() # Copy original surface
            arrowCoord = 4 + ((self.font.get_height() + 4) * self.selected) # Calculate arrow position
            self.surface.blit(self.arrow, (0, arrowCoord)) # Blit arrow

        if keyUp('V', currentInput, lastInput):
            # Do something, Taipu
            if self.choices[self.selected] == 'Resume':
                pass
            elif self.choices[self.selected] == 'Save Game':
                self.level.save.getLevelChanges(self.level)
                self.level.save.getPlayerChanges(self.level.thingInControl)
                self.level.save.writeToFile()
            elif self.choices[self.selected] == 'View Inventory':
                self.level.thingInControl.inventoryScreen(self.level)
            self.level.removeDialogBox(self)
            self.level.flushInput()
            del self

        if keyUp('MENU', currentInput, lastInput):
            self.level.removeDialogBox(self)
            self.level.flushInput()
            del self




finished = True
print('Done loading DialogBox classes')
