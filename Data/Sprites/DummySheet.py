# Program for quickly making dummy spritesheets.

import pygame
from pygame import *
pygame.init()

spriteX = 0
spriteY = 0
sheetX = 0
sheetY = 0

color1 = (0, 255, 0) # Box color
color2 = (0, 0, 255) # Border color
color3 = (0, 0, 0)   # Font color

sheetName = 'Untitled.png'

# Statements for setting variables:
spriteX = int(input('spriteX: '))
spriteY = int(input('spriteY: '))
sheetX = int(input('sheetX: '))
sheetY = int(input('sheetY: '))
sheetName = input('sheetName: ')

font = pygame.font.Font(None, 14)

sheetSurf = pygame.surface.Surface((sheetX * spriteX, sheetY * spriteY))

# Draw the sheet
for i in range(sheetX):
    for j in range(sheetY):
        spriteSurf = pygame.surface.Surface((spriteX, spriteY))
        spriteSurf.fill(color1)
        pygame.draw.rect(spriteSurf, color2, pygame.rect.Rect(0, 0, spriteX, spriteY), 1)
        spriteSurf.blit(font.render(str((i, j)), False, color3), (1, 1))

        
        sheetSurf.blit(spriteSurf, (i*spriteX, j*spriteY))


pygame.image.save(sheetSurf, sheetName)
