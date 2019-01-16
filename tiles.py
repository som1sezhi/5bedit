import pygame, os
pygame.init()

def load_sprite(name):
    return pygame.image.load(os.path.join('data', name + '.png')).convert_alpha()

outline_normal = [load_sprite('outline_corner'),
                  load_sprite('outline_1side'),
                  load_sprite('outline_2sides'),
                  load_sprite('outline_3sides'),
                  load_sprite('outline_4sides')]
outline_factory = [load_sprite('outline_corner_factory'),
                  load_sprite('outline_1side_factory'),
                  load_sprite('outline_2sides_factory'),
                  load_sprite('outline_3sides_factory'),
                  load_sprite('outline_4sides_factory')]



def get_outlines(sides, corners, outline_graphics):
    o_corner, o_1side, o_2sides, o_3sides, o_4sides = outline_graphics
    if sum(sides) == 0: # all 4 sides have outlines
        outlines = o_4sides
    elif sum(sides) == 1: # 3 sides have outlines
        for i in range(4):
            if sides[i]:
                outlines = pygame.transform.rotate(o_3sides, -90 * i)
                break
    elif sum(sides) == 2: # 2 sides have outlines
        # cover the case where the 2 outlines are opposite each other first
        if (not sides[0]) and (not sides[2]): # =
            outlines = o_1side.copy()
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        elif (not sides[1]) and (not sides[3]): # ||
            outlines = pygame.transform.rotate(o_1side, 90)
            outlines.blit(pygame.transform.rotate(outlines, 180), (0, 0))
        else: # L (rotated some)
            for i in range(4):
                if (not sides[i]) and (not sides[i - 1]):
                    outlines = pygame.transform.rotate(o_2sides, -90 * i)
                    if not corners[(i + 2) % 4]:
                        outlines.blit(pygame.transform.rotate(o_corner, -90 * i), (0, 0))
                    break
    elif sum(sides) == 3: # 1 side has outline
        for i in range(4):
            if not sides[i]:
                outlines = pygame.transform.rotate(o_1side, -90 * i)
                if not corners[(i + 2) % 4]:
                    outlines.blit(pygame.transform.rotate(o_corner, -90 * i), (0, 0))
                if not corners[(i + 3) % 4]:
                    outlines.blit(pygame.transform.rotate(o_corner, -90 * i - 90), (0, 0))
                break
    else: # 0 sides, maybe corners
        outlines = pygame.Surface((30, 30), pygame.SRCALPHA)
        outlines.fill((0, 0, 0, 0)) # transparent
        for i in range(4):
            if not corners[i]:
                outlines.blit(pygame.transform.rotate(o_corner, -90 * i + 180), (0, 0))
    return outlines


class Tile:
    def __init__(self, sprite, outline_mode=0):
        self.sprite = sprite
        self.outline_mode = outline_mode
        

tiles = {}
tiles['/'] = Tile(load_sprite('wall_red'), outline_mode=1)
tiles['8'] = Tile(load_sprite('wall_green'), outline_mode=1)
tiles['w'] = Tile(load_sprite('wall_purple'), outline_mode=1)
tiles['€'] = Tile(load_sprite('wall_tan'), outline_mode=1)
tiles['²'] = Tile(load_sprite('wall_factorygrey'), outline_mode=2)
tiles['¼'] = Tile(load_sprite('wall_factorydarkgrey'), outline_mode=2)
tiles['¶'] = Tile(load_sprite('wall_factoryyellow'), outline_mode=2)
tiles['º'] = Tile(load_sprite('wall_factoryred'), outline_mode=2)
tiles['/B'] = Tile(load_sprite('wall_yellow'), outline_mode=1)
