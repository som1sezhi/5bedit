import pygame, os
pygame.init()

def load_sprite(name):
    return pygame.image.load(os.path.join('data', 'tiles', name + '.png')).convert_alpha()

def load_bg(name):
    # todo: check if you can also just use convert()
    return pygame.image.load(os.path.join('data', 'bg', name + '.png')).convert()

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
shadows = [load_sprite('shadow_corner'),
           load_sprite('shadow_1side'),
           load_sprite('shadow_2sides'),
           load_sprite('shadow_3sides'),
           load_sprite('shadow_4sides')]


def get_outlines(sides, corners, outline_set):
    o_corner, o_1side, o_2sides, o_3sides, o_4sides = outline_set
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


# check if given tile rep. by ch casts shadows
# (i_off, j_off) is offset of ch FROM tile to be shadow'd
def check_shadows(ch, i_off, j_off):
    mode = tiles[ch].cast_shadows
    if mode == "none": return False # no shadows
    elif mode == "all": return True # all shadows
    else:
        if  i_off != 0 and j_off != 0: return False # if corner, no shadows
        elif mode == "sides": return True # then if sides, yes shadows
        elif mode == "up" and j_off == -1: return True
        elif mode == "right" and i_off == 1: return True
        elif mode == "down" and j_off == 1: return True
        elif mode == "left" and i_off == -1: return True
        else: return True

# for tile properties
class Tile:
    def __init__(self, sprite, outline_mode=0, cast_shadows="none", bg=False, trayicon=None, origin=[0, 0]):
        self.sprite = sprite
        self.outline_mode = outline_mode
        self.cast_shadows = cast_shadows
        self.bg = bg
        if trayicon == None:
            if outline_mode == 1:
                self.tray_icon = sprite.copy()
                self.tray_icon.blit(get_outlines([False]*4, [False]*4, outline_normal), (0, 0))
            elif outline_mode == 2:
                self.tray_icon = sprite.copy()
                self.tray_icon.blit(get_outlines([False]*4, [False]*4, outline_factory), (0, 0))
            else:
                self.tray_icon = sprite
        else:
            self.tray_icon = trayicon
        self.origin = origin

tiles = {}
tiles['.'] = Tile(None)
# walls
tiles['/'] = Tile(load_sprite('wall_red'), outline_mode=1, cast_shadows="all")
tiles['8'] = Tile(load_sprite('wall_green'), outline_mode=1, cast_shadows="all")
tiles['w'] = Tile(load_sprite('wall_purple'), outline_mode=1, cast_shadows="all")
tiles['€'] = Tile(load_sprite('wall_tan'), outline_mode=1, cast_shadows="all")
tiles['²'] = Tile(load_sprite('wall_factorygrey'), outline_mode=2, cast_shadows="all")
tiles['¼'] = Tile(load_sprite('wall_factorydarkgrey'), outline_mode=2, cast_shadows="all")
tiles['¶'] = Tile(load_sprite('wall_factoryyellow'), outline_mode=2, cast_shadows="all")
tiles['º'] = Tile(load_sprite('wall_factoryred'), outline_mode=2, cast_shadows="all")
tiles['/B'] = Tile(load_sprite('wall_yellow'), outline_mode=1, cast_shadows="all")
# bg
tiles['7'] = Tile(load_sprite('bg_red'), bg=True)
tiles['9'] = Tile(load_sprite('bg_green'), bg=True)
tiles['{'] = Tile(load_sprite('bg_purple'), bg=True)
tiles['®'] = Tile(load_sprite('bg_tan'), bg=True)
# hazards
tiles['0'] = Tile(load_sprite('spike_grey'), cast_shadows="all")
tiles['1'] = Tile(pygame.transform.rotate(tiles['0'].sprite, 180), cast_shadows="all")
tiles['2'] = Tile(pygame.transform.rotate(tiles['0'].sprite, 90), cast_shadows="all")
tiles['3'] = Tile(pygame.transform.rotate(tiles['0'].sprite, -90), cast_shadows="all")
# interactive
tiles['Q'] = Tile(load_sprite('lever_yellow'), origin=[4, 0])
tiles[':'] = Tile(load_sprite('wintoken'))

bg = {}
bg[0] = load_bg('0')
bg[2] = load_bg('2')
bg[3] = load_bg('3')
bg[4] = load_bg('4')
bg[9] = load_bg('9')
bg[10] = load_bg('10')
