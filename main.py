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
    