import pygame
import sys, os
pygame.init()

tile_s = 30
lvl_w, lvl_h = 72, 28
lvl_wpx, lvl_hpx = lvl_w * tile_s, lvl_h * tile_s # size of lvl in pixels, not tiles
lvl = [['.'] * lvl_h for i in range(lvl_w)]

# sizes of gui elements
stage_w = 32 * tile_s
stage_h = 18 * tile_s
tray_w = 155
tray_h = 255
statusbar_w = stage_w + tray_w
statusbar_h = 20

screen_w = tray_w + stage_w
screen_h = stage_h + statusbar_h

screen = pygame.display.set_mode([screen_w, screen_h])

current = '/'

z_down = False
space_down = False
#mL, mM, mR = False

updaterects = []

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

########## initial drawing/setup of gui elements ##########
stage = gui.Stage(lvl, tile_s)
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


########## draw loop ##########
while 1:
    updaterects = []
    fullstagerender = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z: z_down = True
            if event.key == pygame.K_SPACE: space_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z: z_down = False
            if event.key == pygame.K_SPACE: space_down = False
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and space_down:
                stage.cx -= event.rel[0]
                stage.cy -= event.rel[1]
                if stage.cx < 0: stage.cx = 0
                elif stage.cx > lvl_wpx - stage_w: stage.cx = lvl_wpx - stage_w
                if stage.cy < 0: stage.cy = 0
                elif stage.cy > lvl_hpx - stage_h: stage.cy = lvl_hpx - stage_h
                fullstagerender = True

    screen.fill((255, 255, 255))
    
    if fullstagerender:
        screen.blit(stage.render_full(), (stage_rect.x, stage_rect.y))
        updaterects.append(stage_rect)
    else:
        ##### mouse stuff #####
        mL, mM, mR = pygame.mouse.get_pressed()
        mx, my = pygame.mouse.get_pos()
        
        if stage_rect.collidepoint(mx, my):
            mxlvl = (stage.cx + mx - stage_rect.left) / tile_s
            mylvl = (stage.cy + my - stage_rect.top) / tile_s
            mxtile = int(mxlvl // 1)
            mytile = int(mylvl // 1)
            if not space_down:
                if mL:
                    lvl[mxtile][mytile] = current
                    if z_down:
                        bigbrush_place(mxtile, mytile, current)
                    mtile_rect = pygame.Rect(mxtile*tile_s - stage.cx + stage_rect.left - 2*tile_s,
                                             mytile*tile_s - stage.cy + stage_rect.top - 2*tile_s,
                                             5*tile_s, 5*tile_s)
                    mtile_rect_stg = pygame.Rect(mtile_rect.x - stage_rect.left,
                                                   mtile_rect.y - stage_rect.top,
                                                   5*tile_s, 5*tile_s)
                    screen.blit(stage.render_part(mtile_rect_stg), (mtile_rect.x, mtile_rect.y))
                    updaterects.append(mtile_rect)
                elif mR:
                    lvl[mxtile][mytile] = '.'
                    if z_down:
                        bigbrush_place(mxtile, mytile, '.')
                    mtile_rect = pygame.Rect(mxtile*tile_s - stage.cx + stage_rect.left - 2*tile_s,
                                             mytile*tile_s - stage.cy + stage_rect.top - 2*tile_s,
                                             5*tile_s, 5*tile_s)
                    mtile_rect_stg = pygame.Rect(mtile_rect.x - stage_rect.left,
                                                   mtile_rect.y - stage_rect.top,
                                                   5*tile_s, 5*tile_s)
                    screen.blit(stage.render_part(mtile_rect_stg), (mtile_rect.x, mtile_rect.y))
                    updaterects.append(mtile_rect)
            if mM:
                if lvl[mxtile][mytile] != '.':
                    current = lvl[mxtile][mytile]
                    tiletray.set_val(current, True)
                    updaterects.append(tray_rect)
            statusbar.rtext = 'xy: (%.2f, %.2f), tile (%d, %d)' % (mxlvl, mylvl, mxtile, mytile)
        elif tray_rect.collidepoint(mx, my):
            if mL:
                tiletray.mouse_select(mx - tray_rect.x, my - tray_rect.y)
                current = tiletray.get_val()
                updaterects.append(tray_rect)

    statusbar.text = 'current tile: \'%s\'' % current

    pygame.draw.rect(screen, (30, 30, 30), (0, 0, tray_w, stage_h))
    screen.blit(statusbar.render(), (0, stage_h))
    screen.blit(tiletray.render(), (0, 0))

    updaterects.append(statusbar_rect)

    pygame.display.update(updaterects)
    
