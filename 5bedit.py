import pygame
import sys, os
pygame.init()

tile_size = 30
lvl_w, lvl_h = 32, 18
lvl = [['.'] * lvl_h for i in range(lvl_w)]

# sizes of gui elements
stage_w = 32 * tile_size
stage_h = 18 * tile_size
statusbar_w = stage_w
statusbar_h = 20

screen_w = stage_w
screen_h = stage_h + statusbar_h

screen = pygame.display.set_mode([screen_w, screen_h])

current = '/'
bigbrush = False

import tiles
import gui

def bigbrush_place(mxtile, mytile, current):
    if mxtile > 0:
        lvl[mxtile - 1][mytile] = current
        if mytile > 0:
            lvl[mxtile - 1][mytile - 1] = current
        if mytile < lvl_h - 1:
            lvl[mxtile - 1][mytile + 1] = current
    if mytile > 0:
        lvl[mxtile][mytile - 1] = current
    if mxtile < lvl_w - 1:
        lvl[mxtile + 1][mytile] = current
        if mytile > 0:
            lvl[mxtile + 1][mytile - 1] = current
        if mytile < lvl_h - 1:
            lvl[mxtile + 1][mytile + 1] = current
    if mytile < lvl_h - 1:
        lvl[mxtile][mytile + 1] = current

########## initial drawing of gui elements ##########
stage_rect = pygame.Rect(0, 0, stage_w, stage_h)
statusbar = gui.StatusBar(w=statusbar_w, h=statusbar_h, margin=2,
                          col=(100, 100, 100), textcol=(255, 255, 255),
                          font='Courier New', fontsize=12,
                          text='sup', rtext='supper')
statusbar_rect = screen.blit(statusbar.get(), (0, stage_h))

########## draw loop ##########
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
            elif event.key == pygame.K_q: current = '7'
            elif event.key == pygame.K_w: current = '9'
            elif event.key == pygame.K_e: current = '{'
            elif event.key == pygame.K_r: current = '®'

            if event.key == pygame.K_z: bigbrush = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z: bigbrush = False

    ##### mouse stuff #####
    mL, mM, mR = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    mxtile = mx // tile_size
    mytile = my // tile_size
    if stage_rect.collidepoint(mx, my):
        if mL:
            lvl[mxtile][mytile] = current
            if bigbrush:
                bigbrush_place(mxtile, mytile, current)
        elif mR:
            lvl[mxtile][mytile] = '.'
            if bigbrush:
                bigbrush_place(mxtile, mytile, '.')
        elif mM:
            if lvl[mxtile][mytile] != '.':
                current = lvl[mxtile][mytile]

    ##### render the stage #####
    screen.fill((255, 255, 255))
    for i in range(lvl_w):
        for j in range(lvl_h):
            cdraw = lvl[i][j] # char of tile being drawn
            if not(cdraw == '.'): # if not air...
                tile = tiles.tiles[cdraw].sprite.copy() # get sprite
                outline_mode = tiles.tiles[cdraw].outline_mode

                ## outlines ##
                if outline_mode != 0: 
                    # True if same type of tile is present on the sides/corners of current tile
                    # (ensuring valid list indexes only, returning True for OOB "tiles")
                    # order for sides is U, R, D, L
                    # order for corners is LU, RU, RD, LD
                    sides = [lvl[i][j - 1] == cdraw if j - 1 >= 0 else True,
                             lvl[i + 1][j] == cdraw if i + 1 < lvl_w else True,
                             lvl[i][j + 1] == cdraw if j + 1 < lvl_h else True,
                             lvl[i - 1][j] == cdraw if i - 1 >= 0 else True]
                    corners = [lvl[i - 1][j - 1] == cdraw if i - 1 >= 0 and j - 1 >= 0 else True,
                               lvl[i + 1][j - 1] == cdraw if i + 1 < lvl_w and j - 1 >= 0 else True,
                               lvl[i + 1][j + 1] == cdraw if i + 1 < lvl_w and j + 1 < lvl_h else True,
                               lvl[i - 1][j + 1] == cdraw if i - 1 >= 0 and j + 1 < lvl_h else True]
                    if not sides == corners == [True, True, True, True]: # don't bother w/ outlines if surrounded by same tile
                        outline_graphics = tiles.outline_normal if outline_mode == 1 else tiles.outline_factory
                        tile.blit(tiles.get_outlines(sides, corners, outline_graphics), (0, 0))

                ## shadows ##
                if tiles.tiles[cdraw].bg: # put shadows on bg tiles only
                    # True if tile in question casts shadows
                    # same sort of deal as in outlines
                    sides = [tiles.check_shadows(lvl[i][j - 1], 0, 1) if j - 1 >= 0 else False,
                             tiles.check_shadows(lvl[i + 1][j], -1, 0) if i + 1 < lvl_w else False,
                             tiles.check_shadows(lvl[i][j + 1], 0, -1) if j + 1 < lvl_h else False,
                             tiles.check_shadows(lvl[i - 1][j], 1, 0) if i - 1 >= 0 else False]
                    corners = [tiles.check_shadows(lvl[i - 1][j - 1], 1, 1) if i - 1 >= 0 and j - 1 >= 0 else False,
                               tiles.check_shadows(lvl[i + 1][j - 1], -1, 1) if i + 1 < lvl_w and j - 1 >= 0 else False,
                               tiles.check_shadows(lvl[i + 1][j + 1], -1, -1) if i + 1 < lvl_w and j + 1 < lvl_h else False,
                               tiles.check_shadows(lvl[i - 1][j + 1], 1, -1) if i - 1 >= 0 and j + 1 < lvl_h else False]
                    if not sides == corners == [False, False, False, False]: # if there are outlines
                        shadow_graphics = tiles.shadows
                        # invert sides and corners lists to make it work with get_outlines
                        tile.blit(tiles.get_outlines([not i for i in sides], [not i for i in corners], shadow_graphics), (0, 0))
                        
                screen.blit(tile, (i * tile_size, j * tile_size))

    statusbar_rect = screen.blit(statusbar.get(), (0, stage_h))
    pygame.display.flip()
    
