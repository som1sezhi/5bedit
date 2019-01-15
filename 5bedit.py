import sys, pygame
import os
pygame.init()

tsize = 30
lvlw, lvlh = 32, 18
lvl = [['.'] * lvlh for i in range(lvlw)]
lvl[2][1] = '/'
screenw, screenh = lvlw * tsize, lvlh * tsize

screen = pygame.display.set_mode([screenw,screenh])
tile_red = pygame.image.load(os.path.join('data', 'tile_red.png')).convert()

def get_outlines(sides, corners):
    if sum(sides) == 0: # all 4 sides have outlines
        outlines = pygame.image.load(os.path.join('data', '4sides.png')).convert_alpha()
    elif sum(sides) == 4 and sum(corners) == 4: # no outlines at all
        outlines = pygame.Surface((30, 30), pygame.SRCALPHA)
        outlines.fill((0, 0, 0, 0)) # transparent
    elif sum(sides) == 1: # 3 sides have outlines
        for i in range(4):
            if sides[i]:
                outlines = pygame.transform.rotate(pygame.image.load(os.path.join('data', '3sides.png')).convert_alpha(), -90 * i)
                break
    elif sum(sides) == 2: # 2 sides have outlines
        # cover the case where the 2 outlines are opposite each other first
        if (not sides[0]) and (not sides[2]): # =
            outlines = pygame.image.load(os.path.join('data', '1side.png')).convert_alpha()
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        elif (not sides[1]) and (not sides[3]): # ||
            outlines = pygame.transform.rotate(pygame.image.load(os.path.join('data', '1side.png')).convert_alpha(), 90)
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        else: # L (rotated some)
            outlines = pygame.image.load(os.path.join('data', '2sides.png')).convert_alpha()
            corner = pygame.image.load(os.path.join('data', 'corner.png')).convert_alpha()
            for i in range(4):
                if (not sides[i]) and (not sides[i - 1]):
                    outlines = pygame.transform.rotate(outlines, -90 * i)
                    if not corners[(i + 2) % 4]:
                        outlines.blit(pygame.transform.rotate(corner, -90 * i), (0, 0))
                    break
    elif sum(sides) == 3: # 1 side has outline
        outlines = pygame.image.load(os.path.join('data', '1side.png')).convert_alpha()
        corner = pygame.image.load(os.path.join('data', 'corner.png')).convert_alpha()
        for i in range(4):
            if not sides[i]:
                outlines = pygame.transform.rotate(outlines, -90 * i)
                if not corners[(i + 2) % 4]:
                    outlines.blit(pygame.transform.rotate(corner, -90 * i), (0, 0))
                if not corners[(i + 3) % 4]:
                    outlines.blit(pygame.transform.rotate(corner, -90 * i - 90), (0, 0))
                break
    else: # 0 sides, maybe corners
        outlines = pygame.Surface((30, 30), pygame.SRCALPHA)
        outlines.fill((0, 0, 0, 0)) # transparent
        corner = pygame.image.load(os.path.join('data', 'corner.png')).convert_alpha()
        for i in range(4):
            if not corners[i]:
                outlines.blit(pygame.transform.rotate(corner, -90 * i + 180), (0, 0))
    return outlines

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    mL, _, mR = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    mxtile = mx // tsize
    mytile = my // tsize
    if mL:
        lvl[mxtile][mytile] = '/'
    elif mR:
        lvl[mxtile][mytile] = '.'

    screen.fill((255, 255, 255))
    for i in range(lvlw):
        for j in range(lvlh):
            if lvl[i][j] == '/':
                sides = [lvl[i][j - 1] == '/',
                         lvl[i + 1][j] == '/',
                         lvl[i][j + 1] == '/',
                         lvl[i - 1][j] == '/']
                corners = [lvl[i - 1][j - 1] == '/',
                           lvl[i + 1][j - 1] == '/',
                           lvl[i + 1][j + 1] == '/',
                           lvl[i - 1][j + 1] == '/']
                tile = tile_red.copy()
                tile.blit(get_outlines(sides, corners), (0, 0))
                screen.blit(tile, (i * tsize, j * tsize))
    pygame.display.flip()
    
