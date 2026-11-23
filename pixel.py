import math
import pygame
import ui

SW, SH = ui.W // 2, ui.H // 2
SHADOW = (28, 16, 58)
SKIN = (232, 190, 160)

def shade(c, f):
    if f >= 0:
        return tuple(int(v + (255 - v) * f) for v in c)
    return tuple(int(v * (1 + f)) for v in c)

def box(s, x, y, w, h, col):
    pygame.draw.rect(s, shade(col, -0.55), (x, y, w, h))
    pygame.draw.rect(s, col, (x + 1, y + 1, w - 2, h - 3))
    pygame.draw.rect(s, shade(col, 0.35), (x + 1, y + 1, w - 2, 2))
    pygame.draw.rect(s, shade(col, -0.25), (x + 1, y + h - 3, w - 2, 2))
    
def star(s, x, y, c = ui.YELLOW):
    pygame.draw.rect(s, c, (x, y - 1, 1, 3))
    pygame.draw.rect(s, c, (x - 1, y, 3, 1))
    
def cloud(s, x, y, w=40):
    for i, (ox, r) in enumerate(((0, 6), (10, 9), (22, 7), (32, 5))):
        if ox <= w:
            pygame.draw.circle(s, ui.PINK, (x + ox, y), r)
    pygame.draw.rect(s, ui.PINK, (x, y, w, 6))
    pygame.draw.rect(s, ui.CORAL, (x + 4, y - 4, w // 2, 3))
    pygame.draw.rect(s, ui.BLUE, (x, y + 6, w, 3))


def pine(s, x, base, h=36, w=26):
    for i in range(3):
        top = base - h + i * (h // 4)
        bw = w - (2 - i) * 6
        pts = [(x, top), (x + bw // 2, top + h // 2), (x - bw // 2, top + h // 2)]
        pygame.draw.polygon(s, ui.LAV, pts)
        pygame.draw.polygon(s, ui.LAV_DK, [(x, top), (x - bw // 2, top + h // 2), (x - bw // 6, top + h // 2)])
        pygame.draw.line(s, ui.YELLOW, (x, top), (x + bw // 2, top + h // 2), 1)
    pygame.draw.rect(s, (70, 45, 120), (x - 2, base - 2, 4, 6))
