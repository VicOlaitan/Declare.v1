import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_DARK, CARD_WHITE, CARD_BACK_BLUE,
    CARD_BACK_PATTERN, CARD_SHADOW, BLACK, RED, GOLD, TEXT_WHITE, TEXT_BLACK,
    TEXT_DIM, HIGHLIGHT, DIM, PANEL_BG, PANEL_BORDER, POWER_GLOW, EMPTY_SLOT,
    DECLARE_RED, DECLARE_RED_HOVER, SWAP_GREEN, SWAP_GREEN_HOVER, PEEK_BLUE, PEEK_BLUE_HOVER,
    CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS, CARD_SPREAD, HAND_SIZE, HAND_SIZE_OPTIONS,
    DECK_CENTER, DRAWN_CARD_POS, DISCARD_POS,
    PLAYER_BOTTOM, PLAYER_TOP, PLAYER_LEFT, PLAYER_RIGHT,
    TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, UI_FONT_SIZE, LOG_FONT_SIZE,
    SMALL_FONT_SIZE, CARD_FONT_SIZE, CARD_BIG_FONT_SIZE,
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

        shadow_surf = pygame.Surface((self.rect.width + 4, self.rect.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (2, 3, self.rect.width, self.rect.height), border_radius=CORNER_RADIUS)
        screen.blit(shadow_surf, (self.rect.x - 2, self.rect.y + 3))

        pygame.draw.rect(screen, color, self.rect, border_radius=CORNER_RADIUS)

        c_r = max(color[0] - 35, 0)
        c_g = max(color[1] - 35, 0)
        c_b = max(color[2] - 35, 0)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (self.rect.left + 3, self.rect.bottom - 3),
                         (self.rect.right - 3, self.rect.bottom - 3), 2)
        pygame.draw.line(screen, (c_r, c_g, c_b),
                         (self.rect.right - 3, self.rect.top + 3),
                         (self.rect.right - 3, self.rect.bottom - 3), 2)
        l_r = min(color[0] + 40, 255)
        l_g = min(color[1] + 40, 255)
        l_b = min(color[2] + 40, 255)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (self.rect.left + 3, self.rect.top + 3),
                         (self.rect.right - 3, self.rect.top + 3), 2)
        pygame.draw.line(screen, (l_r, l_g, l_b),
                         (self.rect.left + 3, self.rect.top + 3),
                         (self.rect.left + 3, self.rect.bottom - 3), 2)

        pygame.draw.rect(screen, BLACK, self.rect, width=2, border_radius=CORNER_RADIUS)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mouse_pos):
            return True
        return False

    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("segoeui", TITLE_FONT_SIZE, bold=True)
        self.subtitle_font = pygame.font.SysFont("segoeui", SUBTITLE_FONT_SIZE)
        self.button_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.new_game_button = Button(SCREEN_WIDTH // 2, 430, 260, 54, "New Game", SWAP_GREEN, SWAP_GREEN_HOVER)
        self.quit_button = Button(SCREEN_WIDTH // 2, 500, 260, 54, "Quit", DECLARE_RED, DECLARE_RED_HOVER)
        self.buttons = [self.new_game_button, self.quit_button]

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

    def draw(self):
        self.screen.fill(BG_DARK)

        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(0, 300, 6):
            alpha = int(40 * (1 - i / 300))
            pygame.draw.rect(vignette, (10, 10, 15, alpha),
                             (i, i, SCREEN_WIDTH - 2 * i, SCREEN_HEIGHT - 2 * i), border_radius=20)
        self.screen.blit(vignette, (0, 0))

        card_fan = [(-110, 295, -12), (-55, 290, -4), (0, 288, 0), (55, 290, 4), (110, 295, 12)]
        for dx, cy, angle in card_fan:
            cx = SCREEN_WIDTH // 2 + dx
            self._draw_menu_card_back(cx, cy, angle)

        title_surf = self.title_font.render("DECLARE", True, GOLD)
        shadow_surf = self.title_font.render("DECLARE", True, (50, 30, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2, 162))
        self.screen.blit(shadow_surf, title_rect)
        title_rect2 = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(title_surf, title_rect2)

        subtitle_surf = self.subtitle_font.render("A Card Game of Memory & Strategy", True, TEXT_DIM)
        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 205)))

        for button in self.buttons:
            button.draw(self.screen, self.button_font)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.update_hover(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.new_game_button.is_clicked(event.pos):
                return 'new_game'
            if self.quit_button.is_clicked(event.pos):
                return 'quit'
        return None


class SetupScreen:
    def __init__(self, screen, game_settings=None, num_players=2):
        self.screen = screen
        self.game_settings = game_settings
        self.title_font = pygame.font.SysFont("segoeui", TITLE_FONT_SIZE, bold=True)
        self.label_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.button_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.input_font = pygame.font.SysFont("segoeui", SMALL_FONT_SIZE)
        self.num_players = num_players
        self.players_config = []
        for i in range(4):
            self.players_config.append({"name": f"Player {i + 1}", "is_human": i == 0})
        self.active_input = None
        self.player_count_buttons = []
        for idx, count in enumerate([2, 3, 4]):
            bx = SCREEN_WIDTH // 2 - 100 + idx * 100
            self.player_count_buttons.append(
                Button(bx, 180, 80, 44, str(count), SWAP_GREEN, SWAP_GREEN_HOVER)
            )
        self._build_game_settings_buttons()
        self.start_button = Button(SCREEN_WIDTH // 2, 700, 280, 54, "Start Game", SWAP_GREEN, SWAP_GREEN_HOVER)
        self.back_button = Button(100, 770, 160, 44, "Back", DECLARE_RED, DECLARE_RED_HOVER)

    def _build_game_settings_buttons(self):
        self.hand_size_buttons = []
        for idx, size in enumerate(HAND_SIZE_OPTIONS):
            bx = SCREEN_WIDTH // 2 - 180 + idx * 75
            self.hand_size_buttons.append(
                Button(bx, 0, 60, 36, str(size), SWAP_GREEN, SWAP_GREEN_HOVER)
            )
        self._rebuild_peek_count_buttons()

    def _rebuild_peek_count_buttons(self):
        self.peek_count_buttons = []
        if self.game_settings is None:
            return
        hand_size = self.game_settings.hand_size
        count = hand_size + 1
        start_x = SCREEN_WIDTH // 2 - (count * 55) // 2 + 25
        for i in range(count):
            bx = start_x + i * 55
            label = str(i)
            self.peek_count_buttons.append(
                Button(bx, 0, 48, 36, label, PEEK_BLUE, PEEK_BLUE_HOVER)
            )

    def _get_toggle_button(self, index, y):
        config = self.players_config[index]
        text = "Human" if config["is_human"] else "AI"
        color = SWAP_GREEN if config["is_human"] else PEEK_BLUE
        hover = SWAP_GREEN_HOVER if config["is_human"] else (100, 170, 250)
        btn = Button(820, y, 120, 36, text, color, hover)
        return btn

    def _settings_y(self):
        return 250 + self.num_players * 90 + 10

    def draw(self):
        self.screen.fill(BG_DARK)
        title_surf = self.title_font.render("SETUP", True, GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        label_surf = self.label_font.render("Number of Players:", True, TEXT_WHITE)
        self.screen.blit(label_surf, label_surf.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        for idx, btn in enumerate(self.player_count_buttons):
            count_val = [2, 3, 4][idx]
            if self.num_players == count_val:
                btn.color = GOLD
                btn.hover_color = (255, 230, 100)
                btn.text_color = TEXT_BLACK
            else:
                btn.color = SWAP_GREEN
                btn.hover_color = SWAP_GREEN_HOVER
                btn.text_color = TEXT_WHITE
            btn.draw(self.screen, self.button_font)
        for i in range(self.num_players):
            y = 250 + i * 90
            config = self.players_config[i]
            num_label = self.label_font.render(f"Player {i + 1}:", True, TEXT_WHITE)
            self.screen.blit(num_label, (150, y - 12))
            name_rect = pygame.Rect(340, y - 18, 380, 36)
            border_color = HIGHLIGHT if self.active_input == i else DIM
            pygame.draw.rect(self.screen, CARD_WHITE, name_rect, border_radius=CORNER_RADIUS)
            pygame.draw.rect(self.screen, border_color, name_rect, width=2, border_radius=CORNER_RADIUS)
            name_surf = self.input_font.render(config["name"], True, TEXT_BLACK)
            self.screen.blit(name_surf, (name_rect.x + 8, name_rect.y + 8))
            toggle = self._get_toggle_button(i, y)
            toggle.draw(self.screen, self.input_font)

        if self.game_settings is not None:
            settings_y = self._settings_y()
            section_surf = self.label_font.render("Game Settings", True, GOLD)
            self.screen.blit(section_surf, section_surf.get_rect(center=(SCREEN_WIDTH // 2, settings_y)))
            pygame.draw.line(self.screen, DIM, (SCREEN_WIDTH // 2 - 200, settings_y + 18),
                             (SCREEN_WIDTH // 2 + 200, settings_y + 18), 1)

            hand_y = settings_y + 36
            hand_label = self.input_font.render("Cards per Hand:", True, TEXT_DIM)
            self.screen.blit(hand_label, (SCREEN_WIDTH // 2 - 240, hand_y - 8))
            for idx, btn in enumerate(self.hand_size_buttons):
                btn.rect.centery = hand_y
                if self.game_settings.hand_size == HAND_SIZE_OPTIONS[idx]:
                    btn.color = GOLD
                    btn.hover_color = (255, 230, 100)
                    btn.text_color = TEXT_BLACK
                else:
                    btn.color = SWAP_GREEN
                    btn.hover_color = SWAP_GREEN_HOVER
                    btn.text_color = TEXT_WHITE
                btn.draw(self.screen, self.input_font)

            peek_y = hand_y + 50
            peek_label = self.input_font.render("Cards Visible:", True, TEXT_DIM)
            self.screen.blit(peek_label, (SCREEN_WIDTH // 2 - 240, peek_y - 8))
            for idx, btn in enumerate(self.peek_count_buttons):
                btn.rect.centery = peek_y
                if self.game_settings.peek_count == idx:
                    btn.color = GOLD
                    btn.hover_color = (255, 230, 100)
                    btn.text_color = TEXT_BLACK
                else:
                    btn.color = PEEK_BLUE
                    btn.hover_color = PEEK_BLUE_HOVER
                    btn.text_color = TEXT_WHITE
                btn.draw(self.screen, self.input_font)

        self.start_button.draw(self.screen, self.button_font)
        self.back_button.draw(self.screen, self.input_font)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for btn in self.player_count_buttons:
                btn.update_hover(event.pos)
            for btn in self.hand_size_buttons:
                btn.update_hover(event.pos)
            for btn in self.peek_count_buttons:
                btn.update_hover(event.pos)
            self.start_button.update_hover(event.pos)
            self.back_button.update_hover(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, btn in enumerate(self.player_count_buttons):
                if btn.is_clicked(event.pos):
                    self.num_players = [2, 3, 4][idx]
                    return None

            for i in range(self.num_players):
                y = 250 + i * 90
                toggle = self._get_toggle_button(i, y)
                if toggle.is_clicked(event.pos):
                    self.players_config[i]["is_human"] = not self.players_config[i]["is_human"]
                    return None
                name_rect = pygame.Rect(340, y - 18, 380, 36)
                if name_rect.collidepoint(event.pos):
                    self.active_input = i
                elif self.active_input == i:
                    self.active_input = None

            if self.game_settings is not None:
                for idx, btn in enumerate(self.hand_size_buttons):
                    if btn.is_clicked(event.pos):
                        self.game_settings.hand_size = HAND_SIZE_OPTIONS[idx]
                        if self.game_settings.peek_count > self.game_settings.hand_size:
                            self.game_settings.peek_count = self.game_settings.hand_size
                        self._rebuild_peek_count_buttons()
                        return None
                for idx, btn in enumerate(self.peek_count_buttons):
                    if btn.is_clicked(event.pos):
                        self.game_settings.peek_count = idx
                        return None

            if self.start_button.is_clicked(event.pos):
                return 'start_game'
            if self.back_button.is_clicked(event.pos):
                return 'back'

        if event.type == pygame.KEYDOWN and self.active_input is not None:
            i = self.active_input
            if i < self.num_players:
                if event.key == pygame.K_BACKSPACE:
                    self.players_config[i]["name"] = self.players_config[i]["name"][:-1]
                elif event.key == pygame.K_RETURN:
                    self.active_input = None
                elif len(self.players_config[i]["name"]) < 20 and event.unicode.isprintable() and event.unicode != '':
                    self.players_config[i]["name"] += event.unicode
        return None


class PeekScreen:
    def __init__(self, screen, hand_size=4, peek_count=2, peek_seconds=5.0):
        self.screen = screen
        self.hand_size = hand_size
        self.peek_count = peek_count
        self.title_font = pygame.font.SysFont("segoeui", TITLE_FONT_SIZE, bold=True)
        self.subtitle_font = pygame.font.SysFont("segoeui", SUBTITLE_FONT_SIZE)
        self.label_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.button_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.card_font = pygame.font.SysFont("segoeui", CARD_FONT_SIZE, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", SMALL_FONT_SIZE)
        self.max_time = peek_seconds
        self.elapsed = 0.0
        self.revealed = True
        self.done_button = Button(SCREEN_WIDTH // 2, 500, 300, 54, "I've memorized them!", SWAP_GREEN, SWAP_GREEN_HOVER)

    def _draw_card_face(self, x, y, card, glow=False):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        if glow:
            glow_rect = pygame.Rect(x - 4, y - 4, CARD_WIDTH + 8, CARD_HEIGHT + 8)
            pygame.draw.rect(self.screen, HIGHLIGHT, glow_rect, border_radius=CORNER_RADIUS + 2)
        pygame.draw.rect(self.screen, CARD_WHITE, rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(self.screen, BLACK, rect, width=2, border_radius=CORNER_RADIUS)
        color = RED if card.is_red else BLACK
        rank_surf = self.card_font.render(card.rank, True, color)
        self.screen.blit(rank_surf, (x + 6, y + 4))
        sym_surf = self.card_font.render(card.suit_symbol, True, color)
        self.screen.blit(sym_surf, (x + 6, y + 22))
        center_surf = self.card_font.render(card.display_name, True, color)
        center_rect = center_surf.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
        self.screen.blit(center_surf, center_rect)

    def _draw_card_back(self, x, y, dimmed=False):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        base_color = tuple(c // 2 for c in CARD_BACK_BLUE) if dimmed else CARD_BACK_BLUE
        pygame.draw.rect(self.screen, base_color, rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(self.screen, BLACK, rect, width=2, border_radius=CORNER_RADIUS)
        inner = pygame.Rect(x + 8, y + 8, CARD_WIDTH - 16, CARD_HEIGHT - 16)
        inner_color = tuple(c // 2 for c in CARD_BACK_PATTERN) if dimmed else CARD_BACK_PATTERN
        pygame.draw.rect(self.screen, inner_color, inner, border_radius=4)

    def draw(self, game_manager):
        self.screen.fill(BG_DARK)
        title_surf = self.title_font.render("PEEK PHASE", True, GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        if self.peek_count == 0:
            subtitle_text = "Blind start — no cards visible!"
        elif self.peek_count >= self.hand_size:
            subtitle_text = "All cards are face up!"
        else:
            subtitle_text = f"Memorize your bottom {self.peek_count} cards!"
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, TEXT_WHITE)
        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 130)))
        bar_w = 400
        bar_h = 20
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = 170
        remaining = max(0, 1.0 - self.elapsed / self.max_time)
        pygame.draw.rect(self.screen, DIM, (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * remaining)
        if fill_w > 0:
            r = int(220 * (1 - remaining) + 40 * remaining)
            g = int(40 * (1 - remaining) + 180 * remaining)
            b = int(40 * (1 - remaining) + 60 * remaining)
            pygame.draw.rect(self.screen, (r, g, b), (bar_x, bar_y, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(self.screen, TEXT_DIM, (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=6)
        if game_manager is None:
            self.done_button.draw(self.screen, self.button_font)
            return
        human = None
        for p in game_manager.players:
            if p.is_human:
                human = p
                break
        if human is None:
            self.done_button.draw(self.screen, self.button_font)
            return
        hand_size = len(human.hand)
        peek_slots = set(range(max(0, hand_size - self.peek_count), hand_size))
        total_spread = hand_size * CARD_WIDTH + (hand_size - 1) * CARD_SPREAD
        start_x = SCREEN_WIDTH // 2 - total_spread // 2
        card_y = 260
        for slot_idx in range(hand_size):
            cx = start_x + slot_idx * (CARD_WIDTH + CARD_SPREAD)
            card = human.hand[slot_idx]
            is_peek_slot = slot_idx in peek_slots and self.revealed
            if card is not None and is_peek_slot:
                self._draw_card_face(cx, card_y, card, glow=True)
            elif card is not None:
                self._draw_card_back(cx, card_y, dimmed=True)
            else:
                rect = pygame.Rect(cx, card_y, CARD_WIDTH, CARD_HEIGHT)
                pygame.draw.rect(self.screen, EMPTY_SLOT, rect, border_radius=CORNER_RADIUS)
            label = self.small_font.render(f"Slot {slot_idx + 1}", True, TEXT_DIM)
            self.screen.blit(label, label.get_rect(center=(cx + CARD_WIDTH // 2, card_y + CARD_HEIGHT + 20)))
        self.done_button.draw(self.screen, self.button_font)

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
        self.title_font = pygame.font.SysFont("segoeui", TITLE_FONT_SIZE, bold=True)
        self.label_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.button_font = pygame.font.SysFont("segoeui", UI_FONT_SIZE)
        self.card_font = pygame.font.SysFont("segoeui", CARD_FONT_SIZE, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", SMALL_FONT_SIZE)
        self.play_again_button = Button(320, 680, 240, 50, "Play Again", SWAP_GREEN, SWAP_GREEN_HOVER)
        self.menu_button = Button(960, 680, 240, 50, "Main Menu", DECLARE_RED, DECLARE_RED_HOVER)
        self.buttons = [self.play_again_button, self.menu_button]

    def _draw_card_face(self, x, y, card):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(self.screen, CARD_WHITE, rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(self.screen, BLACK, rect, width=2, border_radius=CORNER_RADIUS)
        color = RED if card.is_red else BLACK
        rank_surf = self.card_font.render(card.rank, True, color)
        self.screen.blit(rank_surf, (x + 6, y + 4))
        sym_surf = self.card_font.render(card.suit_symbol, True, color)
        self.screen.blit(sym_surf, (x + 6, y + 22))
        center_surf = self.card_font.render(card.display_name, True, color)
        center_rect = center_surf.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
        self.screen.blit(center_surf, center_rect)

    def _draw_empty_slot(self, x, y):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(self.screen, EMPTY_SLOT, rect, border_radius=CORNER_RADIUS)
        pygame.draw.rect(self.screen, BLACK, rect, width=1, border_radius=CORNER_RADIUS)

    def draw(self, game_manager, result=None):
        self.screen.fill(BG_DARK)
        title_surf = self.title_font.render("GAME OVER", True, GOLD)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60)))
        if result:
            if result.get("auto_win"):
                announce_surf = self.label_font.render("Auto-win! A player has no cards!", True, TEXT_WHITE)
                self.screen.blit(announce_surf, announce_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))
            elif result.get("winner"):
                winner = result["winner"]
                color = GOLD
                announce_text = f"{winner.name} wins!"
                announce_surf = self.label_font.render(announce_text, True, color)
                self.screen.blit(announce_surf, announce_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))
            elif result.get("declarer_won") is False:
                announce_surf = self.label_font.render("The declarer lost!", True, RED)
                self.screen.blit(announce_surf, announce_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))
            else:
                announce_surf = self.label_font.render("It's a draw!", True, TEXT_WHITE)
                self.screen.blit(announce_surf, announce_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))
        if game_manager is None:
            for button in self.buttons:
                button.draw(self.screen, self.button_font)
            return
        num_players = len(game_manager.players)
        scores = result.get("scores", {}) if result else {}
        section_width = SCREEN_WIDTH // num_players
        for i, player in enumerate(game_manager.players):
            px = section_width * i + section_width // 2
            name_surf = self.label_font.render(player.name, True, TEXT_WHITE)
            self.screen.blit(name_surf, name_surf.get_rect(center=(px, 160)))
            score_val = scores.get(player.seat_index, player.score if hasattr(player, 'score') else 0)
            score_surf = self.small_font.render(f"Score: {score_val}", True, GOLD)
            self.screen.blit(score_surf, score_surf.get_rect(center=(px, 190)))
            hand_size = len(player.hand)
            card_start_x = px - (hand_size * CARD_WIDTH + (hand_size - 1) * CARD_SPREAD) // 2
            for slot_idx in range(hand_size):
                card = player.hand[slot_idx]
                cx = card_start_x + slot_idx * (CARD_WIDTH + CARD_SPREAD)
                cy = 220
                if card is not None:
                    self._draw_card_face(cx, cy, card)
                else:
                    self._draw_empty_slot(cx, cy)
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