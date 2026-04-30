import os

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60
AI_DELAY = 0.8
PEEK_REVEAL_SECONDS = 2.5

BG_DARK = (13, 17, 23)
BG_GRADIENT_TOP = (18, 22, 30)
BG_GRADIENT_BOTTOM = (10, 12, 16)

CARD_WHITE = (248, 248, 245)
CARD_BACK_BLUE = (22, 42, 72)
CARD_BACK_PATTERN = (30, 55, 90)
CARD_BACK_MEDALLION = (45, 75, 130)
CARD_BACK_MEDALLION_HI = (180, 200, 240)
CARD_BACK_MEDALLION_LO = (28, 48, 80)
CARD_SHADOW = (10, 12, 16)
BLACK = (26, 26, 26)
RED = (196, 30, 58)
GOLD = (201, 168, 76)
GOLD_HOVER = (224, 192, 104)
GOLD_DIM = (140, 115, 50)
TEXT_WHITE = (232, 232, 232)
TEXT_BLACK = (26, 26, 26)
TEXT_DIM = (140, 140, 140)
TEXT_DIMMER = (100, 100, 100)
HIGHLIGHT = (224, 192, 104)
DIM = (80, 80, 80)
PANEL_BG = (18, 18, 22)
PANEL_BORDER = (50, 50, 55)
PANEL_BORDER_GOLD = (201, 168, 76)
POWER_GLOW = (80, 180, 255)
EMPTY_SLOT = (40, 60, 50)
KNOWN_TINT = (201, 168, 76, 50)
DECLARE_RED = (180, 35, 50)
DECLARE_RED_HOVER = (210, 50, 65)
CANCEL_GRAY = (70, 70, 75)
CANCEL_GRAY_HOVER = (100, 100, 105)
PEEK_BLUE = (60, 130, 200)
PEEK_BLUE_HOVER = (80, 155, 230)
SWAP_GREEN = (35, 120, 80)
SWAP_GREEN_HOVER = (50, 150, 100)
DISCARD_ORANGE = (190, 110, 30)
DISCARD_ORANGE_HOVER = (220, 140, 45)
PAIR_TEAL = (35, 130, 150)
PAIR_TEAL_HOVER = (50, 160, 180)

STATUS_BAR_H = 44
ACTION_BAR_Y = 830
ACTION_BAR_H = 70

CARD_WIDTH = 80
CARD_HEIGHT = 112
CORNER_RADIUS = 8

CARD_SPREAD = 95

DECK_CENTER = (640, 400)
DRAWN_CARD_POS = (860, 400)
DISCARD_POS = (750, 400)

PLAYER_BOTTOM = (800, 700)
PLAYER_TOP = (800, 200)
PLAYER_LEFT = (260, 450)
PLAYER_RIGHT = (1340, 450)

PLAYER_AREA_2 = {
    0: (20, 480, 1580, 820),
    1: (40, 80, 1560, 380),
}
PLAYER_AREA_3 = {
    0: (20, 480, 1580, 820),
    1: (40, 80, 780, 380),
    2: (820, 80, 1560, 380),
}
PLAYER_AREA_4 = {
    0: (20, 480, 1580, 820),
    1: (40, 80, 1560, 380),
    2: (20, 140, 480, 820),
    3: (1120, 140, 1580, 820),
}

LOG_PANEL_X = 1300
LOG_PANEL_Y = 520
LOG_PANEL_W = 280
LOG_PANEL_H = 280

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

DEFAULT_HAND_SIZE = 4
DEFAULT_PEEK_COUNT = 2
HAND_SIZE_OPTIONS = [2, 3, 4, 5, 6]

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

CARD_GRID_SPACING_X = 100
CARD_GRID_SPACING_Y = 130
PLAYER_AREA_PADDING = 20

DEFAULT_AI_DELAY = 0.8
DEFAULT_PEEK_REVEAL_TIME = 2.5
DEFAULT_PEEK_PHASE_SECONDS = 5.0
DEFAULT_ANIMATIONS_ENABLED = True
DEFAULT_SHOW_OWN_SCORE = False
DEFAULT_SHOW_KNOWN_MARKER = True
DEFAULT_SHOW_GAME_LOG = True
DEFAULT_CONFIRM_DECLARE = True
DEFAULT_AI_DIFFICULTY = 'medium'
DEFAULT_LAYOUT_MODE = 'line'
DEFAULT_FELT = 'forest'
DEFAULT_SELF_PAIR_ENABLED = True
DEFAULT_SHUFFLE_ENABLED = True
DEFAULT_WRONG_DROP_PENALTY = True
DEFAULT_REACTION_WINDOW_SECONDS = 3.0

REACTION_WINDOW_OPTIONS = [2.0, 3.0, 5.0]
REACTION_WINDOW_LABELS = ['2s', '3s', '5s']

SHUFFLE_COLOR = (120, 100, 180)
SHUFFLE_HOVER = (150, 130, 210)
SELF_PAIR_COLOR = (40, 160, 140)
SELF_PAIR_HOVER = (60, 190, 170)
DROP_MATCH_COLOR = (220, 140, 40)
DROP_MATCH_HOVER = (240, 165, 60)

AI_DELAY_OPTIONS = [0.3, 0.8, 1.5]
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
PEEK_PHASE_LABELS = ['3s', '5s', '10s', '\u221e']

ANIM_SHUFFLE_DURATION = 0.4
ANIM_REACTIVE_DROP_DURATION = 0.3
ANIM_PENALTY_DRAW_DURATION = 0.3

FELT_COLORS = {
    'forest':   (27, 67, 50),
    'burgundy': (92, 26, 27),
    'navy':     (26, 39, 68),
    'charcoal': (45, 45, 45),
    'emerald':  (18, 80, 60),
}
FELT_LABELS = ['Forest', 'Burgundy', 'Navy', 'Charcoal', 'Emerald']

FELT_COLORS_LIGHT = {
    'forest':   (35, 85, 62),
    'burgundy': (120, 35, 36),
    'navy':     (35, 52, 88),
    'charcoal': (60, 60, 60),
    'emerald':  (25, 100, 75),
}

ANIM_DRAW_DURATION = 0.3
ANIM_SWAP_DURATION = 0.4
ANIM_UNSEEN_SWAP_DURATION = 0.5
ANIM_SEEN_SWAP_DURATION = 0.6
ANIM_PEEK_LIFT_DURATION = 0.25
ANIM_PAIR_FLY_DURATION = 0.4
ANIM_DISCARD_DURATION = 0.3
ANIM_NOTIFICATION_DURATION = 2.0
ANIM_FLASH_DURATION = 0.3

CARD_FONT_SIZE = 18
CARD_BIG_FONT_SIZE = 28
TITLE_FONT_SIZE = 56
SUBTITLE_FONT_SIZE = 22
UI_FONT_SIZE = 20
LOG_FONT_SIZE = 15
SMALL_FONT_SIZE = 14

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts')
FONT_PATHS = {
    'title': os.path.join(FONTS_DIR, 'Cinzel-Bold.ttf'),
    'subtitle': os.path.join(FONTS_DIR, 'Cinzel-Regular.ttf'),
    'ui': os.path.join(FONTS_DIR, 'Inter-Regular.ttf'),
    'ui_bold': os.path.join(FONTS_DIR, 'Inter-SemiBold.ttf'),
    'card': os.path.join(FONTS_DIR, 'Roboto-Regular.ttf'),
    'card_bold': os.path.join(FONTS_DIR, 'Roboto-Bold.ttf'),
    'small': os.path.join(FONTS_DIR, 'Inter-Regular.ttf'),
    'log': os.path.join(FONTS_DIR, 'Inter-Regular.ttf'),
}
FONT_FALLBACKS = {
    'title': 'georgia',
    'subtitle': 'georgia',
    'ui': 'segoeui',
    'ui_bold': 'segoeui',
    'card': 'arial',
    'card_bold': 'arial',
    'small': 'segoeui',
    'log': 'segoeui',
}
