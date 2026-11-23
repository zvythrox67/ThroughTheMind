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
        self.buttons = [Button("Start", (362, 396, 300, 62), lambda: app.play("gad"), 42),
                        Button("Quit", (362, 476, 300, 62), app.quit, 42)]

    def event(self, e):
        for b in self.buttons:
            b.event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            self.app.play("gad")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        if not self.has_art:
            text(screen, "Through the Mind", (W // 2, 250), 96, ui.TEXT, center=True, shadow=True)
        for b in self.buttons:
            b.draw(screen)

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