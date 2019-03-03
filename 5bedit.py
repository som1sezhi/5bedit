import pygame
import sys, os
pygame.init()

tile_s = 30 # size of tile (px)
lvl_w, lvl_h = 64, 36 # size of lvl
lvl_wpx, lvl_hpx = lvl_w * tile_s, lvl_h * tile_s # size of lvl in px, not tiles
lvl = [['.'] * lvl_h for i in range(lvl_w)]

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

stage = gui.Stage(lvl, 0, tile_s)
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

# rect corresponding to tiles in the level
def tile_rect(i, j, rx, ry, rw, rh):
    return pygame.Rect(i*tile_s - stage.cx + stage_rect.left + rx*tile_s,
                       j*tile_s - stage.cy + stage_rect.top + ry*tile_s,
                       rw*tile_s, rh*tile_s)

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
                stage_urect_stg = stage_urect.move(-stage_rect.left, -stage_rect.top)
                # paint tiles
                if mL:
                    lvl[mxtile][mytile] = current
                    if z_down:
                        bigbrush_place(mxtile, mytile, current)
                # erase tiles
                elif mR:
                    lvl[mxtile][mytile] = '.'
                    if z_down:
                        bigbrush_place(mxtile, mytile, '.')
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
    
