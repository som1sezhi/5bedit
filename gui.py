import pygame
import os
pygame.init()
if __name__ == '__main__':
    pygame.display.set_mode([100, 100])
import tiles

def load_sprite(name):
    return pygame.image.load(os.path.join('data', 'gui', name + '.png')).convert_alpha()

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

        self.color = (90, 90, 90)
        self.color_button = (100, 100, 100)
        self.color_buttondown = (50, 50, 50)
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
            #elif my > (2*margin + self.button_h):
            else:
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
        self.color = (60, 60, 60)
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

tl_walls = ['/','8','w','€','²','¼','¶','º','/B']
tl_bg = ['7','9','{','®']
def get_tile(ch):
    return TrayEntry(tiles.tiles[ch].tray_icon, ch)
el_walls = list(map(get_tile, tl_walls))
el_bg = list(map(get_tile, tl_bg))
c_walls = TrayCategory(el_walls, load_sprite('icon_walls'), 'Walls')
c_bg = TrayCategory(el_bg, load_sprite('icon_bg'), 'BG')
tiletray = Tray(w_entries=4, h_entries=6,
                entry_w=30, entry_h=30,
                margin=10, spacing=5,
                button_h=21,
                catlist=[c_walls, c_bg])
if __name__ == '__main__':
    print(tiletray.w, tiletray.h)
