# TIOM Cutscene class.

finished = False
print('Loading Cutscene class...')

import Main
from Main import *

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

finished = True
print('Done loading Cutscene class')
