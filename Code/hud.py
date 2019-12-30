# TIOM class for the heads-up-display.

finished = False
print("Loading HUD class...")

import Main
from Main import *

class HUD:
    def __init__(self):
        self.lastActions = None
        self.surface = pygame.surface.Surface((256, 768))
        self.surface.fill((127, 127, 127))

    
    def getSurf(self, source, override=False):
        if source.currentActions != self.lastActions or override: # Only refresh if the source's current set of actions has changed
            actions = source.getCurrentActions()
            iconSurf = pygame.surface.Surface((64, 64))
            finalSurf = pygame.surface.Surface((256, 768))
            iconSurf.fill((255, 0, 255))
            finalSurf.fill((150, 150, 150))
            txtSurf = pygame.surface.Surface((128, 64))
            txtSurf.fill((150, 150, 150))

            pygame.draw.line(iconSurf, (0,0,0), (16, 16), (48-2, 48-2))
            pygame.draw.line(iconSurf, (0,0,0), (16, 48-2), (48-2, 16))

            # Movement
            if actions['V'] != None:
                if actions['V'].color == None:
                    color = V_COLOR
                else:
                    color = actions['V'].color

                if actions['V'].spriteCoord == None:
                    spriteCoord = (0, 0)
                else:
                    spriteCoord = actions['V'].spriteCoord
                    
                v_txtSurf = txtSurf.copy()
                v_txtSurf = txtToSurface(txtSurf, actions['V'].name, DEFAULT_FONT, color)
                finalSurf.blit(v_txtSurf, (160, 64))
                pygame.draw.polygon(iconSurf, color, [(16, 48-1), (32-1, 32), (48-2, 48-1), (32-1, 64-2)])
                iconSurf.blit(ICON_SHEET.getSprite(spriteCoord), (16, 32))

            # Magic
            if actions['M'] != None:
                if actions['M'].color == None:
                    color = M_COLOR
                else:
                    color = actions['M'].color

                if actions['M'].spriteCoord == None:
                    spriteCoord = (1, 0)
                else:
                    spriteCoord = actions['M'].spriteCoord
                    
                m_txtSurf = txtSurf.copy()
                m_txtSurf = txtToSurface(txtSurf, actions['M'].name, DEFAULT_FONT, color)
                finalSurf.blit(m_txtSurf, (160, 0))
                pygame.draw.polygon(iconSurf, color, [(32, 32-1), (48-1, 16), (64-2, 32-1), (48-1, 48-2)])
                iconSurf.blit(ICON_SHEET.getSprite(spriteCoord), (32, 16))

            # Interaction
            if actions['I'] != None:
                if actions['I'].color == None:
                    color = I_COLOR
                else:
                    color = actions['I'].color

                if actions['I'].spriteCoord == None:
                    spriteCoord = (2, 0)
                else:
                    spriteCoord = actions['I'].spriteCoord
                    
                i_txtSurf = txtSurf.copy()
                i_txtSurf = txtToSurface(txtSurf, actions['I'].name, DEFAULT_FONT, color)
                finalSurf.blit(i_txtSurf, (0, 64))
                pygame.draw.polygon(iconSurf, color, [(0, 32-1), (16-1, 16), (32-2, 32-1), (16-1, 48-2)])
                iconSurf.blit(ICON_SHEET.getSprite(spriteCoord), (0, 16))

            # Defense
            if actions['D'] != None:
                if actions['D'].color == None:
                    color = D_COLOR
                else:
                    color = actions['D'].color

                if actions['D'].spriteCoord == None:
                    spriteCoord = (3, 0)
                else:
                    spriteCoord = actions['D'].spriteCoord
                    
                d_txtSurf = txtSurf.copy()
                d_txtSurf = txtToSurface(txtSurf, actions['D'].name, DEFAULT_FONT, color)
                finalSurf.blit(d_txtSurf, (0, 0))
                pygame.draw.polygon(iconSurf, color, [(16, 16-1), (32-1, 0), (48-2, 16-1), (32-1, 32-2)])
                iconSurf.blit(ICON_SHEET.getSprite(spriteCoord), (16, 0))

            iconSurf.set_colorkey((255, 0, 255))
            finalSurf.blit(iconSurf, (96, 32))

            self.surface = finalSurf
            self.lastActions = source.currentActions

        return self.surface


finished = True
print("Done loading HUD class")
