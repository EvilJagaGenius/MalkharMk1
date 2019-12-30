# TIOM HUD tests.

import pygame, sys, os
from pygame import *
pygame.init()

WX = 256
WY = 128
WINDOW = pygame.display.set_mode((WX, WY), 0, 32)


def imgLoad(pathList): # pathList is a list of files/folders ending in the filename you want.
    filePath = os.path.join(*pathList)
    returnFile = pygame.image.load(filePath)
    return returnFile

def txtToSurface(startSurface, txt, font, color): # This function covers a pygame.Surface with text.
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

ICON_SHEET = SpriteSheet('IconSheet.png', 32, 32, (255, 0, 255))
V_COLOR = (0, 255, 0)
M_COLOR = (255, 0, 0)
I_COLOR = (0, 0, 255)
D_COLOR = (255, 255, 0)
ACTIONS = {'V':(0, 0, 'Movement'), 'M':(1, 0, 'Magic'), 'I':(2, 0, 'Interact'), 'D':(3, 0, 'Defense')}
txtFont = pygame.font.Font(None, 20)




class HUD:
    def __init__(self):
        pass

    def getIconSurf(self, actions):
        iconSurf = pygame.surface.Surface((64, 64))
        finalSurf = pygame.surface.Surface((256, 128))
        iconSurf.fill((255, 0, 255))
        finalSurf.fill((150, 150, 150))
        txtSurf = pygame.surface.Surface((64, 64))
        txtSurf.fill((150, 150, 150))
        v_txtSurf = txtSurf.copy()
        m_txtSurf = txtSurf.copy()
        i_txtSurf = txtSurf.copy()
        d_txtSurf = txtSurf.copy()

        

        # Movement
        v_txtSurf = txtToSurface(txtSurf, actions['V'][2], txtFont, V_COLOR)
        finalSurf.blit(v_txtSurf, (0, 64))
        pygame.draw.polygon(iconSurf, V_COLOR, [(16, 48-1), (32-1, 32), (48-2, 48-1), (32-1, 64-2)])
        iconSurf.blit(ICON_SHEET.getSprite(actions['V']), (16, 32))

        # Magic
        m_txtSurf = txtToSurface(txtSurf, actions['M'][2], txtFont, M_COLOR)
        finalSurf.blit(m_txtSurf, (160, 64))
        pygame.draw.polygon(iconSurf, M_COLOR, [(32, 32-1), (48-1, 16), (64-2, 32-1), (48-1, 48-2)])
        iconSurf.blit(ICON_SHEET.getSprite(actions['M']), (32, 16))

        # Interaction
        i_txtSurf = txtToSurface(txtSurf, actions['I'][2], txtFont, I_COLOR)
        finalSurf.blit(i_txtSurf, (0, 0))
        pygame.draw.polygon(iconSurf, I_COLOR, [(0, 32-1), (16-1, 16), (32-2, 32-1), (16-1, 48-2)])
        iconSurf.blit(ICON_SHEET.getSprite(actions['I']), (0, 16))

        # Defense
        d_txtSurf = txtToSurface(txtSurf, actions['D'][2], txtFont, D_COLOR)
        finalSurf.blit(d_txtSurf, (160, 0))
        pygame.draw.polygon(iconSurf, D_COLOR, [(16, 16-1), (32-1, 0), (48-2, 16-1), (32-1, 32-2)])
        iconSurf.blit(ICON_SHEET.getSprite(actions['D']), (16, 0))

        iconSurf.set_colorkey((255, 0, 255))
        finalSurf.blit(iconSurf, (96, 32))
        

        return finalSurf

hud = HUD()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    WINDOW.fill((150, 150, 150))
    hudSurf = hud.getIconSurf(ACTIONS)
    WINDOW.blit(hudSurf, (0, 0))

    pygame.display.update()
    
