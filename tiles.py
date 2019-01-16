import pygame, os
pygame.init()

class Tile:
    def __init__(self, sprite, outline_mode=0):
        self.sprite = sprite
        self.outline_mode = outline_mode

outline_corner = pygame.image.load(os.path.join('data', 'outline_corner.png')).convert_alpha()
outline_1side = pygame.image.load(os.path.join('data', 'outline_1side.png')).convert_alpha()
outline_2sides = pygame.image.load(os.path.join('data', 'outline_2sides.png')).convert_alpha()
outline_3sides = pygame.image.load(os.path.join('data', 'outline_3sides.png')).convert_alpha()
outline_4sides = pygame.image.load(os.path.join('data', 'outline_4sides.png')).convert_alpha()
outline_normal = [outline_corner, outline_1side, outline_2sides, outline_3sides, outline_4sides]
outline_corner_factory = pygame.image.load(os.path.join('data', 'outline_corner_factory.png')).convert_alpha()
outline_1side_factory = pygame.image.load(os.path.join('data', 'outline_1side_factory.png')).convert_alpha()
outline_2sides_factory = pygame.image.load(os.path.join('data', 'outline_2sides_factory.png')).convert_alpha()
outline_3sides_factory = pygame.image.load(os.path.join('data', 'outline_3sides_factory.png')).convert_alpha()
outline_4sides_factory = pygame.image.load(os.path.join('data', 'outline_4sides_factory.png')).convert_alpha()
outline_factory = [outline_corner_factory, outline_1side_factory, outline_2sides_factory, outline_3sides_factory, outline_4sides_factory]

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

def t_path(name):
    return os.path.join('data', name + '.png')

tiles = {}
tiles['/'] = Tile(pygame.image.load(t_path('wall_red')).convert(), 1)
tiles['8'] = Tile(pygame.image.load(t_path('wall_green')).convert(), 1)
tiles['w'] = Tile(pygame.image.load(t_path('wall_purple')).convert(), 1)
tiles['€'] = Tile(pygame.image.load(t_path('wall_tan')).convert(), 1)
tiles['²'] = Tile(pygame.image.load(t_path('wall_factorygrey')).convert(), 2)
tiles['¼'] = Tile(pygame.image.load(t_path('wall_factorydarkgrey')).convert(), 2)
tiles['¶'] = Tile(pygame.image.load(t_path('wall_factoryyellow')).convert(), 2)
tiles['º'] = Tile(pygame.image.load(t_path('wall_factoryred')).convert(), 2)
tiles['/B'] = Tile(pygame.image.load(t_path('wall_yellow')).convert(), 1)
