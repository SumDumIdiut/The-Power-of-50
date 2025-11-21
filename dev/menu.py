import os
import sys
import pygame
import time

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Utils
from Utils.textbox import Textbox
from Utils.save_manager import save_save, load_save

# Games
from games.snake.snake_game import run as run_snake
from games.shooter.shooter_game import ShooterGame
from games.rhythm import beatmap_loader
from games.rhythm.rhythm_game import run as run_rhythm_game

# ------------------------------
# Helper functions
# ------------------------------
def draw_centered_text(surface, text, font, color, center):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=center)
    surface.blit(txt, rect)

# ------------------------------
# Snake sequence for dev menu
# ------------------------------
def run_snake_dev(screen):
    while True:
        result = run_snake(screen)
        if result in ('quit','menu'):
            return

# ------------------------------
# Shooter sequence for dev menu
# ------------------------------
def run_shooter_dev(screen):
    game = ShooterGame(screen)
    game.run()

# ------------------------------
# Rhythm sequence for dev menu
# ------------------------------

def run_rhythm_dev(screen):
    result = run_rhythm_game(screen)
    # result will be 'menu' or 'quit'
    return result

# ------------------------------
# Dev Menu
# ------------------------------
def dev_menu(screen):
    width, height = screen.get_size()
    font_title = pygame.font.SysFont('segoeui', 64, bold=True)
    font_btn = pygame.font.SysFont('segoeui', 36, bold=True)

    buttons = [
        {"label": "Snake", "rect": pygame.Rect(0,0,300,80)},
        {"label": "Shooter", "rect": pygame.Rect(0,0,300,80)},
        {"label": "Rhythm", "rect": pygame.Rect(0,0,300,80)},
        {"label": "Quit", "rect": pygame.Rect(0,0,300,80)}
    ]

    for i, b in enumerate(buttons):
        b["rect"].center = (width//2, height//2 + i*100)

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'menu'
                if event.key == pygame.K_1:
                    run_snake_dev(screen)
                if event.key == pygame.K_2:
                    run_shooter_dev(screen)
                if event.key == pygame.K_3:
                    run_rhythm_dev(screen)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    if b["rect"].collidepoint(event.pos):
                        if b["label"]=="Snake":
                            run_snake_dev(screen)
                        elif b["label"]=="Shooter":
                            run_shooter_dev(screen)
                        elif b["label"]=="Rhythm":
                            run_rhythm_dev(screen)
                        elif b["label"]=="Quit":
                            return 'quit'

        screen.fill((20,20,30))
        draw_centered_text(screen, "DEV MENU", font_title, (255,215,0), (width//2, height//3))

        for b in buttons:
            pygame.draw.rect(screen, (255,215,0), b["rect"], border_radius=10)
            pygame.draw.rect(screen, (200,160,0), b["rect"], 4, border_radius=10)
            draw_centered_text(screen, b["label"], font_btn, (0,0,0), b["rect"].center)

        pygame.display.flip()
        clock.tick(60)

# ------------------------------
# ENTRY POINT
# ------------------------------
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption('DEV MENU - The Power of 50')

    dev_menu(screen)
    pygame.quit()
    sys.exit(0)
