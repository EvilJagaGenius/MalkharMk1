# TIOM NPC classes.

print('Loading NPC classes...')
finished = False

import Main
from Main import *

class NPC(Entity):
    def __init__(self, file):
        Entity.__init__(self, file)
        self.conversation = Conversation(file)
        
        self.canTalk = True
        self.body = [[0,0,0], [0,0,1]]
        self.visible = True
        self.solid = True

        
        self.direction = (0, 1, 0)

        self.spriteSheet = SpriteSheet('NPCSheet.png', 64, 64, (255, 0, 255))
        self.animations = {'idle':AnimSheet(self.spriteSheet,
                                  {0:(0, 0),
                                   1:'goto:0',
                                   -1:'goto:0'}),
                           'talk':AnimSheet(self.spriteSheet,
                                  {0:(0, 0),
                                   3:(0, 1),
                                   6:'goto:0',
                                   -1:'changeAnim:idle'})}

        self.currentAnim = self.animations['idle']
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))

        self.conversationChanges = []

        

    def setLevel(self, level):
        self.level = level
        self.conversation.setLevel(level)

    def talk(self):
        self.conversation.resetConversation()
        self.level.setConversation(self.conversation)

    
    def frameTick(self):
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))
        if type(self.sprite) == type(''):
            # Do something, Taipu
            #print('self.sprite is a string:  ' + self.sprite)
            if self.sprite.startswith('changeAnim'):
                newAnim = self.sprite.split(':')[1]
                self.changeAnim(newAnim)
        self.currentAnim.frameTick()
        self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))

    

    def changeAnim(self, newAnim): # newAnim is a string, a key in self.animations
        if newAnim in self.animations:
            # Reset current animation
            self.currentAnim.reset()
            # Switch to new animation
            self.currentAnim = self.animations[newAnim]
            self.currentAnim.reset()
            self.sprite = self.currentAnim.getCurrentSprite((calcDirFromVector(self.direction), 0))

    def changeDirection(self, newDirection):
        self.direction = newDirection

print('Done loading NPC classes')
finished = True
