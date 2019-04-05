import pygame
import os
pygame.init()
if __name__ == '__main__':
    pygame.display.set_mode([100, 100])
import tiles

def load_sprite(name):
    return pygame.image.load(os.path.join('data', 'gui', name + '.png')).convert_alpha()

class Stage:
    def __init__(self, lvl, lvloverlap, bg, tile_s):
        assert all(len(i) == len(lvl[0]) for i in lvl) # assert 'rectangular' list
        self.lvl = lvl
        self.lvloverlap = lvloverlap
        self.tile_s = tile_s
        self.lvl_w = len(lvl)
        self.lvl_h = len(lvl[0])
        # stage screen is 32*18 tiles
        self.w = 32 * tile_s
        self.h = 18 * tile_s
        # x, y pos of current camera pos in the level (px)
        self.cx = 0
        self.cy = 0

        self.bg_unsized = tiles.bg[bg]
        self.update_bgsize()
        
        self.fullrect = pygame.Rect(0, 0, self.w, self.h)

    def update_bgsize(self):
        lvl_w = self.lvl_w
        lvl_h = self.lvl_h
        tile_s = self.tile_s
        parallax = tile_s / 3
        if lvl_w / 32 > lvl_h / 18:
            bg_w = 32*tile_s+(lvl_w-32)*parallax
            bg_uncropped = pygame.transform.smoothscale(self.bg_unsized, (int(bg_w), int(bg_w*9/16)))
            bg = pygame.Surface((bg_w, 18*tile_s+(lvl_h-18)*parallax))
        else:
            bg_h = 18*tile_s+(lvl_h-18)*parallax
            bg_uncropped = pygame.transform.smoothscale(self.bg_unsized, (int(bg_h*16/9), int(bg_h)))
            bg = pygame.Surface((32*tile_s+(lvl_w-32)*parallax, bg_h))
        bg_rect = pygame.Rect(0, (bg_uncropped.get_height()-bg.get_height()) // 2, bg.get_width(), bg.get_height())
        bg.blit(bg_uncropped, (0, 0), bg_rect)
        self.bg = bg

    def get_bg_area(self, x, y, w, h): # x and y are coords in-level
        cx = self.cx
        cy = self.cy
        bg = self.bg
        parallax = 1/3
        bg_area = pygame.Surface((w, h))
        area = pygame.Rect(int(cx*parallax + (x-cx)),
                           int(cy*parallax + (y-cy)),
                           w, h)
        bg_area.blit(bg, (0, 0), area)
        return bg_area

    def render_tile(self, i, j):
        lvl = self.lvl
        lvl_w = self.lvl_w
        lvl_h = self.lvl_h
        
        cdraw = lvl[i][j] # char of this tile
        if tiles.tiles[cdraw].origin != (0,0):
            tile = pygame.Surface((self.tile_s, self.tile_s), pygame.SRCALPHA)
            ox, oy = tiles.tiles[cdraw].origin
            tile.blit(tiles.tiles[cdraw].sprite, (-ox, -oy))
        else:
            tile = tiles.tiles[cdraw].sprite.copy() # get sprite
        ol_mode = tiles.tiles[cdraw].outline_mode

        ### outlines ###
        if ol_mode != 0: 
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
                olset = tiles.olset_normal if ol_mode == 1 else tiles.olset_factory
                tile.blit(tiles.get_outlines(sides, corners, olset), (0, 0))

        ### parts of other tiles overlapping this one ###
        shadow_from_overlap = False
        if self.lvloverlap[i][j]:
            for xoff, yoff in self.lvloverlap[i][j]:
                tileoverlap = tiles.tiles[self.lvloverlap[i][j][(xoff, yoff)]]
                xoff_px = -tileoverlap.origin[0] - xoff*self.tile_s
                yoff_px = -tileoverlap.origin[1] - yoff*self.tile_s
                tile.blit(tileoverlap.sprite, (xoff_px, yoff_px))
                shadow_from_overlap = tileoverlap.bg

        ### shadows ###
        if tiles.tiles[cdraw].bg or shadow_from_overlap: # put shadows on bg tiles only (incl overlap bg)
            # True if tile in question casts shadows
            # same sort of deal as in outlines
            chkshdw = tiles.check_shadows
            sides = [chkshdw(lvl[i][j - 1], 0, 1) if j - 1 >= 0 else False,
                     chkshdw(lvl[i + 1][j], -1, 0) if i + 1 < lvl_w else False,
                     chkshdw(lvl[i][j + 1], 0, -1) if j + 1 < lvl_h else False,
                     chkshdw(lvl[i - 1][j],1, 0) if i - 1 >= 0 else False]
            corners = [chkshdw(lvl[i - 1][j - 1], 1, 1) if i - 1 >= 0 and j - 1 >= 0 else False,
                       chkshdw(lvl[i + 1][j - 1], -1, 1) if i + 1 < lvl_w and j - 1 >= 0 else False,
                       chkshdw(lvl[i + 1][j + 1], -1, -1) if i + 1 < lvl_w and j + 1 < lvl_h else False,
                       chkshdw(lvl[i - 1][j + 1], 1, -1) if i - 1 >= 0 and j + 1 < lvl_h else False]
            if not sides == corners == [False, False, False, False]: # if there are outlines
                shdwset = tiles.olset_shadows
                # invert sides and corners lists to make it work with get_outlines
                tile.blit(tiles.get_outlines([not i for i in sides], [not i for i in corners], shdwset), (0, 0))
        
        return tile

    def render_part(self, rect):
        cx = self.cx
        cy = self.cy
        w = self.w
        h = self.h
        lvl = self.lvl
        lvloverlap = self.lvloverlap
        lvl_w = self.lvl_w
        lvl_h = self.lvl_h
        tile_s = self.tile_s
        render = self.get_bg_area(cx+rect.x, cy+rect.y, rect.w, rect.h)

        lb, rb = max(0, (cx+rect.x)//tile_s), min(self.lvl_w, (cx+rect.x+rect.w)//tile_s + 1)
        tb, bb = max(0, (cy+rect.y)//tile_s), min(self.lvl_h, (cy+rect.y+rect.h)//tile_s + 1)
        for i in range(lb, rb):
            for j in range(tb, bb):
                if (lvl[i][j] != '.') or lvloverlap[i][j]: # if not air or there's smth overlapping
                    render.blit(self.render_tile(i, j), (i * tile_s - cx - rect.x,
                                                    j * tile_s - cy - rect.y))
        return render
        
    def render_full(self):
        cx = self.cx
        cy = self.cy
        w = self.w
        h = self.h
        lvl = self.lvl
        lvloverlap = self.lvloverlap
        lvl_w = self.lvl_w
        lvl_h = self.lvl_h
        tile_s = self.tile_s
        render = self.get_bg_area(cx, cy, w, h)
        
        lb, rb = max(0, cx//tile_s), min(lvl_w, (cx+w)//tile_s + 1)
        tb, bb = max(0, cy//tile_s), min(lvl_h, (cy+h)//tile_s + 1)
        for i in range(lb, rb):
            for j in range(tb, bb):
                if (lvl[i][j] != '.') or lvloverlap[i][j]: # if not air or there's smth overlapping
                    render.blit(self.render_tile(i, j), ((i - cx // tile_s) * tile_s - (cx % tile_s),
                                                    (j - cy // tile_s) * tile_s - (cy % tile_s)))
        return render

class TrayEntry:
    def __init__(self, sprite, val):
        self.sprite = sprite
        self.val = val

class TrayCategory:
    def __init__(self, entrylist, icon, name):
        self.entries = entrylist
        self.icon = icon
        self.name = name
        self.page = 0

class Tray:
    def __init__(self, w_entries, h_entries, entry_w, entry_h, margin, spacing, button_h, catlist):
        self.w_entries, self.h_entries = w_entries, h_entries
        self.entry_w, self.entry_h = entry_w, entry_h
        self.margin = margin
        self.spacing = spacing
        self.button_h = button_h
        self.cat = catlist

        self.color = (37, 37, 37)
        self.color_button = (45, 45, 45)
        self.color_buttondown = (10, 10, 10)
        self.color_selected = (255, 255, 0)

        self.w = 2*margin + (w_entries-1)*spacing + w_entries*entry_w
        self.h = 3*margin + button_h + (h_entries-1)*spacing + h_entries*entry_h
        self.button_w = (self.w - 2*margin - (len(catlist)-1)*spacing) // len(catlist)

        self.curr_cat = 0
        self.curr_pg = 0
        self.selected = (0, 0)
        self.pg_size = w_entries * h_entries

        self.buttons = []
        for c in catlist:
            self.buttons.append([self.render_button(c.icon), self.render_button(c.icon, True)])
        
    def render_button(self, icon, down=False):
        button = pygame.Surface((self.button_w, self.button_h))
        if down: button.fill(self.color_buttondown)
        else: button.fill(self.color_button)
        icon_x = int((self.button_w - icon.get_width()) / 2)
        icon_y = int((self.button_h - icon.get_height()) / 2)
        button.blit(icon, (icon_x, icon_y))
        return button

    def render(self):
        render = pygame.Surface((self.w, self.h))
        render.fill(self.color)
        # render buttons 
        for i in range(len(self.cat)):
            render.blit(self.buttons[i][i == self.curr_cat],
                        (self.margin + i * (self.spacing + self.button_w), self.margin))
        # render all the entries
        for i in range(self.curr_pg*self.pg_size, min((self.curr_pg+1)*self.pg_size, len(self.cat[self.curr_cat].entries))):
            render.blit(self.cat[self.curr_cat].entries[i].sprite,
                        (self.margin + (i%self.w_entries) * (self.spacing+self.entry_w),
                         2*self.margin + self.button_h + (i//self.w_entries%self.h_entries) * (self.spacing+self.entry_h)))
        # draw selected box
        if self.selected[0] == self.curr_cat and self.selected[1] // self.pg_size == self.curr_pg:
            selected_rect = pygame.Rect(self.margin + (self.selected[1]%self.w_entries) * (self.spacing+self.entry_w),
                               2*self.margin + self.button_h + (self.selected[1]//self.w_entries%self.h_entries) * (self.spacing+self.entry_h),
                               self.entry_w, self.entry_h)
            pygame.draw.rect(render, self.color_selected, selected_rect, 3)
        return render

    def mouse_select(self, mx, my):
        margin = self.margin # screw this
        # don't bother if not within margins
        if (margin < mx < (self.w - margin)) and (margin < my < (self.h - margin)):
            # category buttons
            if my < (margin + self.button_h):
                # not in spaces between buttons?
                if (mx - margin) % (self.button_w + self.spacing) < self.button_w:
                    # set cat
                    self.curr_cat = (mx - margin) // (self.button_w + self.spacing)
                    
            # tray of entries
            elif my >= (2*margin + self.button_h):
                # not in the spaces?
                if ((mx - margin) % (self.entry_w + self.spacing) < self.entry_w and
                    (my - 2*margin - self.button_h) % (self.entry_h + self.spacing) < self.entry_h):
                    entcol = (mx - margin) // (self.entry_w + self.spacing)
                    entrow = (my - 2*margin - self.button_h) // (self.entry_h + self.spacing)
                    ent = (self.curr_pg * self.pg_size) + (entrow * self.w_entries + entcol)
                    if ent < len(self.cat[self.curr_cat].entries):
                        self.selected = (self.curr_cat, ent)

    def get_val(self):
        return self.cat[self.selected[0]].entries[self.selected[1]].val

    def set_val(self, val, go_to_pg):
        for i in range(len(self.cat)):
            vallist = [e.val for e in self.cat[i].entries]
            if val in vallist:
                self.selected = (i, vallist.index(val))
                if go_to_pg:
                    self.curr_cat = i
                    self.curr_pg = self.selected[1] // self.pg_size

class StatusBar:
    def __init__(self, w, h, margin, font, fontsize, text='', rtext=''):
        self.w = w
        self.h = h
        self.margin = margin
        self.color = (20, 20, 20)
        self.textcolor = (255, 255, 255)
        self.font = pygame.font.SysFont(font, fontsize)

        self.text = text
        self.rtext = rtext
        self.render()
        
    def render(self):
        render = pygame.Surface((self.w, self.h))
        render.fill(self.color)
        
        text_render = self.font.render(self.text, True, self.textcolor, self.color)
        rtext_render = self.font.render(self.rtext, True, self.textcolor, self.color)

        render.blit(text_render, (self.margin, self.margin))
        render.blit(rtext_render, (self.w - (self.margin + rtext_render.get_width()), self.margin))
        return render

##tl_walls = ['/','8','w','€','²','¼','¶','º','/B']
##tl_bg = ['7','9','{','®',
##         '5']
##tl_hazards = ['0', '1', '2', '3']
##tl_interact = ['4', ';', 'Q', ':']
tl_walls = []
tl_bg = []
tl_hazards = []
tl_interact = []

# feed tiles (in order of being defined) into categories automatically so i dont have to
cu = '' # which category to stick them into
for ch in tiles.tiles:
    if ch == '/': cu = 'walls'
    elif ch == '7': cu = 'bg'
    elif ch == '0': cu = 'hazards'
    elif ch == '4': cu = 'interact'
    if cu == 'walls': tl_walls.append(ch)
    elif cu == 'bg': tl_bg.append(ch)
    elif cu == 'hazards': tl_hazards.append(ch)
    elif cu == 'interact': tl_interact.append(ch)
def get_tile(ch):
    return TrayEntry(tiles.tiles[ch].tray_icon, ch)
el_walls = list(map(get_tile, tl_walls))
el_bg = list(map(get_tile, tl_bg))
el_hazards = list(map(get_tile, tl_hazards))
el_interact = list(map(get_tile, tl_interact))
c_walls = TrayCategory(el_walls, load_sprite('icon_walls'), 'Walls')
c_bg = TrayCategory(el_bg, load_sprite('icon_bg'), 'BG')
c_hazards = TrayCategory(el_hazards, load_sprite('icon_hazards'), 'BG')
c_interact = TrayCategory(el_interact, load_sprite('icon_interact'), 'BG')
tiletray = Tray(w_entries=4, h_entries=6,
                entry_w=30, entry_h=30,
                margin=10, spacing=5,
                button_h=21,
                catlist=[c_walls, c_bg, c_hazards, c_interact])
if __name__ == '__main__':
    print(tiletray.w, tiletray.h)
