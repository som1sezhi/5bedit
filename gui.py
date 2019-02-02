import pygame
import sys, os
pygame.init()

class StatusBar:
    def __init__(self, w, h, margin, col, textcol, font, fontsize, text='', rtext=''):
        self.w = w
        self.h = h
        self.margin = margin
        self.color = col # (r, g, b)
        self.textcol = textcol # (r, g, b)
        self.font = pygame.font.SysFont(font, fontsize)

        self.update(text, rtext)
        
    def update(self, text='', rtext=''):
        self.text = text
        self.rtext = rtext
        
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill(self.color)
        
        self.text_render = self.font.render(text, True, textcol, col)
        self.rtext_render = self.font.render(rtext, True, textcol, col)

        self.surface.blit(self.text_render, (self.margin, self.margin))
        self.surface.blit(self.rtext_render, (self.w - (self.margin + self.rtext_render.get_width()), self.margin))
        
    def get_render():
        return self.surface
