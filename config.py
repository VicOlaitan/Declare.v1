# 4K rendering: SCALE multiplies every spatial constant. The original
# layout was authored at 1600x900; bumping SCALE renders everything at
# (1600*S, 900*S) with proportional fonts/cards/positions.
SCALE = 2.4


def S(n):
    """Scale a single linear pixel value."""
    return int(round(n * SCALE))


def Sp(t):
    """Scale a tuple of pixel values (positions, rects, etc)."""
    return tuple(int(round(v * SCALE)) for v in t)


import os

SCREEN_WIDTH = S(1600)
SCREEN_HEIGHT = S(900)
FPS = 60
AI_DELAY = 0.8
PEEK_REVEAL_SECONDS = 2.5

BG_GREEN = (39, 119, 62)
BG_DARK = (20, 20, 20)
CARD_WHITE = (255, 255, 255)
CARD_BACK_BLUE = (30, 60, 120)
CARD_BACK_PATTERN = (40, 80, 150)
CARD_SHADOW = (15, 15, 15)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
GOLD = (255, 215, 0)
TEXT_WHITE = (255, 255, 255)
TEXT_BLACK = (0, 0, 0)
TEXT_DIM = (180, 180, 180)
HIGHLIGHT = (255, 255, 100)
DIM = (100, 100, 100)
PANEL_BG = (15, 15, 15)
PANEL_BORDER = (60, 60, 60)
POWER_GLOW = (80, 180, 255)
EMPTY_SLOT = (60, 90, 60)
KNOWN_TINT = (255, 215, 0, 40)
DECLARE_RED = (220, 40, 40)
DECLARE_RED_HOVER = (255, 70, 70)
CANCEL_GRAY = (100, 100, 100)
CANCEL_GRAY_HOVER = (140, 140, 140)
PEEK_BLUE = (70, 140, 220)
PEEK_BLUE_HOVER = (100, 170, 250)
SWAP_GREEN = (40, 130, 60)
SWAP_GREEN_HOVER = (60, 170, 80)
DISCARD_ORANGE = (200, 120, 30)
DISCARD_ORANGE_HOVER = (230, 150, 50)
PAIR_TEAL = (40, 140, 160)
PAIR_TEAL_HOVER = (60, 170, 190)

STATUS_BAR_H = S(44)
ACTION_BAR_Y = S(830)
ACTION_BAR_H = S(70)

CARD_WIDTH = S(100)
CARD_HEIGHT = S(140)
CORNER_RADIUS = S(10)

CARD_SPREAD = S(116)

DECK_CENTER = Sp((640, 400))
DRAWN_CARD_POS = Sp((860, 400))
DISCARD_POS = Sp((750, 400))

PLAYER_BOTTOM = Sp((800, 700))
PLAYER_TOP = Sp((800, 200))
PLAYER_LEFT = Sp((260, 450))
PLAYER_RIGHT = Sp((1340, 450))

PLAYER_AREA_2 = {
    0: Sp((20, 480, 1580, 820)),
    1: Sp((40, 80, 1560, 380)),
}
PLAYER_AREA_3 = {
    0: Sp((20, 480, 1580, 820)),
    1: Sp((40, 80, 780, 380)),
    2: Sp((820, 80, 1560, 380)),
}
PLAYER_AREA_4 = {
    0: Sp((20, 480, 1580, 820)),
    1: Sp((40, 80, 1560, 380)),
    2: Sp((20, 140, 480, 820)),
    3: Sp((1120, 140, 1580, 820)),
}

LOG_PANEL_X = S(1300)
LOG_PANEL_Y = S(520)
LOG_PANEL_W = S(280)
LOG_PANEL_H = S(280)

CARD_VALUES = {
    'A': 1,
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13,
}

BLACK_KING_VALUE = 0

RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['spade', 'heart', 'diamond', 'club']

HAND_SIZE = 4
MAX_PAIR_STACK = 2

POWER_CARDS = {
    '7': 'peek_self',
    '8': 'peek_self',
    '9': 'peek_opponent',
    '10': 'peek_opponent',
    'J': 'skip',
    'Q': 'unseen_swap',
    ('K', 'heart'): 'seen_swap',
    ('K', 'diamond'): 'seen_swap',
    ('K', 'spade'): None,
    ('K', 'club'): None,
}

POWER_LABELS = {
    'peek_self': 'Peek Self',
    'peek_opponent': 'Peek Opponent',
    'skip': 'Skip Next',
    'unseen_swap': 'Unseen Swap',
    'seen_swap': 'Seen Swap',
}

POWER_COLORS = {
    'peek_self': PEEK_BLUE,
    'peek_opponent': PEEK_BLUE,
    'skip': DECLARE_RED,
    'unseen_swap': SWAP_GREEN,
    'seen_swap': SWAP_GREEN,
}

CARD_GRID_SPACING_X = S(100)
CARD_GRID_SPACING_Y = S(130)
PLAYER_AREA_PADDING = S(20)

DEFAULT_AI_DELAY = 1.6
DEFAULT_PEEK_REVEAL_TIME = 2.5
DEFAULT_PEEK_PHASE_SECONDS = 5.0
DEFAULT_ANIMATIONS_ENABLED = True
DEFAULT_SHOW_OWN_SCORE = False
DEFAULT_SHOW_KNOWN_MARKER = True
DEFAULT_SHOW_GAME_LOG = True
DEFAULT_CONFIRM_DECLARE = True
DEFAULT_AI_DIFFICULTY = 'medium'
DEFAULT_LAYOUT_MODE = 'line'
DEFAULT_SELF_PAIR_ENABLED = True
DEFAULT_SHUFFLE_ENABLED = True
DEFAULT_WRONG_DROP_PENALTY = True
DEFAULT_REACTION_WINDOW_SECONDS = 3.0

AI_DELAY_OPTIONS = [0.8, 1.6, 3.0]
AI_DELAY_LABELS = ['Fast', 'Normal', 'Slow']
PEEK_REVEAL_OPTIONS = [1.5, 2.5, 4.0]
PEEK_REVEAL_LABELS = ['Short', 'Normal', 'Long']
ANIMATION_OPTIONS = [True, False]
ANIMATION_LABELS = ['ON', 'OFF']
LAYOUT_OPTIONS = ['line', 'square', 'free']
LAYOUT_LABELS = ['Line', 'Square', 'Free']
AI_DIFFICULTY_OPTIONS = ['easy', 'medium', 'hard']
AI_DIFFICULTY_LABELS = ['Easy', 'Medium', 'Hard']
PEEK_PHASE_OPTIONS = [3.0, 5.0, 10.0, 999.0]
PEEK_PHASE_LABELS = ['3s', '5s', '10s', '∞']
SWAP_REVEAL_SECONDS = 2.0
DEFAULT_HAND_SIZE = 4
DEFAULT_PEEK_COUNT = 2
DEFAULT_REACTION_WINDOW = 3.0
HAND_SIZE_OPTIONS = [2, 3, 4, 5, 6]
HAND_SIZE_LABELS = ['2', '3', '4', '5', '6']
REACTION_WINDOW_OPTIONS = [2.0, 3.0, 5.0]
REACTION_WINDOW_LABELS = ['2s', '3s', '5s']
PEEK_COUNT_OPTIONS = [0, 1, 2, 3, 4, 5]
PEEK_COUNT_LABELS = ['0', '1', '2', '3', '4', '5']

ANIM_DRAW_DURATION = 0.55
ANIM_SWAP_DURATION = 0.7
ANIM_UNSEEN_SWAP_DURATION = 0.8
ANIM_SEEN_SWAP_DURATION = 1.0
ANIM_PEEK_LIFT_DURATION = 0.45
ANIM_PAIR_FLY_DURATION = 0.65
ANIM_DISCARD_DURATION = 0.55
ANIM_NOTIFICATION_DURATION = 2.0
ANIM_FLASH_DURATION = 0.3
ANIM_SHUFFLE_DURATION = 0.4
ANIM_REACTIVE_DROP_DURATION = 0.3
ANIM_PENALTY_DRAW_DURATION = 0.3

SHUFFLE_COLOR = (120, 100, 180)
SHUFFLE_HOVER = (150, 130, 210)
SELF_PAIR_COLOR = (40, 160, 140)
SELF_PAIR_HOVER = (60, 190, 170)
DROP_MATCH_COLOR = (220, 140, 40)
DROP_MATCH_HOVER = (240, 165, 60)

CARD_FONT_SIZE = S(18)
CARD_BIG_FONT_SIZE = S(28)
TITLE_FONT_SIZE = S(56)
SUBTITLE_FONT_SIZE = S(22)
UI_FONT_SIZE = S(20)
LOG_FONT_SIZE = S(15)
SMALL_FONT_SIZE = S(14)
