# Quick thingus to test if game controllers work.
# Make sure you have the controller plugged in before firing it up.

import pygame, sys
from pygame import *
pygame.init()

WX = 100
WY = 100
window = pygame.display.set_mode((WX, WY), 0, 32)

testPad = pygame.joystick.Joystick(0)
testPad.init()
print('Axes: ' + str(testPad.get_numaxes()))


def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == JOYAXISMOTION:
                print('Joystick moving, value = ' + str(event.value))
            elif event.type == JOYHATMOTION:
                print('Hat moving, value = ' + str(event.value))
            elif event.type == JOYBUTTONDOWN:
                print('Button down, button = ' + str(event.button))
            elif event.type == JOYBUTTONUP:
                print('Button up, button = ' + str(event.button))

input('Press ENTER to start the tests.')
main()
