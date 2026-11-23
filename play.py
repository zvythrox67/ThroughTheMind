import math
import random

import pygame
import minigames
import pixel
import ui
import world
from game import Game, TOTAL_LEVELS, TASKS, INTRO, Dialogue
from ui import W, H, text, panel


class PlayScene:
    def __init__(self, app):
        self.app = app
        self.game = Game()
        self.game.ui = self
        self.dialog = ui.DialogueBox()
        self.px, self.py = 340.0, 470.0
        self.facing = "south"
        self.moving = False
        self.bob = 0.0
        self.room_id = "home"
        self.bg = None
        self.objs = []
        self.near = None
        self.mini = None
        self.mini_cb = None
        self.sum = None
        self.travel_state = 0
        self.travel_t = 0.0
        self.pending = None
        self.from_room = "home"
        self.fade = 0.0
        self.flash_t = 0.0
        self.panic_t = 0.0
        self.toasts = []
        self.thoughts = []
        self.stats_open = False
        self.slide = 0.0
        self.time = 0.0
        self.tab = (W - 130, 12, 118, 32)
        self.vig = ui.make_vignette((30, 14, 60), 0.42)
        self.tunnel = ui.make_vignette((16, 6, 40), 0.18)
        self.small = pygame.Surface((pixel.SW, pixel.SH))
        self.game.start_level()
        self.new_level()

    def say(self, d):
        self.dialog.say(d)

    def toast(self, t, good):
        self.toasts.append([t, good, 0.0])
        if len(self.toasts) > 6:
            self.toasts.pop(0)

    def thought(self, t):
        self.thoughts.append([t, self.px, self.py - 110, 0.0])

    def travel(self, ex):
        if self.travel_state != 0:
            return
        self.pending, self.from_room, self.travel_state, self.travel_t = ex, self.room_id, 1, 0.0

    def minigame(self, kind, params, cb):
        self.mini = minigames.make(kind, params)
        self.mini_cb = cb

    def summary(self, title, body, buttons):
        self.dialog.clear()
        self.sum = {"title": title, "body": body, "buttons": buttons, "sel": 0, "rects": []}

    def panic_fx(self, seconds):
        self.panic_t = seconds
        self.flash_t = 0.5

    def exit_to_menu(self):
        self.app.show_menu()

    def new_level(self):
        g = self.game
        self.load_room("home", 340, 470)
        info = g.level_info()
        lines = [info["blurb"], "", "Symptoms this level:"] + ["  - " + n for n in info["new"]]
        self.summary("Level %d: %s" % (g.level, info["name"]), "\n".join(lines), [("Begin", self.begin_level)])

    def begin_level(self):
        g = self.game
        chain = []
        if g.level == 1:
            chain.append(Dialogue("Content note", "This game shows struggles with mental health, which some people may find "
                                  "upsetting. If you're struggling, please talk to a trusted adult, a school counselor, or a doctor. "
                                  "In the US you can call or text 988 anytime."))
            for i, page in enumerate(INTRO):
                chain.append(Dialogue("Meet Miku" if i == 0 else "Miku", page))
            chain.append(Dialogue("How to play", "Move with WASD or the arrow keys. Press E to interact. Press Q (or click Stats) "
                                  "to see your levels. Press Esc to pause.\n\nEach task plays differently: when you work, eat, "
                                  "present, or sleep, the game switches into a mini-game.\n\nGet through all 5 levels while keeping "
                                  "your grades, attendance, mood, energy, health, stress and relationships on track."))
        chain.append(g.morning())
        for i in range(len(chain) - 1):
            nxt = chain[i + 1]
            chain[i].then(lambda nxt=nxt: self.say(nxt))
        self.say(chain[0])

    def load_room(self, rid, sx, sy):
        self.room_id = rid
        self.game.room = rid
        self.objs = list(world.ROOMS[rid].objs)
        self.bg = pixel.make_room_bg(world.ROOMS[rid])
        self.px, self.py = float(sx), float(sy)
        self.near = None

    def event(self, e):
        if self.mini is not None:
            self.mini.event(e)
            return
        if self.sum is not None:
            self.sum_event(e)
            return
        if self.dialog.active():
            self.dialog.event(e)
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q:
                self.stats_open = not self.stats_open
            elif e.key == pygame.K_ESCAPE:
                self.pause()
            elif e.key == pygame.K_e and self.near is not None and self.travel_state == 0:
                self.activate(self.near)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            x, y, w, h = self.tab
            if x <= e.pos[0] <= x + w and y <= e.pos[1] <= y + h:
                self.stats_open = not self.stats_open

    def sum_event(self, e):
        s = self.sum
        n = len(s["buttons"])
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_UP):
                s["sel"] = max(0, s["sel"] - 1)
            elif e.key in (pygame.K_RIGHT, pygame.K_DOWN):
                s["sel"] = min(n - 1, s["sel"] + 1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.pick_summary(s["sel"])
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(s["rects"]):
                if r[0] <= e.pos[0] <= r[0] + r[2] and r[1] <= e.pos[1] <= r[1] + r[3]:
                    self.pick_summary(i)

    def pick_summary(self, i):
        fn = self.sum["buttons"][i][1]
        self.sum = None
        if fn:
            fn()

    def pause(self):
        self.say(Dialogue("Paused", "Take a break whenever you need to.")
                 .choice("Resume").choice("Back to the menu", self.app.show_menu))

    def activate(self, o):
        if o.exit:
            self.travel(o)
        else:
            self.game.act(o.action)

    def update(self, dt):
        self.time += dt
        self.slide += ((1.0 if self.stats_open else 0.0) - self.slide) * min(1.0, dt * 10)
        for t in self.toasts:
            t[2] += dt
        self.toasts = [t for t in self.toasts if t[2] < 2.4]
        for t in self.thoughts:
            t[3] += dt
            t[2] -= dt * 14
        self.thoughts = [t for t in self.thoughts if t[3] < 4.0]
        self.flash_t = max(0.0, self.flash_t - dt)
        self.panic_t = max(0.0, self.panic_t - dt)

        if self.travel_state:
            self.update_travel(dt)
            return
        if self.mini is not None:
            self.mini.update(dt)
            if self.mini.done:
                m, cb = self.mini, self.mini_cb
                self.mini = self.mini_cb = None
                cb(m.result)
                self.dialog.flush()
            return
        if self.dialog.active() or self.sum is not None:
            self.near = None
            return

        k = pygame.key.get_pressed()
        dx = (1 if (k[pygame.K_d] or k[pygame.K_RIGHT]) else 0) - (1 if (k[pygame.K_a] or k[pygame.K_LEFT]) else 0)
        dy = (1 if (k[pygame.K_s] or k[pygame.K_DOWN]) else 0) - (1 if (k[pygame.K_w] or k[pygame.K_UP]) else 0)
        self.moving = bool(dx or dy)
        if self.moving:
            ln = math.hypot(dx, dy)
            step = 230 * dt
            nx, ny = self.px + dx / ln * step, self.py + dy / ln * step
            if not self.blocked(nx, self.py):
                self.px = nx
            if not self.blocked(self.px, ny):
                self.py = ny
            self.px = max(50.0, min(W - 50.0, self.px))
            self.py = max(190.0, min(H - 40.0, self.py))
            self.facing = ui.dir_toward(dx, dy)
            self.bob += dt * 12
        else:
            self.bob = 0.0
        self.near = None
        best = 46.0
        for o in self.objs:
            if o.deco:
                continue
            d = o.dist(self.px, self.py)
            if d < best:
                best, self.near = d, o

    def blocked(self, x, y):
        l, t, r, b = x - 13, y - 14, x + 13, y
        for o in self.objs:
            if o.exit:
                continue
            if l < o.x + o.w and r > o.x and t < o.y + o.h and b > o.y:
                return True
        return False

    def update_travel(self, dt):
        self.travel_t += dt
        if self.travel_state == 1:
            self.fade = min(1.0, self.travel_t / 0.25)
            if self.travel_t >= 0.25:
                ex = self.pending
                self.game.room = ex.via or "transit"
                self.game.advance(ex.minutes)
                self.load_room(ex.to, ex.sx, ex.sy)
                self.travel_state, self.travel_t = 2, 0.0
        else:
            self.fade = 1.0 - min(1.0, self.travel_t / 0.25)
            if self.travel_t >= 0.25:
                self.travel_state, self.fade = 0, 0.0
                self.game.on_arrive(self.pending.to, self.from_room)
                self.dialog.flush()

    def draw(self, screen):
        if self.mini is not None:
            self.mini.draw(screen)
            self.draw_toasts(screen)
            return
        self.small.blit(self.bg, (0, 0))
        pixel.draw_scene(self.small, self.objs, (ui.HERO, self.px, self.py, self.facing, self.bob, self.moving), self.time)
        canvas = pygame.transform.scale(self.small, (W, H))
        self.draw_labels(canvas)

        g = self.game
        sev, worry = g.sev(), g.worry
        shake = max(0.0, (worry - 70) / 30 * 1.5) + max(0.0, (sev - 1.0) * 0.8) 
        sway = 0.0
        if self.panic_t > 0:
            shake += 3.5
            sway = 6.0
        elif g.level >= 4 and worry > 55:
            sway = 3.0 * (sev - 1.2)
        off_x = int(random.uniform(-shake, shake) + math.sin(self.time * 1.7) * sway)
        off_y = int(random.uniform(-shake, shake) + math.cos(self.time * 1.3) * sway * 0.6)
        screen.fill((0, 0, 0))
        screen.blit(canvas, (off_x, off_y))
        bpm = 60 + worry * 0.6 + (50 if self.panic_t > 0 else 0)
        beat = max(0.0, math.sin(self.time * bpm / 60 * 2 * math.pi)) ** 6
        a = min(1.0, 0.06 + 0.16 * sev + 0.3 * worry / 100 + 0.15 * beat * sev)
        self.vig.set_alpha(int(255 * a))
        screen.blit(self.vig, (0, 0))
        tun = 0.0
        if g.level >= 3:
            tun = min(1.0, (sev - 1.0) * 0.9 + (worry / 100 * 0.4 if g.level >= 4 else 0.0))
        if self.panic_t > 0:
            tun = 0.95
            ui.tint(screen, (200, 40, 80), 0.10 + 0.12 * beat)
        if tun > 0:
            self.tunnel.set_alpha(int(255 * tun))
            screen.blit(self.tunnel, (0, 0))

        self.draw_thoughts(screen)
        self.draw_hud(screen)
        self.draw_toasts(screen)
        if self.near is not None and not self.dialog.active() and self.sum is None and self.travel_state == 0:
            text(screen, "[E]  " + self.near.label, (W // 2, H - 44), 34, center=True, shadow=True)
        self.dialog.draw(screen)
        if self.sum is not None:
            self.draw_summary(screen)
        if self.fade > 0:
            ui.tint(screen, (20, 10, 40), self.fade)
        if self.flash_t > 0:
            ui.tint(screen, (255, 240, 255), min(1.0, self.flash_t / 0.5) * 0.7)

    def draw_labels(self, s):
        for o in self.objs:
            if not o.label or o.kind in ("npcs", "door") and False:
                continue
            if o.kind == "npcs":
                continue
            size = 24
            while size > 16 and ui.text_width(o.label, size) > o.w - 6:
                size -= 2
            lines = ui.wrap(o.label, size, o.w - 6)
            lh = ui.font(size).get_height()
            if o.npcs:
                y = o.y + o.h - lh * len(lines) - 6
            else:
                y = o.y + (o.h - lh * len(lines)) // 2
            for ln in lines:
                text(s, ln, (o.x + o.w // 2, y), size, ui.CREAM, center=True, shadow=True)
                y += lh

    def draw_thoughts(self, s):
        for t, x, y, age in self.thoughts:
            a = max(0.0, min(1.0, min(age / 0.4, (4.0 - age) / 1.0)))
            w = ui.text_width(t, 26) + 24
            bx = int(max(10, min(W - w - 10, x - w / 2)))
            bg = pygame.Surface((w, 32), pygame.SRCALPHA)
            pygame.draw.rect(bg, (255, 243, 196, int(a * 235)), (0, 0, w, 32))
            pygame.draw.rect(bg, (251, 107, 162, int(a * 255)), (0, 0, w, 32), 2)
            s.blit(bg, (bx, int(y) - 22))
            img = ui.font(26).render(t, True, ui.INDIGO_DK)
            img.set_alpha(int(a * 255))
            s.blit(img, (bx + 12, int(y) - 15))

    def draw_toasts(self, s):
        y = 70
        for t, good, age in self.toasts:
            a = max(0.0, min(1.0, (2.4 - age) / 0.6))
            col = ui.GOOD if good else ui.BAD
            img = ui.font(30).render(t, True, col)
            img.set_alpha(int(a * 255))
            sh = ui.font(30).render(t, True, ui.INDIGO_DK)
            sh.set_alpha(int(a * 255))
            x = W // 2 - img.get_width() // 2
            s.blit(sh, (x + 2, y + 2))
            s.blit(img, (x, y))
            y += 24

    def draw_hud(self, s):
        g = self.game
        panel(s, (10, 10, 252, 158))
        text(s, "Level %d/%d   %s" % (g.level, TOTAL_LEVELS, g.time()), (20, 18), 30, ui.YELLOW)
        text(s, world.ROOMS[self.room_id].name, (20, 42), 22, ui.LAV_LT)
        y = 66
        for k, label in TASKS.items():
            done = g.tasks[k]
            text(s, ("[x] " if done else "[ ] ") + label, (20, y), 21, ui.GOOD if done else ui.TEXT)
            y += 16
        x, ty, w, h = self.tab
        pygame.draw.rect(s, ui.INDIGO_DK, (x + 3, ty + 4, w, h))
        pygame.draw.rect(s, ui.PINK if self.stats_open else ui.LAV_DK, (x, ty, w, h))
        pygame.draw.rect(s, ui.YELLOW if self.stats_open else ui.LAV_LT, (x, ty, w, h), 3)
        text(s, "Stats (Q)", (x + w // 2, ty + 8), 24, center=True)
        rows = 13
        ph = 56 + rows * 25
        pw = 330
        top = int(-ph + self.slide * (ph + 52))
        if self.slide > 0.01:
            panel(s, (W - pw - 12, top, pw, ph))
            bx = W - pw + 4
            yy = top + 14
            text(s, "Miku's levels", (bx, yy), 30, ui.YELLOW)
            yy += 34
            for name, key in (("Happiness", "happiness"), ("Stress", "stress"), ("Attentiveness", "attentiveness"),
                              ("Energy", "energy"), ("Health", "health")):
                ui.bar(s, bx, yy, name, g.st[key], key == "stress")
                yy += 25
            ui.bar(s, bx, yy, "Grades", g.grades)
            yy += 25
            ui.bar(s, bx, yy, "Attendance", g.attendance())
            yy += 25
            for who in ("family", "friends", "teachers", "classmates"):
                ui.bar(s, bx, yy, who.capitalize(), g.rel[who])
                yy += 25
            ui.bar(s, bx, yy, "Worry", g.worry, True)
            yy += 25
            ui.bar(s, bx, yy, "Calm skills", g.skill)

    def draw_summary(self, s):
        ui.tint(s, (20, 8, 48), 0.78)
        sm = self.sum
        lines = ui.wrap(sm["body"], 26, 660)
        pw = 720
        ph = 100 + len(lines) * 23 + 80
        x, y = (W - pw) // 2, max(20, (H - ph) // 2)
        panel(s, (x, y, pw, ph), (34, 20, 70, 248))
        text(s, sm["title"], (x + 28, y + 24), 50, ui.YELLOW)
        ty = y + 88
        for ln in lines:
            text(s, ln, (x + 28, ty), 26)
            ty += 23
        sm["rects"] = []
        bx = x + 28
        for i, (label, _) in enumerate(sm["buttons"]):
            r = (bx, y + ph - 62, 210, 42)
            sm["rects"].append(r)
            pygame.draw.rect(s, ui.PINK if i == sm["sel"] else ui.LAV_DK, r)
            pygame.draw.rect(s, ui.YELLOW if i == sm["sel"] else ui.LAV_LT, r, 3)
            text(s, label, (r[0] + r[2] // 2, r[1] + 11), 28, center=True)
            bx += 224