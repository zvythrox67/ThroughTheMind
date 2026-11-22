import math
import os
import pygame

W, H = 1024, 640
HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = ["east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"]
HERO = "miku"

INDIGO_DK = (46, 27, 91)
INDIGO = (64, 43, 115)
VIOLET = (88, 78, 177)
LAV = (142, 105, 230)
LAV_DK = (115, 83, 187)
LAV_LT = (157, 120, 210)
PINK = (251, 107, 162)
CORAL = (255, 152, 154)
BLUE = (86, 97, 211)
YELLOW = (250, 229, 114)
CREAM = (255, 243, 196)
TEXT = (245, 238, 255)
GOLD = YELLOW
WHITE = (255, 255, 255)
GOOD = (120, 222, 178)
BAD = (255, 120, 140)
BTN, BTN_HOVER = LAV_DK, LAV

_fonts = {}


def font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(None, size)
        _fonts[size] = f
    return f

def text(surf, s, pos, size = 28, color = TEXT, center = False, right = FALSE, shadow = FALSE):
    if s == "":
        return 0, 0
    img = font(size).render(s, True, color)
    w, h = img.get_size()
    x, y = pos
    if center:
        x -= w // 2
    elif right:
        x -= w
    if shadow:
        sh = font(size).render(s, True, INDIGO_DK)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2)):
            surf.blit(sh, (x + ox, y + oy))
    surf.blit(img, (x, y))
    return w, h

def text_width(s, size):
    return font(size).size(s)[0]


