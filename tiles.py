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

def gen_rots(ol):
    olrots = []
    for spr in ol:
        olrots.append([spr,
                       pygame.transform.rotate(spr, -90),
                       pygame.transform.rotate(spr, 180),
                       pygame.transform.rotate(spr, 90)])
    return olrots

olset_normal = gen_rots(outline_normal)
olset_factory = gen_rots(outline_factory)
olset_shadows = gen_rots(shadows)

def get_outlines(sides, corners, ol):
    if sum(sides) == 0: # all 4 sides have outlines
        outlines = ol[4][0]
    elif sum(sides) == 1: # 3 sides have outlines
        for i in range(4):
            if sides[i]:
                outlines = ol[3][i]
                break
    elif sum(sides) == 2: # 2 sides have outlines
        # cover the case where the 2 outlines are opposite each other first
        if (not sides[0]) and (not sides[2]): # =
            outlines = ol[1][0].copy()
            outlines.blit(ol[1][2], (0, 0))
        elif (not sides[1]) and (not sides[3]): # ||
            outlines = ol[1][1].copy()
            outlines.blit(ol[1][3], (0, 0))
        else: # L (rotated some)
            for i in range(4):
                if (not sides[i]) and (not sides[i - 1]):
                    outlines = ol[2][i].copy()
                    if not corners[(i + 2) % 4]:
                        outlines.blit(ol[0][i], (0, 0))
                    break
    elif sum(sides) == 3: # 1 side has outline
        for i in range(4):
            if not sides[i]:
                outlines = ol[1][i].copy()
                if not corners[(i + 2) % 4]:
                    outlines.blit(ol[0][i], (0, 0))
                if not corners[(i + 3) % 4]:
                    outlines.blit(ol[0][(i+1)%4], (0, 0))
                break
    else: # 0 sides, maybe corners
        outlines = pygame.Surface((30, 30), pygame.SRCALPHA)
        outlines.fill((0, 0, 0, 0)) # transparent
        for i in range(4):
            if not corners[i]:
                outlines.blit(ol[0][(i+2)%4], (0, 0))
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
        else: return False

def resize_icon(sprite):
    w, h = sprite.get_size()
    if w > h:
        ws, hs = 30, round(30 * h/w)
    else:
        ws, hs = round(30 * w/h), 30
    # center the icon
    icon = pygame.Surface((30, 30), pygame.SRCALPHA)
    icon.blit(pygame.transform.scale(sprite, (ws, hs)),
                        ((30-ws)//2, (30-hs)//2))
    return icon

# for tile properties
class Tile:
    def __init__(self,
                 sprite,
                 outline_mode=0,
                 cast_shadows="none",
                 bg=False,
                 trayicon=None,
                 origin=(0, 0)):
        self.sprite = sprite
        self.outline_mode = outline_mode
        self.cast_shadows = cast_shadows
        self.bg = bg
        if trayicon == None:
            if outline_mode == 1:
                self.tray_icon = sprite.copy()
                self.tray_icon.blit(get_outlines([False]*4, [False]*4, olset_normal), (0, 0))
            elif outline_mode == 2:
                self.tray_icon = sprite.copy()
                self.tray_icon.blit(get_outlines([False]*4, [False]*4, olset_factory), (0, 0))
            else:
                self.tray_icon = sprite
        elif trayicon == "resize":
              self.tray_icon = resize_icon(sprite)
        else:
              self.tray_icon = trayicon
        self.origin = origin

tiles = {}
tiles['.'] = Tile(pygame.Surface((30, 30), pygame.SRCALPHA))

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
tiles['5'] = Tile(load_sprite('tree_e'), trayicon="resize", origin=(77, 184))

# hazards
tiles['0'] = Tile(load_sprite('spike_grey'), cast_shadows="all")
tiles['1'] = Tile(pygame.transform.rotate(tiles['0'].sprite, 180), cast_shadows="all")
tiles['2'] = Tile(load_sprite('spike_grey_right'), cast_shadows="all")
tiles['3'] = Tile(pygame.transform.rotate(tiles['2'].sprite, 180), cast_shadows="all")
tiles['A'] = Tile(load_sprite('spike_black'), cast_shadows="all")
tiles['B'] = Tile(pygame.transform.rotate(tiles['A'].sprite, 180), cast_shadows="all")
tiles['C'] = Tile(load_sprite('spike_black_right'), cast_shadows="all")
tiles['D'] = Tile(pygame.transform.rotate(tiles['C'].sprite, 180), cast_shadows="all")
tiles['v'] = Tile(load_sprite('spike_ball'), cast_shadows="all")
tiles['='] = Tile(load_sprite('heater'), bg=True)

# interactive/special
tiles['4'] = Tile(load_sprite('exit'), bg=True, trayicon="resize", origin=(30, 90))
tiles[':'] = Tile(load_sprite('wintoken'))

tiles[';'] = Tile(load_sprite('jumppad'), cast_shadows="all")
tiles['<'] = Tile(load_sprite('conveyor'), cast_shadows="sides")
tiles['>'] = Tile(pygame.transform.flip(tiles['<'].sprite, True, False), cast_shadows="sides")
tiles['@'] = Tile(load_sprite('oneway'), cast_shadows="up")
tiles['r'] = Tile(pygame.transform.rotate(tiles['@'].sprite, 90), cast_shadows="left")
tiles['s'] = Tile(pygame.transform.rotate(tiles['@'].sprite, 180), cast_shadows="down")
tiles['e'] = Tile(load_sprite('oneway_rock'), cast_shadows="up")

tiles['Q'] = Tile(load_sprite('lever_yellow'), origin=(4, 0))

bg = {}
bg[0] = load_bg('0')
bg[2] = load_bg('2')
bg[3] = load_bg('3')
bg[4] = load_bg('4')
bg[9] = load_bg('9')
bg[10] = load_bg('10')
