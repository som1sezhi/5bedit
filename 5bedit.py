import sys, pygame
import os
pygame.init()

tsize = 8
lvlw, lvlh = 100, 100
lvl = [['.'] * lvlh for i in range(lvlw)]
lvl[1][1] = '/'
screenw, screenh = lvlw * tsize, lvlh * tsize

screen = pygame.display.set_mode([screenw,screenh])
tile = pygame.transform.scale(pygame.image.load(os.path.join('data', 'tile.png')).convert(), (8, 8))

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
                screen.blit(tile, (i * tsize, j * tsize))
    pygame.display.flip()
    # heck!
    
