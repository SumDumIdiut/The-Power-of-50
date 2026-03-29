"""
menu.py — The Power of 50 carousel menu.

Two game pages arranged in a looping horizontal carousel:
  Page 0 — Snake
  Page 1 — Shooter

LEFT / RIGHT arrow keys slide between pages (looping).
ESC quits.
"""
from __future__ import annotations
import importlib.util
import math
import os
import sys

import pygame

# ---------------------------------------------------------------------------
# Path setup + module loading
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle — files are extracted to sys._MEIPASS
    ROOT_DIR = sys._MEIPASS
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def _load_mod(name: str, rel_path: str):
    """Load a module from a file path, caching it in sys.modules."""
    if name in sys.modules:
        return sys.modules[name]
    path = os.path.join(ROOT_DIR, rel_path.replace('/', os.sep))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Loading snake_game causes it to insert its directory into sys.path and
# import snake_save as a bare module — so snake_save ends up in sys.modules.
_snake_mod   = _load_mod('snake_game',   'games/snake/snake_game.py')
_shooter_mod = _load_mod('shooter_game', 'games/shooter/shooter_game.py')

SnakeGame   = _snake_mod.SnakeGame
ShooterGame = _shooter_mod.ShooterGame

_snake_ss   = sys.modules.get('snake_save')   # loaded as side-effect of snake_game
_shooter_ss = _shooter_mod._save_mod           # loaded internally by shooter_game


# ---------------------------------------------------------------------------
# Snake page background
# ---------------------------------------------------------------------------
_C_BG    = (  8,  10,  16)
_C_GRID  = ( 14,  17,  26)
_C_GREEN = ( 60, 255,  80)


def _bake_snake_bg(w: int, h: int) -> pygame.Surface:
    tw = th = 20
    bg = pygame.Surface((w, h))
    nx, ny = w // tw + 1, h // th + 1
    for gx in range(nx):
        for gy in range(ny):
            n = (gx * 73856093 ^ gy * 19349663) & 0xFFFFFF
            n = ((n ^ (n >> 13)) * 1664525 + 1013904223) & 0xFFFFFF
            v = (n & 0xFF) / 255.0
            r = min(255, _C_BG[0] + int(v * 4))
            g = min(255, _C_BG[1] + int(v * 5))
            b = min(255, _C_BG[2] + int(v * 7))
            pygame.draw.rect(bg, (r, g, b), (gx * tw, gy * th, tw, th))
    for x in range(0, w + 1, tw):
        pygame.draw.line(bg, _C_GRID, (x, 0), (x, h))
    for y in range(0, h + 1, th):
        pygame.draw.line(bg, _C_GRID, (0, y), (w, y))
    return bg


# ---------------------------------------------------------------------------
# Snake page
# ---------------------------------------------------------------------------
class SnakePage:
    def __init__(self, sw: int, sh: int):
        self._sw, self._sh = sw, sh

        self._bg = _bake_snake_bg(sw, sh)

        gf = _shooter_mod._get_font
        self._ft   = gf(62)
        self._fsub = gf(24)
        self._fb   = gf(22)
        self._fsm  = gf(15)
        self._fsd  = gf(17)

        cx, cy = sw // 2, sh // 2
        bw, bh = 300, 58
        self._new_r  = pygame.Rect(cx - bw // 2, cy - 20,       bw, bh)
        self._con_r  = pygame.Rect(cx - bw // 2, cy - 20 + 78,  bw, bh)
        self._seed_r = pygame.Rect(cx - 140,     sh - 110,      220, 36)
        self._shuf_r = pygame.Rect(cx + 88,      sh - 110,      120, 36)

        self._seed    = _snake_ss.new_seed() if _snake_ss else 'AAAAAA'
        self._editing = False
        self._sinput  = self._seed

    # ---- internal helpers --------------------------------------------------

    def _draw_btn(self, surf: pygame.Surface, rect: pygame.Rect,
                  label: str, hover: bool, active: bool = True) -> None:
        if not active:
            pygame.draw.rect(surf, (22, 30, 22), rect, border_radius=9)
            pygame.draw.rect(surf, (40, 55, 40), rect, 2, border_radius=9)
            t = self._fb.render(label, True, (55, 70, 55))
        else:
            bgc = (28, 55, 32) if hover else (14, 30, 18)
            bdc = (100, 210, 105) if hover else (38, 90, 48)
            pygame.draw.rect(surf, bgc, rect, border_radius=9)
            pygame.draw.rect(surf, bdc, rect, 2, border_radius=9)
            t = self._fb.render(label, True, (175, 230, 175))
        surf.blit(t, t.get_rect(center=rect.center))

    # ---- public interface --------------------------------------------------

    def handle(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if self._editing:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self._seed = self._sinput.upper() if self._sinput else (
                        _snake_ss.new_seed() if _snake_ss else 'AAAAAA')
                    self._editing = False
                elif event.key == pygame.K_BACKSPACE:
                    self._sinput = self._sinput[:-1]
                elif len(self._sinput) < 6 and event.unicode.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                    self._sinput = (self._sinput + event.unicode).upper()
                return None
            if event.key == pygame.K_ESCAPE:
                return 'quit'

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._editing:
                if not self._seed_r.collidepoint(event.pos):
                    self._seed = self._sinput.upper() if self._sinput else (
                        _snake_ss.new_seed() if _snake_ss else 'AAAAAA')
                    self._editing = False
                return None
            has = _snake_ss.has_save() if _snake_ss else False
            if self._new_r.collidepoint(event.pos):
                return 'new_game'
            if self._con_r.collidepoint(event.pos) and has:
                return 'continue'
            if self._shuf_r.collidepoint(event.pos):
                self._seed   = _snake_ss.new_seed() if _snake_ss else 'AAAAAA'
                self._sinput = self._seed
            elif self._seed_r.collidepoint(event.pos):
                self._editing = True
                self._sinput  = self._seed
        return None

    def draw(self, surf: pygame.Surface, frame: int) -> None:
        cx, cy = self._sw // 2, self._sh // 2
        mx, my = pygame.mouse.get_pos()
        has = _snake_ss.has_save() if _snake_ss else False

        surf.blit(self._bg, (0, 0))

        # Title — pulsing green
        pulse = 0.5 + 0.5 * math.sin(frame * 0.05)
        tc = tuple(int(c * (0.82 + 0.18 * pulse)) for c in _C_GREEN)
        t1 = self._ft.render('SNAKE', True, tc)
        t2 = self._fsub.render('\u2014 C L A S S I C \u2014', True, (40, 120, 55))
        surf.blit(t1, t1.get_rect(center=(cx, cy - 160)))
        surf.blit(t2, t2.get_rect(center=(cx, cy - 100)))

        self._draw_btn(surf, self._new_r, '\u25b6  NEW GAME',  self._new_r.collidepoint(mx, my))
        self._draw_btn(surf, self._con_r, '\u27f2  CONTINUE',  self._con_r.collidepoint(mx, my), active=has)

        if has and _snake_ss:
            sd = _snake_ss.load()
            if sd:
                info = self._fsm.render(
                    f"  {sd.get('score', 0)} apples \u00b7 seed {sd.get('seed', '?')}",
                    True, (100, 160, 110))
                surf.blit(info, info.get_rect(midleft=(self._con_r.left + 8, self._con_r.bottom + 8)))

        # Seed field
        pygame.draw.rect(surf, (22, 30, 18) if self._editing else (16, 22, 14), self._seed_r, border_radius=6)
        pygame.draw.rect(surf, (100, 180, 100) if self._editing else (40, 80, 48), self._seed_r, 2, border_radius=6)
        disp = self._sinput if self._editing else self._seed
        if self._editing and (pygame.time.get_ticks() // 500) % 2 == 0:
            disp += '|'
        sl = self._fsd.render(disp, True, (160, 220, 160))
        surf.blit(sl, sl.get_rect(midleft=(self._seed_r.left + 8, self._seed_r.centery)))

        hs = self._shuf_r.collidepoint(mx, my)
        pygame.draw.rect(surf, (30, 55, 35) if hs else (18, 32, 20), self._shuf_r, border_radius=6)
        pygame.draw.rect(surf, (80, 145, 90) if hs else (38, 72, 46), self._shuf_r, 2, border_radius=6)
        surf.blit(self._fsm.render('Shuffle', True, (160, 210, 160)),
                  self._fsm.render('Shuffle', True, (160, 210, 160)).get_rect(center=self._shuf_r.center))

        sh = self._fsm.render('Seed (click to edit)', True, (40, 80, 50))
        surf.blit(sh, sh.get_rect(midbottom=(self._seed_r.centerx, self._seed_r.top - 4)))

        hint = self._fsm.render('\u25c4 \u25ba  to browse games   \u00b7   ESC to quit', True, (38, 65, 42))
        surf.blit(hint, hint.get_rect(center=(cx, self._sh - 28)))

    def launch(self, screen: pygame.Surface, action: str) -> str:
        seed = self._seed or (_snake_ss.new_seed() if _snake_ss else 'AAAAAA')
        if action == 'continue' and _snake_ss:
            data = _snake_ss.load()
            if data:
                result = SnakeGame(screen, seed=data.get('seed', seed), save_data=data).run()
                if result != 'restart':
                    return 'menu' if result != 'quit' else 'quit'
        if _snake_ss:
            _snake_ss.delete()
        while True:
            result = SnakeGame(screen, seed=seed).run()
            if result == 'restart':
                continue
            return 'menu' if result != 'quit' else 'quit'


# ---------------------------------------------------------------------------
# Shooter page
# ---------------------------------------------------------------------------
class ShooterPage:
    def __init__(self, sw: int, sh: int):
        self._sw, self._sh = sw, sh

        self._bg = pygame.Surface((sw, sh))
        _shooter_mod._draw_menu_bg(self._bg)

        gf = _shooter_mod._get_font
        self._ft   = gf(62)
        self._fsub = gf(24)
        self._fb   = gf(22)
        self._fsm  = gf(15)
        self._fsd  = gf(17)

        cx, cy = sw // 2, sh // 2
        bw, bh = 300, 58
        self._new_r  = pygame.Rect(cx - bw // 2, cy - 20,       bw, bh)
        self._con_r  = pygame.Rect(cx - bw // 2, cy - 20 + 78,  bw, bh)
        self._seed_r = pygame.Rect(cx - 140,     sh - 110,      220, 36)
        self._shuf_r = pygame.Rect(cx + 88,      sh - 110,      120, 36)

        self._seed    = _shooter_ss.new_seed() if _shooter_ss else 'ABCD1234'
        self._editing = False
        self._sinput  = self._seed

    # ---- internal helpers --------------------------------------------------

    def _draw_btn(self, surf: pygame.Surface, rect: pygame.Rect,
                  label: str, hover: bool, active: bool = True) -> None:
        if not active:
            pygame.draw.rect(surf, (30, 28, 22), rect, border_radius=9)
            pygame.draw.rect(surf, (55, 50, 40), rect, 2, border_radius=9)
            t = self._fb.render(label, True, (70, 65, 55))
        else:
            bgc = (74, 68, 52) if hover else (40, 36, 28)
            bdc = (210, 185, 105) if hover else (95, 86, 64)
            pygame.draw.rect(surf, bgc, rect, border_radius=9)
            pygame.draw.rect(surf, bdc, rect, 2, border_radius=9)
            t = self._fb.render(label, True, (230, 215, 175))
        surf.blit(t, t.get_rect(center=rect.center))

    # ---- public interface --------------------------------------------------

    def handle(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if self._editing:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self._seed = self._sinput.upper() if self._sinput else (
                        _shooter_ss.new_seed() if _shooter_ss else 'ABCD1234')
                    self._editing = False
                elif event.key == pygame.K_BACKSPACE:
                    self._sinput = self._sinput[:-1]
                elif len(self._sinput) < 12 and event.unicode.isalnum():
                    self._sinput = (self._sinput + event.unicode).upper()
                return None
            if event.key == pygame.K_ESCAPE:
                return 'quit'

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._editing:
                if not self._seed_r.collidepoint(event.pos):
                    self._seed = self._sinput.upper() if self._sinput else (
                        _shooter_ss.new_seed() if _shooter_ss else 'ABCD1234')
                    self._editing = False
                return None
            has = _shooter_ss.has_save() if _shooter_ss else False
            if self._new_r.collidepoint(event.pos):
                return 'new_game'
            if self._con_r.collidepoint(event.pos) and has:
                return 'continue'
            if self._shuf_r.collidepoint(event.pos):
                self._seed   = _shooter_ss.new_seed() if _shooter_ss else 'ABCD1234'
                self._sinput = self._seed
            elif self._seed_r.collidepoint(event.pos):
                self._editing = True
                self._sinput  = self._seed
        return None

    def draw(self, surf: pygame.Surface, _: int) -> None:
        cx, cy = self._sw // 2, self._sh // 2
        mx, my = pygame.mouse.get_pos()
        has = _shooter_ss.has_save() if _shooter_ss else False

        surf.blit(self._bg, (0, 0))

        t1 = self._ft.render('THE POWER OF 50', True, (214, 188, 110))
        t2 = self._fsub.render('\u2014 D U N G E O N \u2014', True, (160, 80, 60))
        surf.blit(t1, t1.get_rect(center=(cx, cy - 160)))
        surf.blit(t2, t2.get_rect(center=(cx, cy - 100)))

        best = _shooter_ss.get_best_kills() if _shooter_ss else 0
        if best > 0:
            bs = self._fsm.render(f'Best run: {best} kills', True, (130, 160, 110))
            surf.blit(bs, bs.get_rect(center=(cx, cy - 66)))

        self._draw_btn(surf, self._new_r, '\u25b6  NEW GAME',  self._new_r.collidepoint(mx, my))
        self._draw_btn(surf, self._con_r, '\u27f2  CONTINUE',  self._con_r.collidepoint(mx, my), active=has)

        if has and _shooter_ss:
            sd = _shooter_ss.load()
            if sd:
                info = self._fsm.render(
                    f"  {sd.get('kills', 0)} kills \u00b7 seed {sd.get('seed', '?')}",
                    True, (140, 160, 110))
                surf.blit(info, info.get_rect(midleft=(self._con_r.left + 8, self._con_r.bottom + 8)))

        # Seed field
        pygame.draw.rect(surf, (28, 30, 22) if self._editing else (22, 20, 16), self._seed_r, border_radius=6)
        pygame.draw.rect(surf, (180, 200, 100) if self._editing else (80, 76, 56), self._seed_r, 2, border_radius=6)
        disp = self._sinput if self._editing else self._seed
        if self._editing and (pygame.time.get_ticks() // 500) % 2 == 0:
            disp += '|'
        sl = self._fsd.render(disp, True, (200, 210, 160))
        surf.blit(sl, sl.get_rect(midleft=(self._seed_r.left + 8, self._seed_r.centery)))

        hs = self._shuf_r.collidepoint(mx, my)
        pygame.draw.rect(surf, (58, 54, 40) if hs else (32, 30, 22), self._shuf_r, border_radius=6)
        pygame.draw.rect(surf, (160, 145, 90) if hs else (72, 66, 48), self._shuf_r, 2, border_radius=6)
        surf.blit(self._fsm.render('Shuffle', True, (200, 190, 150)),
                  self._fsm.render('Shuffle', True, (200, 190, 150)).get_rect(center=self._shuf_r.center))

        sh = self._fsm.render('Seed (click to edit)', True, (90, 84, 64))
        surf.blit(sh, sh.get_rect(midbottom=(self._seed_r.centerx, self._seed_r.top - 4)))

        hint = self._fsm.render('\u25c4 \u25ba  to browse games   \u00b7   ESC to quit', True, (70, 65, 50))
        surf.blit(hint, hint.get_rect(center=(cx, self._sh - 28)))

    def launch(self, screen: pygame.Surface, action: str) -> str:
        seed = self._seed or (_shooter_ss.new_seed() if _shooter_ss else 'ABCD1234')
        if action == 'continue' and _shooter_ss:
            data = _shooter_ss.load()
            if data:
                result = ShooterGame(screen, seed=data.get('seed', seed), save_data=data).run()
                return 'menu' if result != 'quit' else 'quit'
        result = ShooterGame(screen, seed=seed).run()
        return 'menu' if result != 'quit' else 'quit'


# ---------------------------------------------------------------------------
# Carousel helpers
# ---------------------------------------------------------------------------
def _page_x(page_idx: int, scroll: float, n: int, w: int) -> int:
    """Screen x position for a page, with circular wrapping."""
    offset = (page_idx - scroll) % n
    if offset >= n / 2:
        offset -= n
    return int(offset * w)


# ---------------------------------------------------------------------------
# Main carousel loop
# ---------------------------------------------------------------------------
def run(screen: pygame.Surface) -> str:
    W, H = screen.get_size()
    N = 2
    pages      = [SnakePage(W, H), ShooterPage(W, H)]
    page_surfs = [pygame.Surface((W, H)) for _ in pages]

    scroll        = 0.0   # current visual position (unbounded float)
    scroll_target = 0.0   # target position (integer steps, unbounded)
    frame         = 0
    clock         = pygame.time.Clock()

    while True:
        clock.tick(60)
        frame += 1

        # Ease scroll towards target
        diff    = scroll_target - scroll
        scroll += diff * 0.14
        if abs(diff) < 0.002:
            scroll = scroll_target

        animating = abs(scroll_target - scroll) > 0.01
        active_idx = int(round(scroll_target)) % N
        active     = pages[active_idx]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if animating:
                continue

            if event.type == pygame.KEYDOWN:
                editing = getattr(active, '_editing', False)
                if event.key == pygame.K_LEFT and not editing:
                    scroll_target -= 1.0   # slide right: prev page comes from left
                    continue
                if event.key == pygame.K_RIGHT and not editing:
                    scroll_target += 1.0   # slide left: next page comes from right
                    continue
                action = active.handle(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = active.handle(event)
            else:
                continue

            if action == 'quit':
                return 'quit'
            if action in ('play', 'continue', 'new_game'):
                result = active.launch(screen, action)
                if result == 'quit':
                    return 'quit'

        # Draw each visible page to its surface
        for i, (page, psurf) in enumerate(zip(pages, page_surfs)):
            x = _page_x(i, scroll % N, N, W)
            if abs(x) < W:
                page.draw(psurf, frame)

        # Composite pages onto screen
        screen.fill((0, 0, 0))
        for i, psurf in enumerate(page_surfs):
            x = _page_x(i, scroll % N, N, W)
            if abs(x) < W:
                screen.blit(psurf, (x, 0))

        # Page indicator dots
        dot_y      = H - 14
        dot_gap    = 20
        dot_x0     = W // 2 - (N - 1) * dot_gap // 2
        norm_scroll = scroll % N
        for i in range(N):
            raw = (i - norm_scroll) % N
            if raw >= N / 2:
                raw -= N
            if i == active_idx:
                col, rad = (220, 215, 180), 6
            else:
                col, rad = (70, 66, 52), 4
            pygame.draw.circle(screen, col, (dot_x0 + i * dot_gap, dot_y), rad)

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption('The Power of 50')
    run(screen)
    pygame.quit()
    sys.exit(0)
