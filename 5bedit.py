import sys, pygame
import os
pygame.init()

tsize = 30
lvlw, lvlh = 32, 18
lvl = [['.'] * lvlh for i in range(lvlw)]
lvl[2][1] = '/'
screenw, screenh = lvlw * tsize, lvlh * tsize

screen = pygame.display.set_mode([screenw,screenh])
current = '/'

import tiles

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: current = '/'
            elif event.key == pygame.K_2: current = '8'
            elif event.key == pygame.K_3: current = 'w'
            elif event.key == pygame.K_4: current = '€'
            elif event.key == pygame.K_5: current = '²'
            elif event.key == pygame.K_6: current = '¼'
            elif event.key == pygame.K_7: current = '¶'
            elif event.key == pygame.K_8: current = 'º'
            elif event.key == pygame.K_9: current = '/B'

    mL, mM, mR = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    mxtile = mx // tsize
    mytile = my // tsize
    if mL:
        lvl[mxtile][mytile] = current
    elif mR:
        lvl[mxtile][mytile] = '.'
    elif mM:
        current = lvl[mxtile][mytile]

    screen.fill((255, 255, 255))
    for i in range(lvlw):
        for j in range(lvlh):
            cdraw = lvl[i][j]
            if not(cdraw == '.'):
                tile = tiles.tiles[cdraw].sprite.copy()
                outline_mode = tiles.tiles[cdraw].outline_mode
                if outline_mode != 0:
                    sides = [lvl[i][j - 1] == cdraw if j - 1 >= 0 else True,
                             lvl[i + 1][j] == cdraw if i + 1 < lvlw else True,
                             lvl[i][j + 1] == cdraw if j + 1 < lvlh else True,
                             lvl[i - 1][j] == cdraw if i - 1 >= 0 else True]
                    corners = [lvl[i - 1][j - 1] == cdraw if i - 1 >= 0 and j - 1 >= 0 else True,
                               lvl[i + 1][j - 1] == cdraw if i + 1 < lvlw and j - 1 >= 0 else True,
                               lvl[i + 1][j + 1] == cdraw if i + 1 < lvlw and j + 1 < lvlh else True,
                               lvl[i - 1][j + 1] == cdraw if i - 1 >= 0 and j + 1 < lvlh else True]
                    if not sides == corners == [True, True, True, True]: # if there are outlines
                        outline_graphics = tiles.outline_normal if outline_mode == 1 else tiles.outline_factory
                        tile.blit(tiles.get_outlines(sides, corners, outline_graphics), (0, 0))
               
                screen.blit(tile, (i * tsize, j * tsize))
    pygame.display.flip()
    
