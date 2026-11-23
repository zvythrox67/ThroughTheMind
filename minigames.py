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
