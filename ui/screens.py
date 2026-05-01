import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_GREEN, BG_DARK, CARD_WHITE, CARD_BACK_BLUE,
    CARD_BACK_PATTERN, CARD_SHADOW, BLACK, RED, GOLD, TEXT_WHITE, TEXT_BLACK,
    TEXT_DIM, HIGHLIGHT, DIM, PANEL_BG, PANEL_BORDER, POWER_GLOW, EMPTY_SLOT,
    DECLARE_RED, DECLARE_RED_HOVER, SWAP_GREEN, SWAP_GREEN_HOVER,
    PEEK_BLUE, PEEK_BLUE_HOVER,
    DISCARD_ORANGE, DISCARD_ORANGE_HOVER, PAIR_TEAL, PAIR_TEAL_HOVER,
    CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS, CARD_SPREAD, HAND_SIZE,
    DECK_CENTER, DRAWN_CARD_POS, DISCARD_POS,
    PLAYER_BOTTOM, PLAYER_TOP, PLAYER_LEFT, PLAYER_RIGHT,
    TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, UI_FONT_SIZE, LOG_FONT_SIZE,
    SMALL_FONT_SIZE, CARD_FONT_SIZE, CARD_BIG_FONT_SIZE,
    S,
)


class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=TEXT_WHITE):
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color

        s2 = max(1, S(2))
        s3 = max(1, S(3))
        s4 = max(2, S(4))

        shadow_surf = pygame.Surface((self.rect.width + s4, self.rect.height + s4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (s2, s3, self.rect.width, self.rect.height), border_radius=CORNER_RADIUS)
        screen.blit(shadow_surf, (self.rect.x - s2, self.rect.y + s3))

        pygame.draw.rect(screen, color, self.rect, border_radius=CORNER_RADIUS)

        c_r = max(color[0] - 35, 0)
        c_g = max(color[1] - 35, 0)
        c_b = max(color[2] - 35, 0)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (self.rect.left + s3, self.rect.bottom - s3),
                         (self.rect.right - s3, self.rect.bottom - s3), s2)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (self.rect.right - s3, self.rect.top + s3),
                         (self.rect.right - s3, self.rect.bottom - s3), s2)
        l_r = min(color[0] + 40, 255)
        l_g = min(color[1] + 40, 255)
        l_b = min(color[2] + 40, 255)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (self.rect.left + s3, self.rect.top + s3),
                         (self.rect.right - s3, self.rect.top + s3), s2)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (self.rect.left + s3, self.rect.top + s3),
                         (self.rect.left + s3, self.rect.bottom - s3), s2)

        pygame.draw.rect(screen, BLACK, self.rect, width=s2, border_radius=CORNER_RADIUS)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mouse_pos):
            return True
        return False

    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


import typography as typo


def _get_font(size, bold=False):
    """Legacy helper — defaults to body face. Most screens now call typo
    families directly (display/header/body) for proper typographic hierarchy."""
    return typo.body_bold(size) if bold else typo.body(size)


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = typo.display_bold(int(TITLE_FONT_SIZE * 1.4))
        self.subtitle_font = typo.header_italic(int(SUBTITLE_FONT_SIZE * 1.1))
        self.button_font = typo.body_bold(UI_FONT_SIZE)
        cx = SCREEN_WIDTH // 2
        self.play_button = Button(cx, S(528), S(320), S(56), "Play", SWAP_GREEN, SWAP_GREEN_HOVER)
        self.tutorial_button = Button(cx, S(590), S(320), S(44), "Tutorial", PEEK_BLUE, PEEK_BLUE_HOVER)
        self.how_to_button = Button(cx, S(640), S(320), S(44), "How To Play", PAIR_TEAL, PAIR_TEAL_HOVER)
        self.profile_button = Button(cx, S(690), S(320), S(44), "Profile & Stats", DISCARD_ORANGE, DISCARD_ORANGE_HOVER)
        self.settings_button = Button(cx, S(740), S(320), S(44), "Settings", (110, 90, 50), (140, 115, 65))
        self.quit_button = Button(cx, S(790), S(320), S(44), "Quit", DECLARE_RED, DECLARE_RED_HOVER)
        self.new_game_button = self.play_button
        self.buttons = [self.play_button, self.tutorial_button, self.how_to_button,
                        self.profile_button, self.settings_button, self.quit_button]
        self._t = 0.0
        self._shuffle_t = 0.0
        self._card_cache = {}

    def start_shuffle(self):
        self._shuffle_t = 0.0

    def _get_card_surface(self, angle):
        """Return cached (card, shadow) surfaces rotated to `angle`.
        Re-rendering paint_back + smoothscale + blur every frame was the
        source of the menu's idle lag; we now build each rotation lazily
        and cache it."""
        import card_render
        key = round(angle, 1)
        cached = self._card_cache.get(key)
        if cached is not None:
            return cached
        back_surf = card_render.paint_back("classic", CARD_WIDTH, CARD_HEIGHT)
        scaled = pygame.transform.smoothscale(
            back_surf, (int(CARD_WIDTH * 1.4), int(CARD_HEIGHT * 1.4))
        )
        if angle:
            scaled = pygame.transform.rotate(scaled, angle)
        silhouette = scaled.copy()
        silhouette.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sw, sh = silhouette.get_size()
        blur_w = max(1, sw // 5)
        blur_h = max(1, sh // 5)
        soft = pygame.transform.smoothscale(
            pygame.transform.smoothscale(silhouette, (blur_w, blur_h)),
            (sw, sh),
        )
        soft.set_alpha(110)
        self._card_cache[key] = (scaled, soft)
        return scaled, soft

    def _shuffle_card_transform(self, idx, target_x, target_y, target_angle):
        """Returns (x, y, angle) for card `idx` at current shuffle progress.

        Three phases riffle shuffle:
          0.00-0.30s   split into two halves
          0.30-0.60s   collapse back together (interleaved)
          0.60-1.10s   fan out to final position
        After 1.10s the card sits at its final fan slot with a gentle sway.
        """
        import math as _math
        deck_x = SCREEN_WIDTH // 2
        deck_y = S(365)
        t = self._shuffle_t
        side = -1 if idx % 2 == 0 else 1

        split_offset = S(220)
        rise_amt = S(35)
        interleave_step = S(5)

        if t < 0.30:
            a = t / 0.30
            eased = 1 - (1 - a) ** 2
            offset = split_offset * eased * side
            x = deck_x + offset
            y = deck_y - rise_amt * eased
            angle = -18 * side * eased
        elif t < 0.60:
            a = (t - 0.30) / 0.30
            eased = 1 - (1 - a) ** 3
            offset = split_offset * (1 - eased) * side
            x = deck_x + offset
            y = deck_y - rise_amt + rise_amt * eased + (idx - 2) * interleave_step * eased
            angle = -18 * side * (1 - eased)
        elif t < 1.10:
            a = (t - 0.60) / 0.50
            eased = 1 - (1 - a) ** 3
            x = deck_x + (target_x - deck_x) * eased
            y = deck_y + (target_y - deck_y) * eased
            angle = target_angle * eased
        else:
            sway = _math.sin(self._t * 1.5) * S(3)
            x = target_x
            y = target_y + sway * max(0.0, 1.0 - abs(idx - 2) / 2.0)
            angle = target_angle

        return x, y, angle

    def _draw_card_back_medallion(self, surface, cx, cy, scale=1.0):
        w, h = int(44 * scale), int(30 * scale)
        hw, hh = w // 2, h // 2
        fill = (50, 85, 155)
        hi = (190, 210, 240)
        lo = (30, 55, 120)
        oval_rect = pygame.Rect(cx - hw, cy - hh, w, h)
        pygame.draw.ellipse(surface, fill, oval_rect)
        pygame.draw.ellipse(surface, hi, oval_rect, 1)
        left_curl = [
            (cx - hw, cy),
            (cx - hw - int(8 * scale), cy - int(4 * scale)),
            (cx - hw - int(6 * scale), cy - int(10 * scale)),
            (cx - hw + int(2 * scale), cy - int(8 * scale)),
        ]
        right_curl = [
            (cx + hw, cy),
            (cx + hw + int(8 * scale), cy - int(4 * scale)),
            (cx + hw + int(6 * scale), cy - int(10 * scale)),
            (cx + hw - int(2 * scale), cy - int(8 * scale)),
        ]
        pygame.draw.lines(surface, fill, False, left_curl, 2)
        pygame.draw.lines(surface, hi, False, left_curl, 1)
        pygame.draw.lines(surface, fill, False, right_curl, 2)
        pygame.draw.lines(surface, hi, False, right_curl, 1)
        inner_diamond = [
            (cx, cy - int(10 * scale)), (cx + int(8 * scale), cy),
            (cx, cy + int(10 * scale)), (cx - int(8 * scale), cy)
        ]
        pygame.draw.polygon(surface, lo, inner_diamond)
        pygame.draw.polygon(surface, hi, inner_diamond, 1)
        dot = pygame.Rect(cx - 2, cy - 2, 4, 4)
        pygame.draw.rect(surface, hi, dot, border_radius=1)

    def _draw_menu_card_back(self, cx, cy, angle=0):
        surf = pygame.Surface((CARD_WIDTH + 20, CARD_HEIGHT + 20), pygame.SRCALPHA)
        rect = pygame.Rect(10, 10, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surf, CARD_BACK_BLUE, rect, border_radius=CORNER_RADIUS)
        inner = pygame.Rect(16, 16, CARD_WIDTH - 12, CARD_HEIGHT - 12)
        pygame.draw.rect(surf, CARD_BACK_PATTERN, inner, border_radius=CORNER_RADIUS - 2)
        line_color = (50, 90, 170, 40)
        inner_w, inner_h = CARD_WIDTH - 20, CARD_HEIGHT - 20
        cross_surf = pygame.Surface((inner_w, inner_h), pygame.SRCALPHA)
        for i in range(0, max(inner_w, inner_h), 12):
            if i < inner_w:
                pygame.draw.line(cross_surf, line_color, (i, 0), (i, inner_h))
            if i < inner_h:
                pygame.draw.line(cross_surf, line_color, (0, i), (inner_w, i))
        surf.blit(cross_surf, (10, 10))
        self._draw_card_back_medallion(surf, 10 + CARD_WIDTH // 2, 10 + CARD_HEIGHT // 2)
        pygame.draw.rect(surf, TEXT_WHITE, rect, 1, border_radius=CORNER_RADIUS)
        if angle != 0:
            surf = pygame.transform.rotate(surf, angle)
        self.screen.blit(surf, (cx - (CARD_WIDTH + 20) // 2, cy - (CARD_HEIGHT + 20) // 2))

    def update(self, dt):
        self._t += dt
        self._shuffle_t += dt

    def _build_static_layer(self, th):
        """Pre-render the felt gradient + flourish + subtitle.
        These don't depend on time, so we build them once per theme.
        Title is rendered as a separate (smaller) layer to avoid a
        full-screen SRCALPHA blit each frame."""
        layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            t = i / max(1, SCREEN_HEIGHT - 1)
            r = int(th.felt_rim[0] * (1 - t * 0.4) + th.felt_deep[0] * t * 0.6)
            g = int(th.felt_rim[1] * (1 - t * 0.4) + th.felt_deep[1] * t * 0.6)
            b = int(th.felt_rim[2] * (1 - t * 0.4) + th.felt_deep[2] * t * 0.6)
            pygame.draw.line(layer, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        cx = SCREEN_WIDTH // 2
        flourish_y = S(178)
        line_w = S(220)
        line_thickness = max(1, S(1))
        pygame.draw.line(layer, th.brass_500, (cx - line_w, flourish_y),
                         (cx - S(30), flourish_y), line_thickness)
        pygame.draw.line(layer, th.brass_500, (cx + S(30), flourish_y),
                         (cx + line_w, flourish_y), line_thickness)
        pygame.draw.polygon(layer, th.brass_500,
                            [(cx, flourish_y - S(5)), (cx - S(12), flourish_y),
                             (cx, flourish_y + S(5)), (cx + S(12), flourish_y)])

        subtitle_surf = self.subtitle_font.render(
            "A Card Game of Memory & Strategy", True, th.text_dim)
        layer.blit(subtitle_surf, subtitle_surf.get_rect(center=(cx, S(210))))

        return layer

    def _build_title_layer(self, th):
        """3-pass shadowed DECLARE title rendered once, sized to the title bbox."""
        base = typo.render_with_letter_spacing(
            self.title_font, "DECLARE", th.brass_300, spacing_px=S(10),
        )
        bw, bh = base.get_size()
        pad = S(16)
        layer_w = bw + pad * 2
        layer_h = bh + pad * 2
        layer = pygame.Surface((layer_w, layer_h), pygame.SRCALPHA)
        cx_local = layer_w // 2
        cy_local = layer_h // 2 - S(3)
        shadow_offsets = (S(6), S(3), 0)
        for shadow_offset, alpha in zip(shadow_offsets, (60, 110, 255)):
            t_color = th.brass_300 if alpha == 255 else th.brass_700
            t_surf = typo.render_with_letter_spacing(
                self.title_font, "DECLARE", t_color, spacing_px=S(10),
            )
            t_surf.set_alpha(alpha)
            r = t_surf.get_rect(center=(cx_local + shadow_offset - S(3), cy_local + shadow_offset - S(3)))
            layer.blit(t_surf, r)
        self._title_pos = (SCREEN_WIDTH // 2 - layer_w // 2, S(130) - layer_h // 2)
        return layer

    def draw(self):
        import theme as theme_mod
        th = theme_mod.active()

        cache_key = (id(th), getattr(th, 'name', 'default'))
        if getattr(self, '_static_key', None) != cache_key:
            self._static_layer = self._build_static_layer(th)
            self._title_layer = self._build_title_layer(th)
            self._static_key = cache_key
            self._card_cache = {}
        self.screen.blit(self._static_layer, (0, 0))

        # lamp glow removed

        card_fan = [(S(-180), S(380), -16), (S(-90), S(370), -8),
                    (0, S(365), 0), (S(90), S(370), 8), (S(180), S(380), 16)]
        shuffling = self._shuffle_t < 1.10
        shadow_dx = S(3)
        shadow_dy = S(6)
        for idx, (dx, cy, angle) in enumerate(card_fan):
            target_x = SCREEN_WIDTH // 2 + dx
            target_y = cy
            cx, cy_now, draw_angle = self._shuffle_card_transform(idx, target_x, target_y, angle)
            if shuffling:
                quantized = round(draw_angle / 2.0) * 2.0
            else:
                quantized = angle
            scaled, soft = self._get_card_surface(quantized)
            sw, sh = scaled.get_size()
            self.screen.blit(soft, (cx - sw // 2 + shadow_dx, cy_now - sh // 2 + shadow_dy))
            self.screen.blit(scaled, (cx - sw // 2, cy_now - sh // 2))

        self.screen.blit(self._title_layer, self._title_pos)

        for button in self.buttons:
            button.draw(self.screen, self.button_font)

        if not getattr(self, '_footer_surf', None) or getattr(self, '_footer_color', None) != th.text_muted:
            self._footer_surf = self.button_font.render("v1.0 — Built with care", True, th.text_muted)
            self._footer_color = th.text_muted
        self.screen.blit(self._footer_surf, (S(16), SCREEN_HEIGHT - S(28)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.update_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_button.is_clicked(event.pos):
                return 'new_game'
            if self.tutorial_button.is_clicked(event.pos):
                return 'tutorial'
            if self.how_to_button.is_clicked(event.pos):
                return 'how_to_play'
            if self.profile_button.is_clicked(event.pos):
                return 'profile'
            if self.settings_button.is_clicked(event.pos):
                return 'settings'
            if self.quit_button.is_clicked(event.pos):
                return 'quit'
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return 'new_game'
            if event.key == pygame.K_t:
                return 'tutorial'
            if event.key == pygame.K_h:
                return 'how_to_play'
            if event.key == pygame.K_p:
                return 'profile'
            if event.key == pygame.K_s:
                return 'settings'
            if event.key == pygame.K_q:
                return 'quit'
        return None


class SetupScreen:
    AI_PERSONAS = [
        {"name": "Marcus",  "diff": "medium", "quip": "Plays the long game."},
        {"name": "Vivian",  "diff": "hard",   "quip": "Counts every card."},
        {"name": "Cassio",  "diff": "easy",   "quip": "All bluff, no plan."},
        {"name": "Reine",   "diff": "hard",   "quip": "Cold and patient."},
        {"name": "Tobias",  "diff": "medium", "quip": "Loves a risky pair."},
        {"name": "Iliana",  "diff": "medium", "quip": "Reads faces like books."},
    ]

    DIFFICULTY_LABEL = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}

    def __init__(self, screen, num_players=2):
        self.screen = screen
        self.title_font = typo.display_bold(int(TITLE_FONT_SIZE * 1.1))
        self.subtitle_font = typo.header_italic(SUBTITLE_FONT_SIZE)
        self.label_font = typo.body(UI_FONT_SIZE)
        self.button_font = typo.body_bold(UI_FONT_SIZE)
        self.input_font = typo.body(SMALL_FONT_SIZE + S(2))
        self.small_font = typo.body(S(13))
        self.section_font = typo.header_bold(S(14))
        self.num_players = num_players
        self.players_config = []
        import random as _r
        ai_pool = _r.sample(self.AI_PERSONAS, k=min(4, len(self.AI_PERSONAS)))
        for i in range(4):
            if i == 0:
                self.players_config.append({
                    "name": "You", "is_human": True, "difficulty": "medium",
                    "quip": "",
                })
            else:
                persona = ai_pool[i - 1]
                self.players_config.append({
                    "name": persona["name"],
                    "is_human": False,
                    "difficulty": persona["diff"],
                    "quip": persona["quip"],
                })
        self.active_input = None
        self._t = 0.0

        self.player_count_rects = {}
        self._diff_rects = {}
        self._toggle_rects = {}
        self._name_rects = {}

        self.start_button = Button(SCREEN_WIDTH // 2, S(800), S(320), S(56),
                                   "Start Match", SWAP_GREEN, SWAP_GREEN_HOVER)
        self.back_button = Button(S(120), S(60), S(140), S(40),
                                  "← Back", DECLARE_RED, DECLARE_RED_HOVER)

    def _draw_background(self):
        import theme as theme_mod
        import math as _math
        th = theme_mod.active()
        self._t += 1 / 60
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            t = i / max(1, SCREEN_HEIGHT - 1)
            r = int(th.felt_rim[0] * (1 - t * 0.4) + th.felt_deep[0] * t * 0.6)
            g = int(th.felt_rim[1] * (1 - t * 0.4) + th.felt_deep[1] * t * 0.6)
            b = int(th.felt_rim[2] * (1 - t * 0.4) + th.felt_deep[2] * t * 0.6)
            pygame.draw.line(bg, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        self.screen.blit(bg, (0, 0))
        # lamp glow removed

    def draw(self):
        import theme as theme_mod
        th = theme_mod.active()
        self._draw_background()

        for offset, alpha in ((S(4), 70), (S(2), 130), (0, 255)):
            t_color = th.brass_300 if alpha == 255 else th.brass_700
            t_surf = typo.render_with_letter_spacing(
                self.title_font, "SETUP THE TABLE", t_color, spacing_px=S(4),
            )
            t_surf.set_alpha(alpha)
            self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset, S(100) + offset)))

        sub = self.subtitle_font.render("Choose your seats — name yourself, set opponents.",
                                          True, th.text_dim)
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, S(154))))

        cy = S(210)
        sec = self.section_font.render("NUMBER OF PLAYERS", True, th.brass_300)
        self.screen.blit(sec, sec.get_rect(center=(SCREEN_WIDTH // 2, cy)))
        cy += S(30)
        self.player_count_rects = {}
        bw, bh = S(90), S(50)
        spacing = S(14)
        total_w = bw * 3 + spacing * 2
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        for idx, count in enumerate([2, 3, 4]):
            r = pygame.Rect(start_x + idx * (bw + spacing), cy, bw, bh)
            self.player_count_rects[count] = r
            active = (count == self.num_players)
            color = th.brass_500 if active else (50, 50, 50)
            border = th.brass_300 if active else (90, 90, 90)
            pygame.draw.rect(self.screen, color, r, border_radius=S(10))
            pygame.draw.rect(self.screen, border, r, max(1, S(2)), border_radius=S(10))
            ts = self.title_font.render(str(count), True, th.text_white if active else th.text_dim)
            self.screen.blit(ts, ts.get_rect(center=r.center))

        seat_top = S(360)
        seat_h = S(96)
        seat_gap = S(12)
        seat_w = S(920)
        seat_x = SCREEN_WIDTH // 2 - seat_w // 2
        self._diff_rects = {}
        self._toggle_rects = {}
        self._name_rects = {}
        for i in range(self.num_players):
            y = seat_top + i * (seat_h + seat_gap)
            self._draw_seat_card(i, seat_x, y, seat_w, seat_h, th)

        self.start_button.draw(self.screen, self.button_font)
        self.back_button.draw(self.screen, self.input_font)

    def _draw_seat_card(self, i, x, y, w, h, th):
        config = self.players_config[i]
        is_human = config["is_human"]

        shadow = pygame.Surface((w + S(8), h + S(8)), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), (S(4), S(6), w, h), border_radius=S(12))
        self.screen.blit(shadow, (x - S(4), y))

        card = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_color = (28, 38, 32, 240) if is_human else (28, 32, 42, 240)
        pygame.draw.rect(card, bg_color, card.get_rect(), border_radius=S(12))
        accent_w = S(6)
        accent_color = th.you_cyan if is_human else th.brass_500
        pygame.draw.rect(card, accent_color, pygame.Rect(0, 0, accent_w, h),
                         border_top_left_radius=S(12), border_bottom_left_radius=S(12))
        pygame.draw.rect(card, th.brass_700, card.get_rect(), max(1, S(1)), border_radius=S(12))
        self.screen.blit(card, (x, y))

        avatar_x = x + S(38)
        avatar_y = y + h // 2
        avatar_r = S(26)
        if is_human:
            pygame.draw.circle(self.screen, (40, 90, 100), (avatar_x, avatar_y), avatar_r)
            pygame.draw.circle(self.screen, th.you_cyan, (avatar_x, avatar_y), avatar_r, max(1, S(2)))
        else:
            pygame.draw.circle(self.screen, (60, 50, 30), (avatar_x, avatar_y), avatar_r)
            pygame.draw.circle(self.screen, th.brass_300, (avatar_x, avatar_y), avatar_r, max(1, S(2)))
        initial_font = typo.header_bold(S(26))
        initial = initial_font.render(config["name"][0].upper() if config["name"] else "?",
                                       True, th.text_white)
        self.screen.blit(initial, initial.get_rect(center=(avatar_x, avatar_y)))

        seat_label = self.small_font.render(f"SEAT {i + 1}", True, th.brass_300)
        self.screen.blit(seat_label, (x + S(78), y + S(16)))

        name_x = x + S(78)
        name_y = y + S(32)
        name_w = S(260)
        name_h = S(32)
        name_rect = pygame.Rect(name_x, name_y, name_w, name_h)
        self._name_rects[i] = name_rect
        focus = (self.active_input == i)
        pygame.draw.rect(self.screen, (244, 236, 216), name_rect, border_radius=S(6))
        pygame.draw.rect(self.screen, th.brass_300 if focus else (140, 130, 100),
                         name_rect, max(1, S(2)), border_radius=S(6))
        n_surf = self.input_font.render(config["name"], True, (30, 30, 30))
        self.screen.blit(n_surf, (name_rect.x + S(10), name_rect.y + S(7)))
        if focus:
            cursor_x = name_rect.x + S(10) + n_surf.get_width() + 1
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(self.screen, (30, 30, 30),
                                 (cursor_x, name_rect.y + S(6)),
                                 (cursor_x, name_rect.y + name_rect.height - S(6)), max(1, S(2)))

        if not is_human and config.get("quip"):
            quip = self.small_font.render(config["quip"], True, th.text_dim)
            self.screen.blit(quip, (name_x, y + h - S(22)))

        if is_human:
            tip = self.small_font.render("Click name to edit  ·  This is you",
                                          True, th.you_cyan)
            self.screen.blit(tip, (name_x, y + h - S(22)))

        toggle_x = x + S(380)
        toggle_y = y + h // 2 - S(16)
        toggle_w = S(124)
        toggle_h = S(32)
        toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_w, toggle_h)
        self._toggle_rects[i] = toggle_rect
        toggle_color = (60, 130, 90) if is_human else (60, 100, 160)
        pygame.draw.rect(self.screen, toggle_color, toggle_rect, border_radius=S(16))
        pygame.draw.rect(self.screen, th.brass_500, toggle_rect, max(1, S(1)), border_radius=S(16))
        knob_x = toggle_rect.right - S(16) if is_human else toggle_rect.x + S(16)
        pygame.draw.circle(self.screen, th.text_white, (knob_x, toggle_rect.centery), S(12))
        label_txt = "Human" if is_human else "AI"
        ts = self.small_font.render(label_txt, True, th.text_white)
        if is_human:
            self.screen.blit(ts, (toggle_rect.x + S(14), toggle_rect.centery - ts.get_height() // 2))
        else:
            self.screen.blit(ts, (toggle_rect.right - S(14) - ts.get_width(),
                                   toggle_rect.centery - ts.get_height() // 2))

        if not is_human:
            diff_x = x + S(540)
            diff_y = y + h // 2 - S(16)
            self._diff_rects[i] = {}
            label = self.small_font.render("DIFFICULTY", True, th.brass_300)
            self.screen.blit(label, (diff_x, diff_y - S(18)))
            for j, diff in enumerate(["easy", "medium", "hard"]):
                bw_btn = S(84)
                bh_btn = S(32)
                br = pygame.Rect(diff_x + j * (bw_btn + S(4)), diff_y, bw_btn, bh_btn)
                self._diff_rects[i][diff] = br
                active = (config["difficulty"] == diff)
                color = th.brass_500 if active else (50, 50, 50)
                border = th.brass_300 if active else (90, 90, 90)
                pygame.draw.rect(self.screen, color, br, border_radius=S(6))
                pygame.draw.rect(self.screen, border, br, max(1, S(1)), border_radius=S(6))
                ts2 = self.small_font.render(self.DIFFICULTY_LABEL[diff],
                                              True, th.text_white if active else th.text_dim)
                self.screen.blit(ts2, ts2.get_rect(center=br.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.start_button.update_hover(event.pos)
            self.back_button.update_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for count, rect in self.player_count_rects.items():
                if rect.collidepoint(event.pos):
                    self.num_players = count
                    return None

            for i in range(self.num_players):
                if i in self._toggle_rects and self._toggle_rects[i].collidepoint(event.pos):
                    self.players_config[i]["is_human"] = not self.players_config[i]["is_human"]
                    if self.players_config[i]["is_human"]:
                        if self.players_config[i]["name"] in [p["name"] for p in self.AI_PERSONAS]:
                            self.players_config[i]["name"] = "You"
                        self.players_config[i]["quip"] = ""
                    else:
                        used_names = {p["name"] for p in self.players_config if not p["is_human"]}
                        for persona in self.AI_PERSONAS:
                            if persona["name"] not in used_names:
                                self.players_config[i]["name"] = persona["name"]
                                self.players_config[i]["difficulty"] = persona["diff"]
                                self.players_config[i]["quip"] = persona["quip"]
                                break
                    if self.active_input == i:
                        self.active_input = None
                    return None

                if i in self._diff_rects:
                    for diff, dr in self._diff_rects[i].items():
                        if dr.collidepoint(event.pos):
                            self.players_config[i]["difficulty"] = diff
                            return None

                if i in self._name_rects and self._name_rects[i].collidepoint(event.pos):
                    self.active_input = i
                    return None

            if self.active_input is not None:
                self.active_input = None

            if self.start_button.is_clicked(event.pos):
                return 'start_game'
            if self.back_button.is_clicked(event.pos):
                return 'back'

        if event.type == pygame.KEYDOWN and self.active_input is not None:
            i = self.active_input
            if i < self.num_players:
                if event.key == pygame.K_BACKSPACE:
                    self.players_config[i]["name"] = self.players_config[i]["name"][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                    self.active_input = None
                elif event.key == pygame.K_ESCAPE:
                    self.active_input = None
                elif (len(self.players_config[i]["name"]) < 20
                      and event.unicode.isprintable() and event.unicode != ''):
                    self.players_config[i]["name"] += event.unicode
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return 'start_game'
            if event.key == pygame.K_ESCAPE:
                return 'back'
        return None


class PeekScreen:
    def __init__(self, screen, hand_size: int, peek_count: int, peek_seconds: float):
        self.screen = screen
        self.hand_size = hand_size
        self.peek_count = peek_count
        self.peeking = set(range(hand_size - peek_count, hand_size)) if peek_count > 0 else set()
        self.title_font = typo.display_bold(TITLE_FONT_SIZE)
        self.subtitle_font = typo.header_italic(SUBTITLE_FONT_SIZE)
        self.label_font = typo.body(UI_FONT_SIZE)
        self.button_font = typo.body_bold(UI_FONT_SIZE)
        self.card_font = typo.header_bold(CARD_FONT_SIZE)
        self.small_font = typo.body(SMALL_FONT_SIZE)
        self.max_time = peek_seconds
        self.elapsed = 0.0
        self.revealed = True
        self.done_button = Button(SCREEN_WIDTH // 2, S(720), S(320), S(56), "I've Memorized — Continue",
                                   SWAP_GREEN, SWAP_GREEN_HOVER)

    def _draw_background(self):
        import theme as theme_mod
        th = theme_mod.active()
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            t = i / max(1, SCREEN_HEIGHT - 1)
            r = int(th.felt_rim[0] * (1 - t * 0.4) + th.felt_deep[0] * t * 0.6)
            g = int(th.felt_rim[1] * (1 - t * 0.4) + th.felt_deep[1] * t * 0.6)
            b = int(th.felt_rim[2] * (1 - t * 0.4) + th.felt_deep[2] * t * 0.6)
            pygame.draw.line(bg, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        self.screen.blit(bg, (0, 0))
        # lamp glow removed

    def draw(self, game_manager):
        import theme as theme_mod
        import card_render
        th = theme_mod.active()
        self._draw_background()

        for offset, alpha in ((S(4), 70), (S(2), 130), (0, 255)):
            t_color = th.brass_300 if alpha == 255 else th.brass_700
            t_surf = typo.render_with_letter_spacing(
                self.title_font, "STUDY YOUR HAND", t_color, spacing_px=S(6),
            )
            t_surf.set_alpha(alpha)
            self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset,
                                                               S(110) + offset)))

        if self.peek_count == 0:
            sub = self.subtitle_font.render(
                "No cards to peek this round — go in blind.", True, th.text_dim)
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, S(180))))
        else:
            sub = self.subtitle_font.render(
                f"Memorize your bottom {self.peek_count} card{'s' if self.peek_count > 1 else ''} — "
                "they vanish when the timer runs out.",
                True, th.text_dim,
            )
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, S(180))))

        remaining = max(0.0, 1.0 - self.elapsed / max(0.001, self.max_time))
        cx, cy = SCREEN_WIDTH // 2, S(290)
        radius = S(38)
        pygame.draw.circle(self.screen, (*th.panel_bg, ), (cx, cy), radius)
        pygame.draw.circle(self.screen, th.brass_700, (cx, cy), radius, max(1, S(1)))
        if remaining > 0:
            arc_color = th.brass_300 if remaining > 0.4 else th.signal_warn
            self._draw_arc(cx, cy, radius - S(6), remaining, arc_color)
        secs_left = max(0.0, self.max_time - self.elapsed)
        if self.max_time >= 900:
            time_label = "INF"
        else:
            time_label = f"{secs_left:0.1f}s"
        secs_surf = typo.body_bold(S(16)).render(time_label, True, th.text_white)
        self.screen.blit(secs_surf, secs_surf.get_rect(center=(cx, cy)))

        if game_manager is None:
            self.done_button.draw(self.screen, self.button_font)
            return
        human = next((p for p in game_manager.players if p.is_human), None)
        if human is None:
            self.done_button.draw(self.screen, self.button_font)
            return

        card_w = int(CARD_WIDTH * 1.6)
        card_h = int(CARD_HEIGHT * 1.6)
        gap = S(28)
        total_width = card_w * self.hand_size + gap * (self.hand_size - 1)
        start_x = (SCREEN_WIDTH - total_width) // 2
        card_y = S(380)

        slot_label_font = typo.body_bold(S(14))
        peek_tag_font = typo.body_bold(S(12))

        for slot_idx in range(self.hand_size):
            x = start_x + slot_idx * (card_w + gap)
            card = human.hand[slot_idx]
            is_peek_slot = slot_idx in self.peeking and self.revealed

            shadow = pygame.Surface((card_w + S(14), card_h + S(18)), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 130),
                             (S(7), S(10), card_w, card_h), border_radius=S(12))
            self.screen.blit(shadow, (x - S(7), card_y))

            if card is None:
                empty = pygame.Rect(x, card_y, card_w, card_h)
                pygame.draw.rect(self.screen, (*th.felt_rim, ), empty, border_radius=S(12))
                pygame.draw.rect(self.screen, th.brass_700, empty, max(1, S(2)), border_radius=S(12))
                dash_font = typo.header(S(28))
                dash = dash_font.render("—", True, th.text_muted)
                self.screen.blit(dash, dash.get_rect(center=empty.center))
            elif is_peek_slot:
                face = card_render.paint_face(card, card_w, card_h)
                glow_size = (card_w + S(24), card_h + S(24))
                glow = pygame.Surface(glow_size, pygame.SRCALPHA)
                t_phase = pygame.time.get_ticks() / 1000.0
                pulse = 0.6 + 0.4 * abs((t_phase * 1.4) % 2 - 1)
                glow_alpha = int(140 * pulse * (0.5 + 0.5 * remaining))
                pygame.draw.rect(glow, (*th.brass_300, glow_alpha),
                                 glow.get_rect(), border_radius=S(18))
                self.screen.blit(glow, (x - S(12), card_y - S(12)),
                                 special_flags=pygame.BLEND_RGBA_ADD)
                self.screen.blit(face, (x, card_y))

                tag_w, tag_h = S(64), S(22)
                tag_rect = pygame.Rect(x + card_w - tag_w - S(6), card_y + S(6),
                                       tag_w, tag_h)
                pygame.draw.rect(self.screen, th.brass_300, tag_rect, border_radius=S(11))
                tag_text = peek_tag_font.render("PEEKED", True, th.brass_900)
                self.screen.blit(tag_text, tag_text.get_rect(center=tag_rect.center))
            else:
                back = card_render.paint_back("classic", card_w, card_h)
                dim = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 100))
                self.screen.blit(back, (x, card_y))
                self.screen.blit(dim, (x, card_y))
                hidden_label = peek_tag_font.render("HIDDEN", True, th.text_muted)
                self.screen.blit(hidden_label, hidden_label.get_rect(
                    center=(x + card_w // 2, card_y + card_h // 2)))

            label = slot_label_font.render(f"SEAT SLOT {slot_idx + 1}",
                                            True, th.brass_300)
            self.screen.blit(label, label.get_rect(center=(x + card_w // 2,
                                                             card_y + card_h + S(22))))

        tip = self.small_font.render(
            "When the timer ends, your peeked cards flip back. Click anywhere to skip ahead.",
            True, th.text_dim,
        )
        self.screen.blit(tip, tip.get_rect(center=(SCREEN_WIDTH // 2,
                                                     card_y + card_h + S(60))))

        self.done_button.draw(self.screen, self.button_font)

    def _draw_arc(self, cx, cy, radius, fraction, color):
        import math
        steps = max(2, int(60 * fraction))
        if steps < 2:
            return
        start_angle = -math.pi / 2
        end_angle = start_angle + 2 * math.pi * fraction
        points = [(cx, cy)]
        for i in range(steps + 1):
            a = start_angle + (end_angle - start_angle) * (i / steps)
            points.append((cx + math.cos(a) * radius, cy + math.sin(a) * radius))
        if len(points) >= 3:
            pygame.draw.polygon(self.screen, color, points)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.done_button.update_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.done_button.is_clicked(event.pos):
                self.revealed = False
                return 'peek_done'
        return None

    def update(self, dt):
        if self.revealed:
            self.elapsed += dt
            if self.elapsed >= self.max_time:
                self.revealed = False
                return 'peek_done'
        return None


class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = typo.display_bold(int(TITLE_FONT_SIZE * 1.4))
        self.banner_font = typo.header_italic(int(SUBTITLE_FONT_SIZE * 1.05))
        self.name_font = typo.header_bold(int(UI_FONT_SIZE * 1.1))
        self.label_font = typo.body(UI_FONT_SIZE)
        self.button_font = typo.body_bold(UI_FONT_SIZE)
        self.score_font = typo.display_bold(int(UI_FONT_SIZE * 1.4))
        self.small_font = typo.body(SMALL_FONT_SIZE)
        self.play_again_button = Button(SCREEN_WIDTH // 2 - S(160), S(800), S(280), S(52), "Play Again",
                                        SWAP_GREEN, SWAP_GREEN_HOVER)
        self.menu_button = Button(SCREEN_WIDTH // 2 + S(160), S(800), S(280), S(52), "Main Menu",
                                  DECLARE_RED, DECLARE_RED_HOVER)
        self.buttons = [self.play_again_button, self.menu_button]
        self._bg_cache = None

    def _build_background(self):
        import theme as theme_mod
        th = theme_mod.active()
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            t = i / max(1, SCREEN_HEIGHT - 1)
            r = int(th.felt_rim[0] * (1 - t * 0.4) + th.felt_deep[0] * t * 0.6)
            g = int(th.felt_rim[1] * (1 - t * 0.4) + th.felt_deep[1] * t * 0.6)
            b = int(th.felt_rim[2] * (1 - t * 0.4) + th.felt_deep[2] * t * 0.6)
            pygame.draw.line(bg, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        rx, ry = S(760), S(420)
        pygame.draw.ellipse(bg, th.brass_700,
                            pygame.Rect(center[0] - rx, center[1] - ry, rx * 2, ry * 2), max(1, S(1)))
        pygame.draw.ellipse(bg, th.brass_900,
                            pygame.Rect(center[0] - rx - S(6), center[1] - ry - S(6),
                                        (rx + S(6)) * 2, (ry + S(6)) * 2), max(1, S(1)))
        return bg

    def _draw_title(self, banner_text, banner_color):
        import theme as theme_mod
        th = theme_mod.active()
        for offset, alpha in ((S(6), 60), (S(3), 110), (0, 255)):
            t_color = th.brass_300 if alpha == 255 else th.brass_700
            t_surf = typo.render_with_letter_spacing(
                self.title_font, "GAME OVER", t_color, spacing_px=S(10),
            )
            t_surf.set_alpha(alpha)
            r = t_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset, S(90) + offset))
            self.screen.blit(t_surf, r)

        flourish_y = S(152)
        cx = SCREEN_WIDTH // 2
        line_w = S(240)
        pygame.draw.line(self.screen, th.brass_500, (cx - line_w, flourish_y),
                         (cx - S(30), flourish_y), max(1, S(1)))
        pygame.draw.line(self.screen, th.brass_500, (cx + S(30), flourish_y),
                         (cx + line_w, flourish_y), max(1, S(1)))
        pygame.draw.polygon(self.screen, th.brass_500,
                            [(cx, flourish_y - S(5)), (cx - S(12), flourish_y),
                             (cx, flourish_y + S(5)), (cx + S(12), flourish_y)])

        banner_surf = self.banner_font.render(banner_text, True, banner_color)
        banner_rect = banner_surf.get_rect(center=(SCREEN_WIDTH // 2, S(188)))
        chip_w = banner_rect.width + S(56)
        chip_h = banner_rect.height + S(18)
        chip = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
        pygame.draw.rect(chip, (15, 15, 15, 200), chip.get_rect(),
                         border_radius=chip_h // 2)
        pygame.draw.rect(chip, (*banner_color, 200), chip.get_rect(), max(1, S(2)),
                         border_radius=chip_h // 2)
        self.screen.blit(chip, (banner_rect.centerx - chip_w // 2,
                                 banner_rect.centery - chip_h // 2))
        self.screen.blit(banner_surf, banner_rect)

    def _draw_player_panel(self, player, x_center, top_y, hand_size,
                            score_val, is_winner, game_manager):
        import card_render
        import theme as theme_mod
        th = theme_mod.active()

        panel_w = max(S(420), hand_size * (CARD_WIDTH + S(16)) + S(80))
        panel_h = CARD_HEIGHT + S(200)
        panel_rect = pygame.Rect(x_center - panel_w // 2, top_y, panel_w, panel_h)

        shadow = pygame.Surface((panel_w + S(12), panel_h + S(12)), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), (S(6), S(8), panel_w, panel_h),
                         border_radius=S(14))
        self.screen.blit(shadow, (panel_rect.x - S(6), panel_rect.y + S(4)))

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            t = i / max(1, panel_h - 1)
            r = int(th.felt_rim[0] + (th.felt_mid[0] - th.felt_rim[0]) * t * 0.5)
            g = int(th.felt_rim[1] + (th.felt_mid[1] - th.felt_rim[1]) * t * 0.5)
            b = int(th.felt_rim[2] + (th.felt_mid[2] - th.felt_rim[2]) * t * 0.5)
            pygame.draw.line(panel_surf, (r, g, b, 230), (0, i), (panel_w, i))
        mask = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=S(14))
        panel_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(panel_surf, panel_rect.topleft)

        border_color = th.brass_300 if is_winner else th.brass_700
        pygame.draw.rect(self.screen, border_color, panel_rect, max(1, S(2)), border_radius=S(14))
        pygame.draw.rect(self.screen, th.brass_900, panel_rect.inflate(-S(8), -S(8)),
                         max(1, S(1)), border_radius=S(12))

        if is_winner:
            crown_y = panel_rect.top - S(14)
            pts = [
                (x_center - S(18), crown_y + S(14)),
                (x_center - S(14), crown_y),
                (x_center - S(7), crown_y + S(8)),
                (x_center, crown_y - S(4)),
                (x_center + S(7), crown_y + S(8)),
                (x_center + S(14), crown_y),
                (x_center + S(18), crown_y + S(14)),
            ]
            pygame.draw.polygon(self.screen, th.brass_300, pts)
            pygame.draw.polygon(self.screen, th.brass_700, pts, max(1, S(2)))

        name_color = th.brass_300 if is_winner else th.text_white
        name_surf = self.name_font.render(player.name, True, name_color)
        self.screen.blit(name_surf, name_surf.get_rect(
            center=(x_center, panel_rect.top + S(32))))

        score_label = self.small_font.render("SCORE", True, th.text_dim)
        self.screen.blit(score_label, score_label.get_rect(
            center=(x_center, panel_rect.top + S(60))))
        score_color = th.brass_300 if is_winner else th.text_white
        score_surf = self.score_font.render(str(score_val), True, score_color)
        self.screen.blit(score_surf, score_surf.get_rect(
            center=(x_center, panel_rect.top + S(90))))

        # B4 — arithmetic readout under the SCORE value, e.g. "3 + 7 + K(13) = 23".
        parts = []
        for c in player.hand:
            if c is None:
                continue
            v = getattr(c, 'value', 0)
            rank = getattr(c, 'rank', '?')
            if rank in ('J', 'Q', 'K'):
                parts.append(f"{rank}({v})")
            else:
                parts.append(str(v))
        if parts:
            arith = " + ".join(parts) + f" = {score_val}"
        else:
            arith = f"= {score_val}"
        arith_surf = self.small_font.render(arith, True, th.text_dim)
        self.screen.blit(arith_surf, arith_surf.get_rect(
            center=(x_center, panel_rect.top + S(118))))

        gap = S(12)
        total_w = hand_size * CARD_WIDTH + (hand_size - 1) * gap
        cards_x = x_center - total_w // 2
        cards_y = panel_rect.top + S(130)
        for slot_idx in range(hand_size):
            card = player.hand[slot_idx]
            cx = cards_x + slot_idx * (CARD_WIDTH + gap)
            shadow_card = pygame.Surface((CARD_WIDTH + S(8), CARD_HEIGHT + S(8)),
                                          pygame.SRCALPHA)
            pygame.draw.rect(shadow_card, (0, 0, 0, 120),
                             (S(4), S(6), CARD_WIDTH, CARD_HEIGHT),
                             border_radius=CORNER_RADIUS)
            self.screen.blit(shadow_card, (cx - S(4), cards_y - S(4)))
            if card is not None:
                face = card_render.paint_face(card, CARD_WIDTH, CARD_HEIGHT)
                self.screen.blit(face, (cx, cards_y))
            else:
                empty_rect = pygame.Rect(cx, cards_y, CARD_WIDTH, CARD_HEIGHT)
                pygame.draw.rect(self.screen, (*th.felt_rim, 200), empty_rect,
                                 border_radius=CORNER_RADIUS)
                pygame.draw.rect(self.screen, th.brass_700, empty_rect, max(1, S(1)),
                                 border_radius=CORNER_RADIUS)
                dash = self.label_font.render("—", True, th.text_dim)
                self.screen.blit(dash, dash.get_rect(center=empty_rect.center))

    def draw(self, game_manager, result=None, particles=None, edge_flash=None):
        import theme as theme_mod
        th = theme_mod.active()

        if self._bg_cache is None:
            self._bg_cache = self._build_background()
        self.screen.blit(self._bg_cache, (0, 0))

        banner_text = "Game complete"
        banner_color = th.brass_300
        if result:
            if result.get("auto_win"):
                banner_text = "Auto-win — a player ran out of cards"
                banner_color = th.signal_warn
            elif result.get("winner"):
                winner = result["winner"]
                banner_text = f"{winner.name} wins the round"
                banner_color = th.brass_300
            elif result.get("declarer_won") is False:
                banner_text = "The declarer lost!"
                banner_color = th.declare_red
            else:
                banner_text = "It's a draw"
                banner_color = th.text_white

        # B3 — fire one-shot fanfare on the first paint of this game-over.
        # Subsequent paints (the player lingering on the screen) skip both the
        # SFX and the burst.
        if not getattr(self, "_fanfare_played", False) and result is not None:
            try:
                import audio as _audio
                winner = result.get("winner") if result else None
                human_won = winner is not None and getattr(winner, "is_human", False)
                _audio.play("win" if human_won else "loss")
            except Exception:
                pass
            if particles is not None:
                particles.burst_achievement(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            if edge_flash is not None and result.get("declarer_won") is False:
                edge_flash.fire(color=th.declare_red, duration=0.8, thickness=40)
            self._fanfare_played = True

        self._draw_title(banner_text, banner_color)

        if game_manager is None:
            for button in self.buttons:
                button.draw(self.screen, self.button_font)
            return

        num_players = len(game_manager.players)
        scores = result.get("scores", {}) if result else {}
        winner_seat = None
        if result and result.get("winner"):
            winner_seat = result["winner"].seat_index

        hand_size = getattr(game_manager, 'hand_size', 4)
        section_width = SCREEN_WIDTH // num_players
        for i, player in enumerate(game_manager.players):
            px = section_width * i + section_width // 2
            score_val = scores.get(player.seat_index,
                                    player.score if hasattr(player, 'score') else 0)
            is_winner = (winner_seat == player.seat_index)
            self._draw_player_panel(player, px, S(240), hand_size, score_val,
                                     is_winner, game_manager)

        for button in self.buttons:
            button.draw(self.screen, self.button_font)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.update_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_again_button.is_clicked(event.pos):
                return 'play_again'
            if self.menu_button.is_clicked(event.pos):
                return 'menu'
        return None