import sys, pygame
import os
pygame.init()

tsize = 30
lvlw, lvlh = 32, 18
lvl = [['.'] * lvlh for i in range(lvlw)]
lvl[2][1] = '/'
screenw, screenh = lvlw * tsize, lvlh * tsize

screen = pygame.display.set_mode([screenw,screenh])
tile_red = pygame.image.load(os.path.join('data', 'wall_red.png')).convert()

outline_corner = pygame.image.load(os.path.join('data', 'outline_corner.png')).convert_alpha()
outline_1side = pygame.image.load(os.path.join('data', 'outline_1side.png')).convert_alpha()
outline_2sides = pygame.image.load(os.path.join('data', 'outline_2sides.png')).convert_alpha()
outline_3sides = pygame.image.load(os.path.join('data', 'outline_3sides.png')).convert_alpha()
outline_4sides = pygame.image.load(os.path.join('data', 'outline_4sides.png')).convert_alpha()


def get_outlines(sides, corners):
    if sum(sides) == 0: # all 4 sides have outlines
        outlines = outline_4sides
    elif sum(sides) == 1: # 3 sides have outlines
        for i in range(4):
            if sides[i]:
                outlines = pygame.transform.rotate(outline_3sides, -90 * i)
                break
    elif sum(sides) == 2: # 2 sides have outlines
        # cover the case where the 2 outlines are opposite each other first
        if (not sides[0]) and (not sides[2]): # =
            outlines = outline_1side.copy()
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        elif (not sides[1]) and (not sides[3]): # ||
            outlines = pygame.transform.rotate(outline_1side, 90)
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        else: # L (rotated some)
            for i in range(4):
                if (not sides[i]) and (not sides[i - 1]):
                    outlines = pygame.transform.rotate(outline_2sides, -90 * i)
                    if not corners[(i + 2) % 4]:
                        outlines.blit(pygame.transform.rotate(outline_corner, -90 * i), (0, 0))
                    break
    elif sum(sides) == 3: # 1 side has outline
        for i in range(4):
            if not sides[i]:
                outlines = pygame.transform.rotate(outline_1side, -90 * i)
                if not corners[(i + 2) % 4]:
                    outlines.blit(pygame.transform.rotate(outline_corner, -90 * i), (0, 0))
                if not corners[(i + 3) % 4]:
                    outlines.blit(pygame.transform.rotate(outline_corner, -90 * i - 90), (0, 0))
                break
    else: # 0 sides, maybe corners
        outlines = pygame.Surface((30, 30), pygame.SRCALPHA)
        outlines.fill((0, 0, 0, 0)) # transparent
        for i in range(4):
            if not corners[i]:
                outlines.blit(pygame.transform.rotate(outline_corner, -90 * i + 180), (0, 0))
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
                sides = [lvl[i][j - 1] == '/' if j - 1 >= 0 else True,
                         lvl[i + 1][j] == '/' if i + 1 < lvlw else True,
                         lvl[i][j + 1] == '/' if j + 1 < lvlh else True,
                         lvl[i - 1][j] == '/' if i - 1 >= 0 else True]
                corners = [lvl[i - 1][j - 1] == '/' if i - 1 >= 0 and j - 1 >= 0 else True,
                           lvl[i + 1][j - 1] == '/' if i + 1 < lvlw and j - 1 >= 0 else True,
                           lvl[i + 1][j + 1] == '/' if i + 1 < lvlw and j + 1 < lvlh else True,
                           lvl[i - 1][j + 1] == '/' if i - 1 >= 0 and j + 1 < lvlh else True]
                tile = tile_red.copy()
                if not sides == corners == [True, True, True, True]: # if not (no outlines)
                    tile.blit(get_outlines(sides, corners), (0, 0))
                screen.blit(tile, (i * tsize, j * tsize))
    pygame.display.flip()
    
