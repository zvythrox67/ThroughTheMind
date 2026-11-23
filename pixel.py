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

def make_room_bg(room):
    s = pygame.Surface((SW, SH))
    f1, f2 = room.floor
    if room.outdoor:
        s.fill(ui.INDIGO_DK)
        for y in range(0, 76, 2):
            c = (46 + y // 6, 27 + y // 8, 91 + y // 3)
            pygame.draw.rect(s, c, (0, y, SW, 2))
        pygame.draw.circle(s, ui.YELLOW, (400, 28), 15)
        pygame.draw.circle(s, shade(ui.YELLOW, -0.12), (395, 24), 3)
        for sx, sy in ((30, 14), (90, 40), (150, 18), (210, 50), (270, 12), (330, 44), (460, 52), (60, 60), (480, 18)):
            star(s, sx, sy)
        cloud(s, 24, 30, 40)
        cloud(s, 168, 22, 30)
        cloud(s, 300, 36, 36)
        for ty in range(76, SH, 16):
            for tx in range(0, SW, 16):
                pygame.draw.rect(s, f2 if ((tx // 16 + ty // 16) % 2) else f1, (tx, ty, 16, 16))
        for i in range(60):
            gx, gy = (i * 73) % SW, 80 + (i * 41) % (SH - 84)
            pygame.draw.rect(s, shade(f1, 0.25), (gx, gy, 2, 1))
        for tx in range(8, SW, 38):
            pine(s, tx, 96, 38 + (tx % 3) * 4, 26)
        pine(s, 12, 310, 44, 30)
        pine(s, 500, 310, 44, 30)
        return s
    for ty in range(75, SH, 16):
        for tx in range(0, SW, 16):
            pygame.draw.rect(s, f2 if ((tx // 16 + ty // 16) % 2) else f1, (tx, ty, 16, 16))
    wall = room.wall
    pygame.draw.rect(s, wall, (0, 0, SW, 75))
    for bx in range(0, SW, 16):
        pygame.draw.rect(s, shade(wall, 0.06), (bx, 0, 1, 75))
    pygame.draw.rect(s, shade(wall, -0.45), (0, 72, SW, 3))
    pygame.draw.rect(s, shade(wall, 0.25), (0, 70, SW, 2))
    d = room.decor
    if d == "home":
        for wx in (190, 320):
            pygame.draw.rect(s, shade(wall, -0.5), (wx - 2, 12, 34, 38))
            pygame.draw.rect(s, ui.INDIGO_DK, (wx, 14, 30, 34))
            star(s, wx + 8, 24)
            star(s, wx + 22, 36)
            pygame.draw.circle(s, ui.YELLOW, (wx + 22, 24), 4)
            pygame.draw.rect(s, shade(wall, 0.4), (wx + 14, 14, 2, 34))
    elif d == "hall":
        for lx in range(4, SW, 22):
            if 140 <= lx <= 300 or lx > 420:
                pygame.draw.rect(s, ui.VIOLET, (lx, 18, 18, 52))
                pygame.draw.rect(s, shade(ui.VIOLET, -0.4), (lx, 18, 18, 52), 1)
                for vy in (24, 28, 32):
                    pygame.draw.rect(s, shade(ui.VIOLET, -0.4), (lx + 4, vy, 10, 1))
                pygame.draw.rect(s, ui.YELLOW, (lx + 13, 50, 2, 4))
    elif d == "classroom":
        pygame.draw.circle(s, ui.CREAM, (60, 30), 10)
        pygame.draw.circle(s, shade(wall, -0.5), (60, 30), 10, 2)
        pygame.draw.line(s, shade(wall, -0.6), (60, 30), (60, 24), 1)
        pygame.draw.line(s, shade(wall, -0.6), (60, 30), (65, 30), 1)
        for ax, col in ((380, ui.PINK), (400, ui.YELLOW), (420, ui.CORAL)):
            pygame.draw.rect(s, col, (ax, 14, 14, 18))
    elif d == "bathroom":
        for gx in range(0, SW, 12):
            pygame.draw.rect(s, shade(wall, 0.2), (gx, 0, 1, 70))
        for gy in range(0, 70, 12):
            pygame.draw.rect(s, shade(wall, 0.2), (0, gy, SW, 1))
    elif d == "lunch":
        for px_ in range(20, SW, 28):
            c = (ui.PINK, ui.YELLOW, ui.CORAL, ui.BLUE)[(px_ // 28) % 4]
            pygame.draw.polygon(s, c, [(px_, 10), (px_ + 12, 10), (px_ + 6, 24)])
        pygame.draw.line(s, shade(wall, 0.3), (10, 10), (SW - 10, 10), 1)
    elif d == "guidance":
        for bx in range(300, 460, 11):
            col = (ui.PINK, ui.BLUE, ui.YELLOW, ui.GOOD)[(bx // 11) % 4]
            pygame.draw.rect(s, col, (bx, 20 + (bx % 3) * 2, 8, 44))
        pygame.draw.rect(s, shade(wall, -0.5), (296, 62, 168, 4))
        pygame.draw.circle(s, ui.YELLOW, (130, 30), 8)
    elif d == "coffee":
        pygame.draw.rect(s, (30, 20, 50), (330, 12, 110, 46))
        pygame.draw.rect(s, ui.YELLOW, (330, 12, 110, 46), 2)
        for i in range(4):
            pygame.draw.rect(s, ui.CREAM, (340, 20 + i * 9, 40 + (i % 2) * 20, 2))
        for lx in (120, 220, 420):
            pygame.draw.line(s, shade(wall, 0.3), (lx, 0), (lx, 24), 1)
            pygame.draw.circle(s, ui.YELLOW, (lx, 28), 5)
    return s
