import math
import random

import pygame
import ui
from ui import W, H, text, panel
from game import THOUGHTS

class MiniGame:
    title = ""
    help = ""

    def __init__(self):
        self.done = False
        self.result = None
        self.ready = 2.2
        self.t = 0.0
        self.rng = random.Random()

    def finish(self, result):
        self.done = True
        self.result = result

    def event(self, e):
        pass

    def update(self, dt):
        if self.ready > 0:
            self.ready -= dt
            return
        self.t += dt
        self.step(dt)

    def step(self, dt):
        pass

    def draw(self, surf):
        self.render(surf)
        if self.ready > 0:
            ui.tint(surf, (20, 8, 48), 0.6)
            panel(surf, (112, 200, 800, 230), (34, 20, 70, 250))
            text(surf, self.title, (W // 2, 222), 56, ui.YELLOW, center=True)
            for i, ln in enumerate(ui.wrap(self.help, 30, 740)):
                text(surf, ln, (W // 2, 292 + i * 30), 30, center=True)
            text(surf, "Get ready...", (W // 2, 386), 28, ui.LAV_LT, center=True)

    def render(self, surf):
        pass

    def axis(self, neg, pos):
        k = pygame.key.get_pressed()
        return (1 if any(k[p] for p in pos) else 0) - (1 if any(k[n] for n in neg) else 0)

class BreathingGame(MiniGame):
    title = "Breathe"
    help = "Breathe in as the ring closes. Press SPACE when it meets the circle."
    ROUNDS = 5

    def __init__(self, params=None):
        super().__init__()
        params = params or {}
        sev = params.get("sev", 1.0)
        self.period = 3.2 - 0.3 * (sev - 0.7) - (0.5 if params.get("panic") else 0)
        self.window = max(12, 18 - 3 * (sev - 0.7))
        self.panic = params.get("panic", False)
        if self.panic:
            self.title = "Panic: slow your breathing"
        self.round, self.score, self.pressed = 0, 0, False
        self.msg, self.msg_t = "", 0.0

    def ring(self):
        return 220 - 160 * (self.t / self.period)

    def event(self, e):
        if self.ready > 0 or self.done:
            return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not self.pressed:
            self.pressed = True
            if abs(self.ring() - 60) <= self.window:
                self.score += 1
                self.msg = "Good"
            else:
                self.msg = "Off. Slow down."
            self.msg_t = 1.0

    def step(self, dt):
        self.msg_t -= dt
        if self.t >= self.period:
            if not self.pressed:
                self.msg, self.msg_t = "Missed. Breathe with the ring.", 1.0
            self.round += 1
            self.t = 0.0
            self.pressed = False
            if self.round >= self.ROUNDS:
                self.finish({"score": self.score})

    def render(self, surf):
        surf.fill(ui.INDIGO_DK)
        for i in range(30):
            pygame.draw.rect(surf, ui.YELLOW, ((i * 197) % W, (i * 89) % H, 3, 3))
        text(surf, "Breath %d of %d" % (min(self.round + 1, self.ROUNDS), self.ROUNDS), (W // 2, 90), 40, center=True)
        cx, cy = W // 2, H // 2 + 20
        pygame.draw.circle(surf, ui.PINK, (cx, cy), 60, 5)
        r = int(max(10, self.ring()))
        pygame.draw.circle(surf, ui.CREAM, (cx, cy), r, 6)
        if self.msg_t > 0:
            text(surf, self.msg, (cx, H - 100), 44, ui.YELLOW, center=True)

class FocusGame(MiniGame):
    title = "Stay focused"
    help = "Move with A / D or the arrow keys. Catch the green answers. Dodge the pink worry clouds."

    def __init__(self, params):
        super().__init__()
        sev = params.get("sev", 1.0)
        self.exam = params.get("exam", False)
        if self.exam:
            self.title = "The big exam"
        self.duration = 28.0 if self.exam else 24.0
        self.cloud_p = min(0.8, 0.26 + 0.35 * params.get("worry", 50) / 100 + 0.09 * (sev - 0.7) + (0.08 if self.exam else 0))
        self.fall = 0.85 + 0.2 * sev
        self.px = W / 2
        self.items = []
        self.spawn = 0.0
        self.good = self.good_total = self.hits = 0
        self.stun = self.flash = 0.0
        self.facing = "east"

    def step(self, dt):
        dx = self.axis((pygame.K_a, pygame.K_LEFT), (pygame.K_d, pygame.K_RIGHT))
        if dx:
            self.facing = "east" if dx > 0 else "west"
        speed = 340 * (0.45 if self.stun > 0 else 1.0)
        self.px = max(80, min(W - 80, self.px + dx * speed * dt))
        self.stun = max(0.0, self.stun - dt)
        self.flash = max(0.0, self.flash - dt)
        self.spawn -= dt
        if self.spawn <= 0 and self.t < self.duration - 2.5:
            self.spawn = 0.55
            cloud = self.rng.random() < self.cloud_p
            if not cloud:
                self.good_total += 1
            self.items.append({"x": self.rng.uniform(80, W - 80), "y": -30.0,
                               "vy": (self.rng.uniform(170, 230) + self.t * 3) * self.fall,
                               "cloud": cloud, "txt": self.rng.choice(THOUGHTS)})
        player = (self.px - 36, H - 190, 72, 130)
        for it in self.items[:]:
            it["y"] += it["vy"] * dt
            hit = player[0] - 20 < it["x"] < player[0] + player[2] + 20 and player[1] < it["y"] < player[1] + player[3]
            if hit:
                self.items.remove(it)
                if it["cloud"]:
                    self.hits += 1
                    self.stun, self.flash = 0.8, 0.3
                else:
                    self.good += 1
            elif it["y"] > H:
                self.items.remove(it)
        if self.t >= self.duration:
            self.finish({"score": self.good / max(1, self.good_total), "hits": self.hits})

    def render(self, surf):
        surf.fill((104, 82, 170))
        pygame.draw.rect(surf, ui.INDIGO, (0, H - 60, W, 60))
        pygame.draw.rect(surf, ui.LAV_LT, (0, H - 64, W, 4))
        pygame.draw.rect(surf, ui.CREAM, (200, 40, 624, 90))
        pygame.draw.rect(surf, ui.PINK, (200, 40, 624, 90), 4)
        text(surf, "The exam" if self.exam else "The lesson", (W // 2, 70), 44, ui.INDIGO, center=True)
        for dx in (120, 330, 560, 780):
            pygame.draw.rect(surf, (214, 160, 140), (dx, H - 100, 120, 40))
            pygame.draw.rect(surf, (150, 100, 110), (dx, H - 100, 120, 40), 3)
        for it in self.items:
            x, y = int(it["x"]), int(it["y"])
            if it["cloud"]:
                for ox in (-18, 0, 18):
                    pygame.draw.circle(surf, ui.PINK, (x + ox, y), 20)
                pygame.draw.rect(surf, ui.BLUE, (x - 36, y + 12, 72, 8))
                text(surf, it["txt"], (x, y + 28), 20, ui.CREAM, center=True, shadow=True)
            else:
                pygame.draw.rect(surf, ui.GOOD, (x - 28, y - 20, 56, 40))
                pygame.draw.rect(surf, (40, 120, 100), (x - 28, y - 20, 56, 40), 3)
                text(surf, "A+", (x, y - 8), 28, ui.INDIGO_DK, center=True)
        img = ui.sprite(ui.HERO, self.facing, 3)
        w, h = img.get_size()
        surf.blit(img, (int(self.px - w / 2), H - 60 - h + 10))
        if self.flash > 0:
            ui.tint(surf, (251, 107, 162), self.flash)
        left = max(0.0, self.duration - self.t)
        pygame.draw.rect(surf, ui.INDIGO, (330, 150, 364, 14))
        pygame.draw.rect(surf, ui.GOOD, (330, 150, int(364 * left / self.duration), 14))
        pygame.draw.rect(surf, ui.LAV_LT, (330, 150, 364, 14), 2)
        text(surf, "Caught %d     Worries hit %d" % (self.good, self.hits), (W // 2, 176), 30, ui.CREAM, center=True, shadow=True)

class VoiceGame(MiniGame):
    title = "Steady voice"
    help = "Hold LEFT or RIGHT to keep the dot inside the zone while you present. The audience's attention makes your voice shake."
    DURATION = 20.0

    def __init__(self, params):
        super().__init__()
        sev = params.get("sev", 1.0)
        self.tremor = (1.0 + 1.6 * params.get("worry", 50) / 100 + (0.6 if params.get("presenting") else 0)) * (0.7 + 0.4 * sev)
        self.x = 0.0
        self.v = 0.0
        self.in_zone = 0.0
        self.spike = 0.0
        self.next_spike = 4.0

    def step(self, dt):
        dx = self.axis((pygame.K_a, pygame.K_LEFT), (pygame.K_d, pygame.K_RIGHT))
        self.next_spike -= dt
        if self.next_spike <= 0:
            self.spike, self.next_spike = 1.5, self.rng.uniform(4, 6)
        self.spike = max(0.0, self.spike - dt)
        k = self.tremor * (2.0 if self.spike > 0 else 1.0)
        self.v += self.rng.uniform(-1, 1) * k * dt * 6 + dx * dt * 5.5
        self.v *= max(0.0, 1 - 0.9 * dt)
        self.x = max(-1.2, min(1.2, self.x + self.v * dt))
        if abs(self.x) < 0.22:
            self.in_zone += dt
        if self.t >= self.DURATION:
            self.finish({"score": self.in_zone / self.DURATION})

    def render(self, surf):
        surf.fill(ui.INDIGO_DK)
        mx = W // 2 + self.x * 300
        wide = 1.0 + (0.5 if self.spike > 0 else 0.0)
        for i in range(9):
            ui.draw_eye(surf, 110 + i * 100, 110 + (i % 2) * 40, 26 * wide, 0.9, mx, 380)
        pygame.draw.polygon(surf, ui.INDIGO, [(W // 2 - 60, 200), (W // 2 + 60, 200), (W // 2 + 220, H), (W // 2 - 220, H)])
        pygame.draw.rect(surf, (176, 112, 120), (W // 2 - 90, 520, 180, 90))
        pygame.draw.rect(surf, (214, 160, 140), (W // 2 - 90, 520, 180, 14))
        img = ui.sprite(ui.HERO, "north", 3)
        surf.blit(img, (W // 2 - img.get_width() // 2, 400))
        pygame.draw.rect(surf, ui.INDIGO, (W // 2 - 330, 300, 660, 40))
        pygame.draw.rect(surf, ui.LAV, (W // 2 - 330, 300, 660, 40), 3)
        zone_w = int(0.44 * 300)
        pygame.draw.rect(surf, ui.GOOD, (W // 2 - zone_w, 304, zone_w * 2, 32))
        inside = abs(self.x) < 0.22
        pygame.draw.circle(surf, ui.YELLOW if inside else ui.PINK, (int(mx), 320), 18)
        pygame.draw.circle(surf, ui.INDIGO_DK, (int(mx), 320), 18, 3)
        text(surf, "Your voice", (W // 2, 262), 34, center=True)
        left = max(0.0, self.DURATION - self.t)
        text(surf, "%d s left" % math.ceil(left), (W - 30, 20), 32, right=True)
        text(surf, "Steady: %d%%" % round(100 * self.in_zone / max(0.1, self.t)), (30, 20), 32)

class CheckGame(MiniGame):
    title = "Homework"
    help = "Type each answer and press Enter. Then choose: R to re-check, or SPACE to trust yourself and move on."

    def __init__(self, params):
        super().__init__()
        r = self.rng
        self.qs = []
        for i in range(5):
            if i % 2 == 0:
                a, b = r.randint(12, 49), r.randint(12, 49)
                self.qs.append(("%d + %d" % (a, b), a + b))
            else:
                a, b = r.randint(3, 9), r.randint(6, 12)
                self.qs.append(("%d x %d" % (a, b), a * b))
        self.q = 0
        self.input = ""
        self.state = "answer"
        self.rechecks = self.trusted = self.correct = self.q_checks = 0
        self.msg = ""

    def event(self, e):
        if self.ready > 0 or self.done or e.type != pygame.KEYDOWN:
            return
        if self.state == "answer":
            if pygame.K_0 <= e.key <= pygame.K_9 and len(self.input) < 4:
                self.input += chr(e.key)
            elif e.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif e.key == pygame.K_RETURN and self.input:
                self.state = "decide"
                self.msg = ""
        elif self.state == "decide":
            if e.key == pygame.K_r:
                self.rechecks += 1
                self.q_checks += 1
                ok = int(self.input) == self.qs[self.q][1]
                self.msg = ("Re-checking... same answer. It was right. (The doubt will come back.)" if ok
                            else "Re-checking... something looks off. Maybe change it?")
                self.state = "answer"
                if not ok:
                    self.input = ""
            elif e.key == pygame.K_SPACE:
                if int(self.input) == self.qs[self.q][1]:
                    self.correct += 1
                if self.q_checks == 0:
                    self.trusted += 1
                self.q += 1
                self.input, self.q_checks, self.msg, self.state = "", 0, "", "answer"
                if self.q >= len(self.qs):
                    self.finish({"correct": self.correct, "rechecks": self.rechecks, "trusted": self.trusted})

    def render(self, surf):
        surf.fill(ui.CREAM)
        for y in range(120, H, 36):
            pygame.draw.line(surf, (190, 175, 235), (0, y), (W, y), 1)
        pygame.draw.line(surf, ui.PINK, (110, 0), (110, H), 3)
        if self.q >= len(self.qs):
            return
        text(surf, "Question %d of %d" % (self.q + 1, len(self.qs)), (150, 40), 36, ui.VIOLET)
        text(surf, self.qs[self.q][0] + " = ?", (150, 150), 92, ui.INDIGO)
        pygame.draw.rect(surf, ui.WHITE, (150, 280, 260, 70))
        pygame.draw.rect(surf, ui.VIOLET, (150, 280, 260, 70), 4)
        text(surf, self.input + ("_" if self.state == "answer" and int(self.t * 2) % 2 == 0 else ""), (170, 292), 66, ui.INDIGO)
        if self.state == "decide":
            panel(surf, (150, 390, 724, 140), (46, 27, 91, 245))
            text(surf, "What if it's wrong?", (180, 405), 46, ui.YELLOW)
            text(surf, "R  =  re-check it        SPACE  =  trust yourself and move on", (180, 470), 32)
        elif self.msg:
            text(surf, self.msg, (150, 400), 28, ui.PINK)
        else:
            text(surf, "Type your answer, then press Enter.", (150, 400), 28, ui.LAV_DK)
        text(surf, "Re-checks: %d" % self.rechecks, (W - 40, 40), 32, ui.PINK, right=True)
