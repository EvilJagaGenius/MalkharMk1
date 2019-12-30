# Config tests.
import pygame, sys
from pygame import *
pygame.init()

KEYBINDS = {}

def getKeybinds():
    configFile = open('config.cfg', 'r')
    for line in configFile:
        line = line.strip()
        splitLine = line.split('~')
        action = splitLine[0]
        binds = splitLine[1].split('|')
        KEYBINDS.update({action:binds})

getKeybinds()
print(KEYBINDS)

def getInput():
    keyPresses = pygame.key.get_pressed()
    inputs = []
    for i in KEYBINDS:
        for j in KEYBINDS[i]:
            if j.startswith('K_'):
                key = int(j.strip('K_'))
                if keyPresses[key]:
                    inputs.append(i)
                    
    return inputs
                

window = pygame.display.set_mode((100, 100), 0, 32)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    inputs = getInput()
    if inputs != []:
        print(inputs)
