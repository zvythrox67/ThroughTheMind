import os
import sys
import pygame
import ui
from ui import W, H, Button, text

class StartScene:
    def __init__(self, app):
        self.app = app
        self.bg = ui.title_background()
        self.has_art = os.path.exists(os.path.join(ui.HERE, "assets", "title.png"))
        self.buttons = [Button("Start", (362, 396, 300, 62), app.show_menu, 42),
                        Button("Quit", (362, 476, 300, 62), app.quit, 42)]
        
    def event(self, e):
        for b in self.buttons:
            b.event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            self.app.show_menu()
            
    def update(self, dt):
        pass
    
    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        if not self.has_art:
            text(screen, "Through the Mind", (W // 2, 250), 96, ui.TEXT, center=True, shadow=True)
        for b in self.buttons:
            b.draw(screen)
            

class MenuScene:
    STORIES = [("Major Depressive Disorder", None), ("Substance Abuse", None), ("Generalized Anxiety Disorder", "gad"), ("Dyslexia", None), ("PTSD", None)]
    BLURBS = {"gad": "Miku: your body can't relax and your mind runs every worst case. 5 levels, and it gets worse."}
    
    def __init__(self, app):
        self.app = app
        self.bg = ui.title_background(clean=True)
        self.buttons = []
        self.keys = []
        for i, (name, key) in enumerate(self.STORIES):
            x, y = 32 + (i % 3) * 330, 220 + (i // 3) * 110
            if key:
                b = Button(name + "\n(Miku)", (x, y, 300, 92), lambda k=key: app.play(k), 30)
            else:
                b = Button(name + "\n(coming soon)", (x, y, 300, 92), None, 30, enabled=False)
            self.buttons.append(b)
            self.keys.append(key)
        self.buttons.append(Button("Back", (32 + 2 * 330, 330, 300, 92), app.show_start, 36))
        self.keys.append(None)
        self.blurb = ""
        
    def event(self, e):
        for b in self.buttons:
            b.event(e)
        if e.type == pygame.MOUSEMOTION:
            self.blurb = ""
            for b, k in zip(self.buttons, self.keys):
                if k and b.contains(e.pos):
                    self.blurb = self.BLURBS.get(k, "")
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.show_start()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        ui.tint(screen, (24, 12, 56), 0.68)
        text(screen, "Choose a story", (W // 2, 110), 80, ui.YELLOW, center=True, shadow=True)
        for b in self.buttons:
            b.draw(screen)
        text(screen, self.blurb, (W // 2, 540), 32, ui.TEXT, center=True, shadow=True)

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Through the Mind")
        self.clock = pygame.time.Clock()
        self.scene = None
        self.show_start()

    def show_start(self):
        self.scene = StartScene(self)

    def show_menu(self):
        self.scene = MenuScene(self)

    def play(self, key):
        from play import PlayScene 
        self.scene = PlayScene(self)

    def quit(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            dt = min(0.05, self.clock.tick(60) / 1000.0)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit()
                self.scene.event(e)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    App().run()
