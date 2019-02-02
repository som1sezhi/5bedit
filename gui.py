import pygame
import sys, os
pygame.init()

class StatusBar:
    def __init__(self, w, h, margin, col, textcol, font, fontsize, text='', rtext=''):
        self.w = w
        self.h = h
        self.margin = margin
        self.color = col # (r, g, b)
        self.textcolor = textcol # (r, g, b)
        self.font = pygame.font.SysFont(font, fontsize)

        self.text = text
        self.rtext = rtext
        self.render()
        
    def render(self):
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill(self.color)
        
        self.text_render = self.font.render(self.text, True, self.textcolor, self.color)
        self.rtext_render = self.font.render(self.rtext, True, self.textcolor, self.color)

        self.surface.blit(self.text_render, (self.margin, self.margin))
        self.surface.blit(self.rtext_render, (self.w - (self.margin + self.rtext_render.get_width()), self.margin))

    def get(self):
        return self.surface
