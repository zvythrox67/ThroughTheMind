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

def text(surf, s, pos, size = 28, color = TEXT, center = False, right = False, shadow = False):
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

def wrap(s, size, width):
    lines = []
    for para in s.split("\n"):
        if para == "":
            lines.append("")
            continue
        cur = ""
        for word in para.split(" "):
            test = word if cur == "" else cur + " " + word
            if text_width(test, size) > width and cur != "":
                lines.append(cur)
                cur = word
            else:
                cur = test
        lines.append(cur)
    return lines

def panel(surf, rect, color=(34, 20, 70, 232), radius=4, border=(142, 105, 230, 255)):
    x, y, w, h = [int(v) for v in rect]
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, w, h), border_radius=radius)
    if border:
        pygame.draw.rect(s, border, (0, 0, w, h), width=3, border_radius=radius)
    surf.blit(s, (x, y))


def tint(surf, color, alpha):
    if alpha <= 0:
        return
    s = pygame.Surface((W, H))
    s.fill(color)
    s.set_alpha(int(max(0, min(255, alpha * 255))))
    surf.blit(s, (0, 0))


def make_scene(color, inner=0.45):
    sw, sh = 128, 80
    s = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for y in range(sh):
        for x in range(sw):
            dx = (x - sw / 2) / (sw / 2)
            dy = (y - sh / 2) / (sh / 2)
            d = math.hypot(dx, dy) / 1.2
            a = 0.0 if d < inner else min(1.0, (d - inner) / (1.0 - inner))
            s.set_at((x, y), (color[0], color[1], color[2], int(255 * a ** 1.5)))
    return pygame.transform.smoothscale(s, (W, H))

def draw_eye(surf, x, y, w, alpha=1.0, tx=None, ty=None):
    hh = w * 0.45
    pts = []
    n = 10
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((int(x - w * math.cos(t)), int(y - hh * math.sin(t))))
    for i in range(n - 1, 0, -1):
        t = math.pi * i / n
        pts.append((int(x - w * math.cos(t)), int(y + hh * math.sin(t))))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    bx, by = min(xs) - 2, min(ys) - 2
    bw, bh = max(xs) - bx + 4, max(ys) - by + 4
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    local = [(px - bx, py - by) for px, py in pts]
    pygame.draw.polygon(s, (255, 255, 255, 255), local)
    pygame.draw.polygon(s, (46, 27, 91, 255), local, 2)
    ox = oy = 0.0
    if tx is not None:
        dx, dy = tx - x, ty - y
        ln = max(1.0, math.hypot(dx, dy))
        ox, oy = dx / ln * w * 0.28, dy / ln * w * 0.28
    pygame.draw.circle(s, (46, 27, 91, 255), (int(x - bx + ox), int(y - by + oy)), max(2, int(hh * 0.85)))
    s.set_alpha(int(max(0.0, min(1.0, alpha)) * 255))
    surf.blit(s, (bx, by))

_sprites = {}

def sprite(name, direction, scale = 1):
    key = (name, direction, scale)
    if key in _sprites:
        return _sprites[key]
    base = os.path.join(HERE, "assets", name)
    img = None
    for p in (os.path.join(base, "Idle", "rotations", direction + ".png"),
              os.path.join(base, "rotations", direction + ".png"),
              os.path.join(base, direction + ".png")):
        if os.path.exists(p):
            img = pygame.image.load(p).convert_alpha()
            break
    if img is None:
        img = pygame.Surface((48, 48), pygame.SRCALPHA)
        col = (60 + (sum(map(ord, name)) * 37) % 160, 160, 120)
        pygame.draw.rect(img, col, (14, 18, 20, 26))
        pygame.draw.circle(img, (235, 200, 170), (24, 12), 8)
    if scale != 1:
        img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
    _sprites[key] = img
    return img

def dir_toward(dx, dy):
    idx = int(round(math.atan2(dy, dx) / (math.pi / 4))) % 8
    return DIRS[idx]