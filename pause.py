"""Pause overlay: opens on Esc, freezes the game underneath."""
import pygame

import theme
from config import SCREEN_WIDTH, SCREEN_HEIGHT, S


class PauseOverlay:
    def __init__(self):
        self._title_font = None
        self._option_font = None
        self._small_font = None
        self.options = [
            ("resume",      "Resume"),
            ("restart",     "Restart Match"),
            ("settings",    "Settings"),
            ("how_to_play", "How To Play"),
            ("quit_menu",   "Quit to Menu"),
        ]
        self.selected = 0
        self.hovered_index = -1
        self._fade_t = 0.0

    def _ensure_fonts(self):
        if self._title_font is None:
            import typography as typo
            self._title_font = typo.display_bold(S(42))
            self._option_font = typo.body_bold(S(26))
            self._small_font = typo.body(S(16))

    def reset(self):
        self.selected = 0
        self.hovered_index = -1
        self._fade_t = 0.0

    def update(self, dt):
        self._fade_t = min(1.0, self._fade_t + dt * 4.0)

    def draw(self, screen):
        self._ensure_fonts()
        t = theme.active()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(160 * self._fade_t)))
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = S(480), S(460)
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_h // 2
        slide_y = int((1.0 - self._fade_t) * S(30))
        panel_y -= slide_y

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*t.panel_bg, 230), panel.get_rect(), border_radius=S(14))
        pygame.draw.rect(panel, t.brass_500, panel.get_rect(), max(1, S(2)), border_radius=S(14))
        inner = pygame.Rect(S(8), S(8), panel_w - S(16), panel_h - S(16))
        pygame.draw.rect(panel, t.brass_700, inner, max(1, S(1)), border_radius=S(10))
        screen.blit(panel, (panel_x, panel_y))

        title_surf = self._title_font.render("PAUSED", True, t.brass_300)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + S(60)))
        screen.blit(title_surf, title_rect)

        rule_y = panel_y + S(100)
        pygame.draw.line(
            screen, t.brass_700,
            (panel_x + S(60), rule_y), (panel_x + panel_w - S(60), rule_y), max(1, S(1)),
        )

        start_y = panel_y + S(140)
        spacing = S(50)
        self._option_rects = []
        for i, (key, label) in enumerate(self.options):
            y = start_y + i * spacing
            is_focus = (i == self.selected) or (i == self.hovered_index)
            color = t.brass_300 if is_focus else t.text_white
            label_surf = self._option_font.render(label, True, color)
            rect = label_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            self._option_rects.append((rect, key))
            if is_focus:
                bar = pygame.Rect(rect.x - S(18), rect.y, S(4), rect.height)
                pygame.draw.rect(screen, t.brass_300, bar, border_radius=S(2))
                bar2 = pygame.Rect(rect.right + S(14), rect.y, S(4), rect.height)
                pygame.draw.rect(screen, t.brass_300, bar2, border_radius=S(2))
            screen.blit(label_surf, rect)

        hint_surf = self._small_font.render(
            "Esc — Resume    ↑↓ — Navigate    Enter — Select",
            True, t.text_dim,
        )
        screen.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_h - S(28))))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
                return ("nav", None)
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
                return ("nav", None)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return ("select", self.options[self.selected][0])
            if event.key == pygame.K_ESCAPE:
                return ("select", "resume")
        if event.type == pygame.MOUSEMOTION:
            self.hovered_index = -1
            for i, (rect, _key) in enumerate(getattr(self, "_option_rects", [])):
                if rect.collidepoint(event.pos):
                    self.hovered_index = i
                    self.selected = i
                    return ("nav", None)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (rect, key) in enumerate(getattr(self, "_option_rects", [])):
                if rect.collidepoint(event.pos):
                    return ("select", key)
        return (None, None)
