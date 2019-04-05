import pygame
import sys, os
pygame.init()

tile_s = 30 # size of tile (px)
lvl_w, lvl_h = 64, 36 # size of lvl
lvl_wpx, lvl_hpx = lvl_w * tile_s, lvl_h * tile_s # size of lvl in px, not tiles
lvl = [['.'] * lvl_h for _ in range(lvl_w)]
lvloverlap = [[{} for _ in range(lvl_h)] for _ in range(lvl_w)]

# sizes of gui elements
stage_w = 32 * tile_s
stage_h = 18 * tile_s
tray_w = 155
tray_h = 255
statusbar_w = stage_w + tray_w
statusbar_h = 20

# surface to display
screen_w = tray_w + stage_w
screen_h = stage_h + statusbar_h
screen = pygame.display.set_mode([screen_w, screen_h])

windowactive = True # false if window is minimized
current = '/'
z_down = False
space_down = False
pan_mL_down = False
#mL, mM, mR = False

updaterects = []
stagehover_urects = []

import tiles
import gui
import saveload

########## initial drawing/setup of gui elements ##########
pygame.display.set_caption('5bedit')
pygame.display.set_icon(gui.load_sprite('windowicon'))

stage = gui.Stage(lvl, lvloverlap, 0, tile_s)
stage_rect = pygame.Rect(tray_w, 0, stage_w, stage_h)

statusbar = gui.StatusBar(w=statusbar_w, h=statusbar_h, margin=2,
                          font='Courier', fontsize=14,
                          text='current tile: \'%s\'' % current, rtext='')
statusbar_rect = screen.blit(statusbar.render(), (0, stage_h))

tiletray = gui.tiletray
tray_rect = screen.blit(tiletray.render(), (0, 0))

screen.blit(stage.render_full(), (stage_rect.x, stage_rect.y))
pygame.draw.rect(screen, (30, 30, 30), (0, 0, tray_w, stage_h))
screen.blit(statusbar.render(), (0, stage_h))
screen.blit(tiletray.render(), (0, 0))
pygame.display.update()

# rect corresponding to tiles in the level
def tile_rect(i, j, rx, ry, rw, rh):
    return pygame.Rect(i*tile_s - stage.cx + stage_rect.left + rx*tile_s,
                       j*tile_s - stage.cy + stage_rect.top + ry*tile_s,
                       rw*tile_s, rh*tile_s)

# place overlapping bits of tile
def place_overlap(i, j, c):
    ox, oy = tiles.tiles[c].origin
    sx, sy = tiles.tiles[c].sprite.get_size()
    lbound = ubound = 0
    rbound = dbound = 1
    if ox != 0:
        lbound = (-ox) // tile_s
        rbound = (sx-ox) // tile_s + 1
    else:
        lbound, rbound = 0, 1
    lb, rb = max(0, i+lbound), min(lvl_w, i+rbound)
    if oy != 0:
        ubound = (-oy) // tile_s
        dbound = (sy-oy) // tile_s + 1
    else:
        ubound, dbound = 0, 1
    ub, db = max(0, j+ubound), min(lvl_h, j+dbound)
    for x in range(lb, rb):
        for y in range(ub, db):
            if (x, y) != (i, j):
                lvloverlap[x][y][(x-i, y-j)] = c
                #print('placed (%d, %d) [%s] at %d, %d' % (x-i, y-j, c, x, y))
    #print('end func call')
    return tile_rect(i, j, lb-i, ub-j, rb-lb, db-ub)

# delete overlapping bits of tile
def del_overlap(i, j, c):
    ox, oy = tiles.tiles[c].origin
    sx, sy = tiles.tiles[c].sprite.get_size()
    lbound = ubound = 0
    rbound = dbound = 1
    if ox != 0:
        lbound = (-ox) // tile_s
        rbound = (sx-ox) // tile_s + 1
    else:
        lbound, rbound = 0, 1
    lb, rb = max(0, i+lbound), min(lvl_w, i+rbound)
    if oy != 0:
        ubound = (-oy) // tile_s
        dbound = (sy-oy) // tile_s + 1
    else:
        ubound, dbound = 0, 1
    ub, db = max(0, j+ubound), min(lvl_h, j+dbound)
    for x in range(lb, rb):
        for y in range(ub, db):
            if (x, y) != (i, j):
                del lvloverlap[x][y][(x-i, y-j)]
                #print('deleted (%d, %d) [%s] at %d, %d' % (x-i, y-j, c, x, y))
    #print('end func call')
    return tile_rect(i, j, lb-i, ub-j, rb-lb, db-ub)
        
def place_tile(i, j, c):
    ur = [] # update rects
    # if overwriting tiles, remove the overlap they make
    if tiles.tiles[lvl[i][j]].origin != (0, 0):
        ur.append(del_overlap(i, j, lvl[i][j]))
    lvl[i][j] = c
    # place overlap
    if tiles.tiles[c].origin != (0,0):
        ur.append(place_overlap(i, j, c))
    return tile_rect(i, j, -1, -1, 3, 3).unionall(ur)
    
def bigbrush_place(mxtile, mytile, current):
    ur = [] # update rects
    if mxtile > 0: # L
        ur.append(place_tile(mxtile - 1, mytile, current))
        if mytile > 0: # LU
            ur.append(place_tile(mxtile - 1, mytile - 1, current))
        if mytile < lvl_h - 1: # LD
            ur.append(place_tile(mxtile - 1, mytile + 1, current))
    if mytile > 0: # U
        ur.append(place_tile(mxtile, mytile - 1, current))
    if mxtile < lvl_w - 1: # R
        ur.append(place_tile(mxtile + 1, mytile, current))
        if mytile > 0: # RU
            ur.append(place_tile(mxtile + 1, mytile - 1, current))
        if mytile < lvl_h - 1: # RD
            ur.append(place_tile(mxtile + 1, mytile + 1, current))
    if mytile < lvl_h - 1: # D
        ur.append(place_tile(mxtile, mytile + 1, current))
    return tile_rect(mxtile, mytile, -1, -1, 3, 3).unionall(ur)

########## draw loop ##########
while 1:
    updaterects = []
    fullstagerender = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: z_down = True
            if event.key == pygame.K_SPACE: space_down = True
            if event.key == pygame.K_s: saveload.save(lvl)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z: z_down = False
            if event.key == pygame.K_SPACE: space_down = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # tray selection
                if tray_rect.collidepoint(*event.pos):
                    tiletray.mouse_select(event.pos[0] - tray_rect.x,
                                          event.pos[1] - tray_rect.y)
                    current = tiletray.get_val()
                    updaterects.append(tray_rect)
                elif stage_rect.collidepoint(*event.pos):
                    pan_mL_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pan_mL_down = False
        elif event.type == pygame.MOUSEMOTION:
            # panning
            if pan_mL_down and space_down:
                stage.cx -= event.rel[0]
                stage.cy -= event.rel[1]
                fullstagerender = True
                # no oob peeking
                if stage.cx < 0: stage.cx = 0
                elif stage.cx > lvl_wpx - stage_w: stage.cx = lvl_wpx - stage_w
                if stage.cy < 0: stage.cy = 0
                elif stage.cy > lvl_hpx - stage_h: stage.cy = lvl_hpx - stage_h

    # default background colour
    # if you see magenta peeking out, something's gone wrong
    screen.fill((255, 0, 255))

    # if window was just unminimized, draw the entire thing again
    if windowactive != pygame.display.get_active():
        if not windowactive:
            fullstagerender = True
        windowactive = pygame.display.get_active()

    # if in the process of panning, update the entire stage screen
    # dont bother checking for interactivity
    if fullstagerender: 
        screen.blit(stage.render_full(), (stage_rect.x, stage_rect.y))
        updaterects.append(stage_rect)

    # weee interactivity
    else:
        ##### mouse dragging stuff #####
        mL, mM, mR = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()

        # stage interactivity
        if stage_rect.collidepoint(mx, my):
            mxlvl = (stage.cx + mx - stage_rect.left) / tile_s
            mylvl = (stage.cy + my - stage_rect.top) / tile_s
            mxtile = int(mxlvl // 1)
            mytile = int(mylvl // 1)
            mtile_rect = tile_rect(mxtile, mytile, 0, 0, 1, 1)
            if not space_down:
                stage_urect = tile_rect(mxtile, mytile, -2, -2, 5, 5)
                ur = [] # update rects
                # paint tiles
                if mL:
                    ur.append(place_tile(mxtile, mytile, current))
                    if z_down:
                        ur.append(bigbrush_place(mxtile, mytile, current))
                # erase tiles
                elif mR:
                    ur.append(place_tile(mxtile, mytile, '.'))
                    if z_down:
                        ur.append(bigbrush_place(mxtile, mytile, '.'))
                stage_urect.unionall_ip(ur)
                stage_urect_stg = stage_urect.move(-stage_rect.left, -stage_rect.top)
                screen.blit(stage.render_part(stage_urect_stg), stage_urect.topleft)
                updaterects.append(stage_urect)
                
                # draw + update the blue hover selection thing
                if len(stagehover_urects) != 1:
                    stagehover_urects = [pygame.Rect(0, 0, tile_s, tile_s)] # default
                screen.blit(stage.render_part(stagehover_urects[0].move(-stage_rect.left, -stage_rect.top)),
                            stagehover_urects[0].topleft)
                if z_down:
                    pygame.draw.rect(screen, (0, 0, 255), tile_rect(mxtile,mytile,-1,-1,3,3), 3)
                    hover_urect = tile_rect(mxtile, mytile, -1.5, -1.5, 4, 4)
                else:
                    pygame.draw.rect(screen, (0, 0, 255), mtile_rect, 3)
                    hover_urect = tile_rect(mxtile, mytile, -0.5, -0.5, 2, 2)
                stagehover_urects.append(hover_urect)
                updaterects.extend(stagehover_urects)
                del stagehover_urects[0]
                
            # if space is down, remove blue hover selection thing
            # the user is probably about to pan
            else:
                if stagehover_urects:
                    screen.blit(stage.render_part(stagehover_urects[0].move(-stage_rect.left, -stage_rect.top)),
                                stagehover_urects[0].topleft)
                    updaterects.extend(stagehover_urects)
                    del stagehover_urects[0]

            # middle-click to tile pick
            if mM:
                if lvl[mxtile][mytile] != '.':
                    current = lvl[mxtile][mytile]
                    tiletray.set_val(current, True)
                    updaterects.append(tray_rect)

            # only update this part if moving around in the stage area
            statusbar.rtext = 'xy: (%.2f, %.2f), tile (%d, %d)' % (mxlvl, mylvl, mxtile, mytile)

    statusbar.text = 'current tile: \'%s\'' % current

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, tray_w, stage_h))
    screen.blit(statusbar.render(), (0, stage_h))
    screen.blit(tiletray.render(), (0, 0))

    updaterects.append(statusbar_rect)

    pygame.display.update(updaterects)
    
