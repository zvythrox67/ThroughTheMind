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

#objects
def draw_obj(s, o, t):
    x, y, w, h = o.x // 2, o.y // 2, o.w // 2, o.h // 2
    k, c = o.kind, o.color
    if k == "npcs":
        return
    if k == "door":
        pygame.draw.rect(s, (30, 16, 56), (x - 1, y - 1, w + 2, h + 2))
        pygame.draw.rect(s, shade((150, 100, 90), -0.1), (x + 1, y + 1, w - 2, h - 2))
        pygame.draw.rect(s, (110, 70, 80), (x + 3, y + 3, w - 6, h - 6), 1)
        pygame.draw.rect(s, ui.YELLOW, (x + w - 8, y + h // 2, 3, 3))
        return
    box(s, x, y, w, h, c)
    if k == "bed":
        pygame.draw.rect(s, shade(c, 0.15), (x + 20, y + 4, w - 24, h - 9))
        pygame.draw.rect(s, shade(c, -0.25), (x + 20, y + h // 2, w - 24, 2))
        pygame.draw.rect(s, ui.CREAM, (x + 4, y + 6, 14, h - 16))
        pygame.draw.rect(s, shade(ui.CREAM, -0.2), (x + 4, y + h - 12, 14, 2))
    elif k == "table":
        pygame.draw.rect(s, shade(c, 0.18), (x + 3, y + 5, w - 6, h - 12))
        for px_ in (x + w // 4, x + 3 * w // 4):
            pygame.draw.circle(s, ui.CREAM, (px_, y + h // 2 - 2), 4)
        pygame.draw.rect(s, shade(c, -0.6), (x + 2, y + h - 3, 3, 3))
        pygame.draw.rect(s, shade(c, -0.6), (x + w - 5, y + h - 3, 3, 3))
    elif k == "desk":
        pygame.draw.rect(s, ui.BLUE, (x + 5, y + 5, 12, 8))
        pygame.draw.rect(s, ui.CREAM, (x + 19, y + 6, 10, 7))
        if w > 50:
            pygame.draw.rect(s, ui.YELLOW, (x + w - 12, y + 5, 4, 4))
    elif k == "bus":
        pygame.draw.rect(s, ui.CORAL, (x + 1, y + h // 2, w - 2, 3))
        for i in range(4):
            pygame.draw.rect(s, ui.INDIGO_DK, (x + 8 + i * 22, y + 8, 16, 14))
            pygame.draw.rect(s, ui.BLUE, (x + 9 + i * 22, y + 9, 14, 12))
        for wxx in (x + 14, x + w - 22):
            pygame.draw.circle(s, (30, 16, 56), (wxx + 4, y + h - 2), 6)
            pygame.draw.circle(s, ui.LAV_LT, (wxx + 4, y + h - 2), 2)
        pygame.draw.rect(s, ui.CREAM, (x + w - 5, y + 4, 4, 6))
    elif k == "bench":
        for i in range(1, 3):
            pygame.draw.rect(s, shade(c, -0.35), (x + 2, y + i * (h // 3), w - 4, 1))
    elif k == "counter":
        pygame.draw.rect(s, shade(c, 0.2), (x + 2, y + 3, w - 4, 5))
        pygame.draw.rect(s, ui.CREAM, (x + w - 26, y + 6, 10, 8))
        for tx in range(x + 8, x + w - 40, 22):
            pygame.draw.rect(s, ui.CREAM, (tx, y + 6, 14, 8))
            pygame.draw.rect(s, ui.PINK, (tx + 3, y + 8, 4, 4))
    elif k == "whiteboard":
        for i in range(3):
            pygame.draw.rect(s, (150, 140, 190), (x + 8, y + 5 + i * 5, w - 30 - i * 20, 1))
    elif k == "stall":
        pygame.draw.rect(s, shade(c, -0.3), (x + 6, y + 6, w - 12, h - 12), 1)
        pygame.draw.rect(s, shade(c, -0.3), (x + w // 2, y + 6, 1, h - 12))
        pygame.draw.rect(s, ui.YELLOW, (x + w // 2 - 6, y + h // 2, 3, 3))
    elif k == "sofa":
        pygame.draw.rect(s, shade(c, 0.18), (x + 3, y + 3, w - 6, h // 2))
        pygame.draw.rect(s, shade(c, -0.25), (x + w // 2, y + 3, 1, h // 2))
        pygame.draw.rect(s, shade(c, -0.35), (x, y + 2, 3, h - 4))
        pygame.draw.rect(s, shade(c, -0.35), (x + w - 3, y + 2, 3, h - 4))
    elif k == "sinks":
        for sx in (x + 8, x + w - 26):
            pygame.draw.ellipse(s, (150, 150, 200), (sx, y + 6, 18, 12))
            pygame.draw.rect(s, ui.YELLOW, (sx + 8, y + 3, 2, 3))

def draw_adult(s, fx, fy, kind):
    cols = {"teacher": ((90, 60, 50), ui.BLUE), "counselor": ((60, 40, 90), ui.GOOD), "barista": ((200, 120, 80), ui.PINK)}
    hair, shirt = cols.get(kind, ((60, 50, 80), ui.LAV))
    pygame.draw.ellipse(s, SHADOW, (fx - 9, fy - 3, 18, 6))
    pygame.draw.rect(s, (52, 42, 96), (fx - 6, fy - 13, 12, 13))
    pygame.draw.rect(s, shade(shirt, -0.5), (fx - 9, fy - 30, 18, 18))
    pygame.draw.rect(s, shirt, (fx - 8, fy - 29, 16, 16))
    pygame.draw.rect(s, shade(shirt, 0.3), (fx - 8, fy - 29, 16, 2))
    pygame.draw.rect(s, SKIN, (fx - 5, fy - 40, 10, 10))
    pygame.draw.rect(s, hair, (fx - 6, fy - 42, 12, 5))
    pygame.draw.rect(s, (30, 16, 56), (fx - 3, fy - 36, 1, 2))
    pygame.draw.rect(s, (30, 16, 56), (fx + 2, fy - 36, 1, 2))