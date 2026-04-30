import math
import pygame
from config import (
    CORNER_RADIUS, BLACK, GOLD, GOLD_HOVER, TEXT_WHITE, TEXT_DIM,
    BG_DARK, SWAP_GREEN, SWAP_GREEN_HOVER, PEEK_BLUE, PEEK_BLUE_HOVER,
    DECLARE_RED, DECLARE_RED_HOVER, CANCEL_GRAY, CANCEL_GRAY_HOVER,
    DISCARD_ORANGE, DISCARD_ORANGE_HOVER, PAIR_TEAL, PAIR_TEAL_HOVER,
)

BUTTON_VARIANTS = {
    'primary': {'color': SWAP_GREEN, 'hover': SWAP_GREEN_HOVER},
    'secondary': {'color': (55, 55, 60), 'hover': (75, 75, 80)},
    'gold': {'color': GOLD, 'hover': GOLD_HOVER},
    'red': {'color': DECLARE_RED, 'hover': DECLARE_RED_HOVER},
    'blue': {'color': PEEK_BLUE, 'hover': PEEK_BLUE_HOVER},
    'orange': {'color': DISCARD_ORANGE, 'hover': DISCARD_ORANGE_HOVER},
    'teal': {'color': PAIR_TEAL, 'hover': PAIR_TEAL_HOVER},
    'cancel': {'color': CANCEL_GRAY, 'hover': CANCEL_GRAY_HOVER},
}


class Button:
    def __init__(self, cx, cy, w, h, text, variant='primary', font=None,
                 text_color=None, radius=None, glow=False):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.text = text
        self.variant = variant
        self.font = font
        self.text_color = text_color or TEXT_WHITE
        self.radius = radius or 8
        self.glow = glow
        self.is_hovered = False
        self.is_pressed = False
        self._hover_t = 0.0
        self._press_t = 0.0
        self._glow_phase = 0.0

        v = BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS['primary'])
        self.base_color = v['color']
        self.hover_color = v['hover']

    @property
    def rect(self):
        lift = int(2 * self._hover_t) if not self.is_pressed else 0
        return pygame.Rect(
            self.cx - self.w // 2,
            self.cy - self.h // 2 - lift,
            self.w, self.h
        )

    def update(self, dt, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.is_hovered else 0.0
        self._hover_t += (target - self._hover_t) * min(dt * 12, 1.0)
        self._glow_phase += dt * 3

    def on_press(self):
        self.is_pressed = True
        self._press_t = 0.0

    def on_release(self):
        self.is_pressed = False

    def draw(self, screen):
        rect = self.rect
        color = self.hover_color if self._hover_t > 0.5 else self.base_color

        if self.is_pressed:
            color = tuple(max(c - 30, 0) for c in color)

        shadow_offset = 4 - int(2 * self._hover_t)
        shadow_surf = pygame.Surface((self.w + 8, self.h + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60),
                         (4, 6, self.w, self.h), border_radius=self.radius)
        screen.blit(shadow_surf, (rect.x - 4, rect.y + shadow_offset))

        pygame.draw.rect(screen, color, rect, border_radius=self.radius)

        c_r = max(color[0] - 30, 0)
        c_g = max(color[1] - 30, 0)
        c_b = max(color[2] - 30, 0)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.left + 3, rect.bottom - 3),
                         (rect.right - 3, rect.bottom - 3), 2)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.right - 3, rect.top + 3),
                         (rect.right - 3, rect.bottom - 3), 2)

        l_r = min(color[0] + 35, 255)
        l_g = min(color[1] + 35, 255)
        l_b = min(color[2] + 35, 255)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 3, rect.top + 3),
                         (rect.right - 3, rect.top + 3), 2)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 3, rect.top + 3),
                         (rect.left + 3, rect.bottom - 3), 2)

        if self.glow:
            pulse = abs(math.sin(self._glow_phase)) * 0.3 + 0.7
            glow_alpha = int(50 * pulse)
            glow_rect = rect.inflate(8, 8)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GOLD, glow_alpha),
                             glow_surf.get_rect(), border_radius=self.radius + 4)
            screen.blit(glow_surf, (glow_rect.x, glow_rect.y))

        pygame.draw.rect(screen, (20, 20, 25), rect, width=1, border_radius=self.radius)

        if self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class ToggleButton:
    def __init__(self, cx, cy, w, h, text, active=False, font=None):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.text = text
        self.active = active
        self.font = font
        self._hover_t = 0.0
        self._glow_phase = 0.0

    @property
    def rect(self):
        return pygame.Rect(self.cx - self.w // 2, self.cy - self.h // 2, self.w, self.h)

    def update(self, dt, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if hovered else 0.0
        self._hover_t += (target - self._hover_t) * min(dt * 12, 1.0)
        self._glow_phase += dt * 3

    def draw(self, screen):
        rect = self.rect
        if self.active:
            color = GOLD
            text_color = BG_DARK
        else:
            color = (50, 50, 55)
            text_color = TEXT_DIM
            if self._hover_t > 0.5:
                color = (70, 70, 75)
                text_color = TEXT_WHITE

        shadow_surf = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 50), (2, 3, self.w, self.h), border_radius=6)
        screen.blit(shadow_surf, (rect.x - 2, rect.y + 3))

        pygame.draw.rect(screen, color, rect, border_radius=6)

        c_r = max(color[0] - 25, 0)
        c_g = max(color[1] - 25, 0)
        c_b = max(color[2] - 25, 0)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.left + 2, rect.bottom - 2), (rect.right - 2, rect.bottom - 2), 2)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.right - 2, rect.top + 2), (rect.right - 2, rect.bottom - 2), 2)

        l_r = min(color[0] + 35, 255)
        l_g = min(color[1] + 35, 255)
        l_b = min(color[2] + 35, 255)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 2, rect.top + 2), (rect.right - 2, rect.top + 2), 2)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 2, rect.top + 2), (rect.left + 2, rect.bottom - 2), 2)

        if self.active:
            pulse = abs(math.sin(self._glow_phase)) * 0.2 + 0.8
            glow_alpha = int(40 * pulse)
            glow_rect = rect.inflate(6, 6)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GOLD, glow_alpha),
                             glow_surf.get_rect(), border_radius=8)
            screen.blit(glow_surf, (glow_rect.x, glow_rect.y))

        pygame.draw.rect(screen, (20, 20, 25), rect, width=1, border_radius=6)

        if self.font:
            text_surf = self.font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class PillButton:
    def __init__(self, cx, cy, w, h, text, variant='primary', font=None,
                 text_color=None, radius=None):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h
        self.text = text
        self.variant = variant
        self.font = font
        self.text_color = text_color or TEXT_WHITE
        self.radius = radius or h // 2
        self._hover_t = 0.0
        self._glow_phase = 0.0

        v = BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS['primary'])
        self.base_color = v['color']
        self.hover_color = v['hover']

    @property
    def rect(self):
        return pygame.Rect(self.cx - self.w // 2, self.cy - self.h // 2, self.w, self.h)

    def update(self, dt, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if hovered else 0.0
        self._hover_t += (target - self._hover_t) * min(dt * 12, 1.0)
        self._glow_phase += dt * 3

    def draw(self, screen):
        rect = self.rect
        color = self.hover_color if self._hover_t > 0.5 else self.base_color

        shadow_surf = pygame.Surface((self.w + 6, self.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 50), (3, 4, self.w, self.h), border_radius=self.radius)
        screen.blit(shadow_surf, (rect.x - 3, rect.y + 4))

        pygame.draw.rect(screen, color, rect, border_radius=self.radius)

        c_r = max(color[0] - 25, 0)
        c_g = max(color[1] - 25, 0)
        c_b = max(color[2] - 25, 0)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.left + 3, rect.bottom - 3), (rect.right - 3, rect.bottom - 3), 2)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (rect.right - 3, rect.top + 3), (rect.right - 3, rect.bottom - 3), 2)

        l_r = min(color[0] + 35, 255)
        l_g = min(color[1] + 35, 255)
        l_b = min(color[2] + 35, 255)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 3, rect.top + 3), (rect.right - 3, rect.top + 3), 2)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (rect.left + 3, rect.top + 3), (rect.left + 3, rect.bottom - 3), 2)

        pygame.draw.rect(screen, (20, 20, 25), rect, width=1, border_radius=self.radius)

        if self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)
