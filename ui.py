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

# Title/bg

def title_background(clean = False):
    p = os.path.join(HERE, "assets", "title.png")
    if os.path.exists(p):
        img = pygame.image.load(p).convert_alpha()
        iw, ih = img.get_size()
        scale = H / float(ih)
        nw = int(iw * scale)
        img = pygame.transform.scale(img, (nw, H))
        bg = pygame.Surface((W, H))
        bg.blit(img, ((W - nw) // 2, 0))
        if clean:
            strip = pygame.Surface((W, 90))
            strip.blit(bg, (0, -170))
            bg.blit(strip, (0, 288))
        return bg
    bg = pygame.Surface((W, H))
    for y in range(H):
        t = y / float(H)
        pygame.draw.line(bg, (int(46 + 40 * t), int(27 + 30 * t), int(91 + 60 * t)), (0, y), (W, y))
    pygame.draw.circle(bg, YELLOW, (470, 70), 40)
    for i in range(40):
        x, y = (i * 193) % W, (i * 71) % 300
        pygame.draw.rect(bg, YELLOW, (x, y, 4, 4))
    for i in range(14):
        x = i * 80
        pygame.draw.polygon(bg, LAV, [(x, H), (x + 40, H - 150 - (i % 3) * 30), (x + 80, H)])
    return bg

# button
class Button:
    def __init__(self, label, rect, on_click, size=34, enabled=True):
        self.label, self.rect, self.on_click, self.size, self.enabled = label, rect, on_click, size, enabled
        self.hover = False

    def contains(self, pos):
        x, y, w, h = self.rect
        return x <= pos[0] <= x + w and y <= pos[1] <= y + h

    def event(self, e):
        if e.type == pygame.MOUSEMOTION:
            self.hover = self.contains(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.enabled and self.contains(e.pos):
            self.on_click()

    def draw(self, surf):
        x, y, w, h = self.rect
        if not self.enabled:
            fill, edge, col = (58, 44, 104), (88, 78, 150), (150, 140, 190)
        elif self.hover:
            fill, edge, col = PINK, YELLOW, WHITE
        else:
            fill, edge, col = LAV_DK, LAV_LT, TEXT
        pygame.draw.rect(surf, INDIGO_DK, (x + 4, y + 6, w, h))
        pygame.draw.rect(surf, fill, (x, y, w, h))
        pygame.draw.rect(surf, edge, (x, y, w, h), 4)
        lines = self.label.split("\n")
        lh = font(self.size).get_height()
        ty = y + (h - lh * len(lines)) // 2
        for ln in lines:
            text(surf, ln, (x + w // 2, ty), self.size, col, center=True)
            ty += lh


class DialogueBox:
    def __init__(self):
        self.cur = None
        self.queue = []
        self.sel = 0
        self.rects = []
        self.cont_rect = None

    def active(self):
        return self.cur is not None

    def say(self, d):
        if self.cur is None:
            self.cur, self.sel = d, 0
        else:
            self.queue.append(d)

    def clear(self):
        self.cur = None
        self.queue = []

    def choose(self, i):
        d = self.cur
        self.cur = None
        if d.choices:
            fn = d.choices[i][1] if i < len(d.choices) else None
        else:
            fn = d.on_close
        if fn:
            fn()
        self.flush()

    def flush(self):
        if self.cur is None and self.queue:
            self.cur, self.sel = self.queue.pop(0), 0

    def event(self, e):
        d = self.cur
        if d is None:
            return
        n = max(1, len(d.choices))
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % n
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % n
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.choose(self.sel)
            elif pygame.K_1 <= e.key <= pygame.K_9 and e.key - pygame.K_1 < len(d.choices):
                self.choose(e.key - pygame.K_1)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if d.choices:
                for i, r in enumerate(self.rects):
                    if r[0] <= e.pos[0] <= r[0] + r[2] and r[1] <= e.pos[1] <= r[1] + r[3]:
                        self.choose(i)
                        return
            elif self.cont_rect:
                r = self.cont_rect
                if r[0] <= e.pos[0] <= r[0] + r[2] and r[1] <= e.pos[1] <= r[1] + r[3]:
                    self.choose(0)
        elif e.type == pygame.MOUSEMOTION and d.choices:
            for i, r in enumerate(self.rects):
                if r[0] <= e.pos[0] <= r[0] + r[2] and r[1] <= e.pos[1] <= r[1] + r[3]:
                    self.sel = i

    def draw(self, surf):
        d = self.cur
        if d is None:
            return
        bw, pad = W - 100, 18
        lines = wrap(d.text, 26, bw - pad * 2)
        lh = 26
        rows = len(d.choices) if d.choices else 1
        h = pad + (28 if d.speaker else 0) + len(lines) * lh + 8 + rows * 38 + pad
        x, y = 50, H - 16 - h
        panel(surf, (x, y, bw, h), (34, 20, 70, 242))
        ty = y + pad
        if d.speaker:
            text(surf, d.speaker, (x + pad, ty), 28, YELLOW)
            ty += 28
        for ln in lines:
            text(surf, ln, (x + pad, ty), 26)
            ty += lh
        ty += 8
        self.rects = []
        self.cont_rect = None
        if d.choices:
            for i, (label, _) in enumerate(d.choices):
                r = (x + pad, ty, bw - pad * 2, 34)
                self.rects.append(r)
                pygame.draw.rect(surf, PINK if i == self.sel else (64, 43, 115), r)
                if i == self.sel:
                    pygame.draw.rect(surf, YELLOW, r, 2)
                text(surf, "%d.  %s" % (i + 1, label), (r[0] + 12, r[1] + 8), 25, WHITE if i == self.sel else TEXT)
                ty += 38
        else:
            r = (x + pad, ty, 210, 34)
            self.cont_rect = r
            pygame.draw.rect(surf, PINK, r)
            pygame.draw.rect(surf, YELLOW, r, 2)
            text(surf, "Continue  (Enter)", (r[0] + 12, r[1] + 8), 25, WHITE)


def bar(surf, x, y, name, v, bad_high=False, width=140):
    text(surf, name, (x, y), 22)
    bx = x + 125
    pygame.draw.rect(surf, (64, 43, 115), (bx, y + 3, width, 13))
    frac = max(0.0, min(1.0, v / 100.0))
    good = 1 - frac if bad_high else frac
    col = GOOD if good > 0.6 else YELLOW if good > 0.35 else BAD
    if frac > 0:
        pygame.draw.rect(surf, col, (bx, y + 3, max(5, int(width * frac)), 13))
    pygame.draw.rect(surf, LAV, (bx, y + 3, width, 13), 2)
    text(surf, "%d%%" % round(v), (bx + width + 8, y), 22)