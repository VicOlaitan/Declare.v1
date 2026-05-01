"""High-quality card painter.

Loads real public-domain PNG cards from assets/cards/ when available, falls
back to procedural rendering when not. Procedural fallback is still high
quality (paper texture, pip layouts, deco face cards) so the game looks
right whether or not the asset pack was downloaded.
"""
import math
import os
import pygame
import random

import theme
from config import CARD_WIDTH, CARD_HEIGHT, CORNER_RADIUS


_FACE_CACHE = {}
_BACK_CACHE = {}
_RAW_PNG_CACHE = {}


def _assets_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "cards")


def _load_png_face(card):
    key = (card.rank, card.suit)
    if key in _RAW_PNG_CACHE:
        return _RAW_PNG_CACHE[key]
    path = os.path.join(_assets_dir(), f"{card.rank}_{card.suit}.png")
    if not os.path.exists(path):
        _RAW_PNG_CACHE[key] = None
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        _RAW_PNG_CACHE[key] = None
        return None
    _RAW_PNG_CACHE[key] = surf
    return surf


def _load_png_back(style):
    key = ("back", style)
    if key in _RAW_PNG_CACHE:
        return _RAW_PNG_CACHE[key]
    style_filename = {
        "classic": "back_red.png",
        "deco_brass": "back_red.png",
        "deco_emerald": "back_red.png",
        "deco_obsidian": "back_red.png",
    }.get(style, "back_red.png")
    path = os.path.join(_assets_dir(), style_filename)
    if not os.path.exists(path):
        _RAW_PNG_CACHE[key] = None
        return None
    try:
        surf = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        _RAW_PNG_CACHE[key] = None
        return None
    _RAW_PNG_CACHE[key] = surf
    return surf


def _scaled_to_card(src, w, h):
    if src.get_size() == (w, h):
        return src
    return pygame.transform.smoothscale(src, (w, h))


def invalidate_cache():
    _FACE_CACHE.clear()
    _BACK_CACHE.clear()


def _font(size, bold=True):
    import typography as typo
    return typo.body_bold(size) if bold else typo.body(size)


def _serif_font(size, bold=True):
    import typography as typo
    return typo.header_bold(size) if bold else typo.header(size)


SUIT_GLYPH = {"spade": "♠", "heart": "♥", "diamond": "♦", "club": "♣"}


def _draw_corner_chip(surf, card, w, h):
    """Paint a small high-contrast rank+suit indicator in the top-left corner.

    Suit drawn as a polygon (not a font glyph) so missing-Unicode fonts can't
    break it. Subtle paper-color background so it doesn't fight the card art."""
    color = (178, 34, 34) if card.is_red else (26, 26, 26)
    rank_size = max(13, int(h * 0.16))
    rank_font = _serif_font(rank_size, bold=True)
    rank_surf = rank_font.render(card.rank, True, color)
    suit_pip_size = max(7, int(h * 0.09))

    chip_w = max(rank_surf.get_width(), suit_pip_size * 2) + 10
    chip_h = rank_surf.get_height() + suit_pip_size * 2 + 6
    chip = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
    pygame.draw.rect(chip, (244, 236, 216, 240), chip.get_rect(), border_radius=4)
    pygame.draw.rect(chip, (*color, 110), chip.get_rect(), 1, border_radius=4)
    chip.blit(rank_surf, ((chip_w - rank_surf.get_width()) // 2, 1))
    suit_cy = rank_surf.get_height() + suit_pip_size + 2
    _draw_pip(chip, chip_w // 2, suit_cy, card.suit, color, size=suit_pip_size)
    surf.blit(chip, (3, 3))

    chip_rot = pygame.transform.rotate(chip, 180)
    surf.blit(chip_rot, (w - chip_rot.get_width() - 3, h - chip_rot.get_height() - 3))


def _ink(card):
    th = theme.active()
    return th.ink_red if card.is_red else th.ink_black


def _paper(width=CARD_WIDTH, height=CARD_HEIGHT):
    th = theme.active()
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    base = th.paper_warm
    pygame.draw.rect(surf, base, surf.get_rect(), border_radius=CORNER_RADIUS)
    rng = random.Random((width << 8) ^ height ^ sum(base))
    grain = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range(60):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        a = rng.randint(8, 18)
        pygame.draw.circle(grain, (200, 188, 160, a), (x, y), 1)
    surf.blit(grain, (0, 0))

    bevel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.line(bevel, (255, 250, 235, 70), (4, 3), (width - 5, 3), 1)
    pygame.draw.line(bevel, (255, 250, 235, 50), (3, 4), (3, height - 5), 1)
    pygame.draw.line(bevel, (60, 40, 20, 50), (4, height - 4), (width - 5, height - 4), 1)
    pygame.draw.line(bevel, (60, 40, 20, 50), (width - 4, 4), (width - 4, height - 5), 1)
    surf.blit(bevel, (0, 0))

    edge_color = (*th.paper_edge, 200)
    pygame.draw.rect(surf, edge_color, surf.get_rect(), 1, border_radius=CORNER_RADIUS)
    return surf


def _draw_pip(surf, cx, cy, suit, color, size=8, flipped=False):
    if suit == "spade":
        pts = [(cx, cy - size), (cx + size * 0.85, cy + size * 0.5),
               (cx, cy + size * 0.85), (cx - size * 0.85, cy + size * 0.5)]
        pygame.draw.polygon(surf, color, pts)
        stem_top = cy + size * 0.4
        pygame.draw.polygon(surf, color, [
            (cx - size * 0.3, stem_top),
            (cx + size * 0.3, stem_top),
            (cx, stem_top + size * 0.55),
        ])
    elif suit == "heart":
        r = size * 0.55
        pygame.draw.circle(surf, color, (int(cx - r * 0.85), int(cy - r * 0.4)), int(r))
        pygame.draw.circle(surf, color, (int(cx + r * 0.85), int(cy - r * 0.4)), int(r))
        pts = [(cx - size * 1.2, cy - r * 0.1),
               (cx, cy + size * 0.95),
               (cx + size * 1.2, cy - r * 0.1)]
        pygame.draw.polygon(surf, color, pts)
        if flipped:
            pass
    elif suit == "diamond":
        pts = [(cx, cy - size * 1.05), (cx + size * 0.78, cy),
               (cx, cy + size * 1.05), (cx - size * 0.78, cy)]
        pygame.draw.polygon(surf, color, pts)
    elif suit == "club":
        r = size * 0.55
        pygame.draw.circle(surf, color, (int(cx), int(cy - size * 0.6)), int(r))
        pygame.draw.circle(surf, color, (int(cx - size * 0.65), int(cy + size * 0.05)), int(r))
        pygame.draw.circle(surf, color, (int(cx + size * 0.65), int(cy + size * 0.05)), int(r))
        pygame.draw.polygon(surf, color, [
            (cx - size * 0.3, cy + size * 0.4),
            (cx + size * 0.3, cy + size * 0.4),
            (cx, cy + size * 1.1),
        ])


def _pip_layout(rank):
    """Return list of (x_norm, y_norm, flipped) in [0..1] coords for a rank's pips."""
    L = 0.5
    cols = (0.32, 0.5, 0.68)
    rows7 = (0.18, 0.30, 0.42, 0.5, 0.58, 0.70, 0.82)
    if rank == "A":
        return [(L, 0.5, False)]
    if rank == "2":
        return [(L, 0.22, False), (L, 0.78, True)]
    if rank == "3":
        return [(L, 0.22, False), (L, 0.5, False), (L, 0.78, True)]
    if rank == "4":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "5":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (L, 0.5, False),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "6":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (cols[0], 0.5, False), (cols[2], 0.5, False),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "7":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (L, 0.36, False),
                (cols[0], 0.5, False), (cols[2], 0.5, False),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "8":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (L, 0.36, False),
                (cols[0], 0.5, False), (cols[2], 0.5, False),
                (L, 0.64, True),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "9":
        return [(cols[0], 0.22, False), (cols[2], 0.22, False),
                (cols[0], 0.4, False), (cols[2], 0.4, False),
                (L, 0.5, False),
                (cols[0], 0.6, True), (cols[2], 0.6, True),
                (cols[0], 0.78, True), (cols[2], 0.78, True)]
    if rank == "10":
        return [(cols[0], 0.18, False), (cols[2], 0.18, False),
                (L, 0.30, False),
                (cols[0], 0.40, False), (cols[2], 0.40, False),
                (cols[0], 0.60, True), (cols[2], 0.60, True),
                (L, 0.70, True),
                (cols[0], 0.82, True), (cols[2], 0.82, True)]
    return []


def _draw_corner_index(surf, x, y, rank, suit, color, w, h, mirrored=False):
    rank_font = _font(max(11, int(15 * w / CARD_WIDTH)), bold=True)
    suit_font = _font(max(9, int(13 * w / CARD_WIDTH)), bold=True)
    rs = rank_font.render(rank, True, color)
    sg = suit_font.render(SUIT_GLYPH.get(suit, "?"), True, color)
    if mirrored:
        rs = pygame.transform.rotate(rs, 180)
        sg = pygame.transform.rotate(sg, 180)
        surf.blit(rs, (x - rs.get_width(), y - rs.get_height() - sg.get_height() + 2))
        surf.blit(sg, (x - sg.get_width(), y - sg.get_height() + 2))
    else:
        surf.blit(rs, (x, y))
        surf.blit(sg, (x, y + rs.get_height() - 2))


def _draw_face_card(surf, rank, suit, color, w, h):
    """Procedural face cards: silhouette portrait with deco motifs."""
    cx, cy = w // 2, h // 2

    panel = pygame.Surface((int(w * 0.62), int(h * 0.62)), pygame.SRCALPHA)
    pr = panel.get_rect()
    panel_color = (*color[:3], 30)
    pygame.draw.rect(panel, panel_color, pr, border_radius=6)
    pygame.draw.rect(panel, (*color[:3], 110), pr, 1, border_radius=6)
    surf.blit(panel, (cx - pr.width // 2, cy - pr.height // 2))

    def line(x1, y1, x2, y2, width=1):
        pygame.draw.line(surf, color, (cx + x1, cy + y1), (cx + x2, cy + y2), width)

    if rank == "J":
        head_r = int(h * 0.10)
        pygame.draw.circle(surf, color, (cx, cy - int(h * 0.18)), head_r, 2)
        line(-head_r * 0.7, -h * 0.18 + head_r * 0.3, head_r * 0.7, -h * 0.18 + head_r * 0.3, 2)
        line(0, -h * 0.18 + head_r, 0, h * 0.10, 2)
        line(-int(w * 0.18), 0, int(w * 0.18), 0, 2)
        line(-int(w * 0.18), 0, -int(w * 0.10), int(h * 0.18), 2)
        line(int(w * 0.18), 0, int(w * 0.10), int(h * 0.18), 2)
        line(0, h * 0.10, -int(w * 0.10), int(h * 0.22), 2)
        line(0, h * 0.10, int(w * 0.10), int(h * 0.22), 2)
        for i in range(3):
            t = -head_r + i * head_r * 0.6
            line(t, -h * 0.30, t + head_r * 0.3, -h * 0.36, 2)
    elif rank == "Q":
        head_r = int(h * 0.10)
        pygame.draw.circle(surf, color, (cx, cy - int(h * 0.18)), head_r, 2)
        crown_pts = [
            (cx - head_r, cy - int(h * 0.20) - head_r * 0.4),
            (cx - head_r * 0.7, cy - int(h * 0.20) - head_r * 1.2),
            (cx - head_r * 0.3, cy - int(h * 0.20) - head_r * 0.7),
            (cx, cy - int(h * 0.20) - head_r * 1.4),
            (cx + head_r * 0.3, cy - int(h * 0.20) - head_r * 0.7),
            (cx + head_r * 0.7, cy - int(h * 0.20) - head_r * 1.2),
            (cx + head_r, cy - int(h * 0.20) - head_r * 0.4),
        ]
        pygame.draw.lines(surf, color, False, crown_pts, 2)
        line(-int(w * 0.20), -h * 0.05, int(w * 0.20), -h * 0.05, 2)
        line(-int(w * 0.20), -h * 0.05, -int(w * 0.22), int(h * 0.20), 2)
        line(int(w * 0.20), -h * 0.05, int(w * 0.22), int(h * 0.20), 2)
        line(0, -h * 0.05, 0, int(h * 0.18), 2)
        line(-head_r * 0.7, -h * 0.18 + head_r * 0.3, head_r * 0.7, -h * 0.18 + head_r * 0.3, 1)
    elif rank == "K":
        head_r = int(h * 0.11)
        pygame.draw.circle(surf, color, (cx, cy - int(h * 0.16)), head_r, 2)
        cy_crown = cy - int(h * 0.18) - head_r
        crown_pts = [
            (cx - head_r * 1.1, cy_crown),
            (cx - head_r * 0.7, cy_crown - head_r * 0.9),
            (cx - head_r * 0.2, cy_crown - head_r * 0.4),
            (cx, cy_crown - head_r * 1.3),
            (cx + head_r * 0.2, cy_crown - head_r * 0.4),
            (cx + head_r * 0.7, cy_crown - head_r * 0.9),
            (cx + head_r * 1.1, cy_crown),
        ]
        pygame.draw.lines(surf, color, False, crown_pts, 2)
        cross_y = cy_crown - head_r * 1.6
        line(0, cy_crown - h * 0 - cy + cross_y, 0, cy_crown - h * 0 - cy + cross_y - head_r * 0.7, 2)
        line(-head_r * 0.3, cy_crown - h * 0 - cy + cross_y - head_r * 0.4,
             head_r * 0.3, cy_crown - h * 0 - cy + cross_y - head_r * 0.4, 2)
        beard_pts = [
            (cx - head_r * 0.7, cy - int(h * 0.16) + head_r * 0.5),
            (cx - head_r * 0.4, cy - int(h * 0.16) + head_r * 1.2),
            (cx, cy - int(h * 0.16) + head_r * 0.9),
            (cx + head_r * 0.4, cy - int(h * 0.16) + head_r * 1.2),
            (cx + head_r * 0.7, cy - int(h * 0.16) + head_r * 0.5),
        ]
        pygame.draw.lines(surf, color, False, beard_pts, 2)
        line(-int(w * 0.22), -h * 0.02, int(w * 0.22), -h * 0.02, 3)
        line(-int(w * 0.22), -h * 0.02, -int(w * 0.24), int(h * 0.20), 2)
        line(int(w * 0.22), -h * 0.02, int(w * 0.24), int(h * 0.20), 2)

        if suit in ("heart", "diamond"):
            arr_color = (*color[:3], 180)
            sx, sy = cx - int(w * 0.30), cy + int(h * 0.05)
            ex, ey = cx + int(w * 0.30), cy + int(h * 0.05)
            arrow_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pygame.draw.line(arrow_surf, arr_color, (sx, sy + int(h * 0.05)), (ex, ey - int(h * 0.05)), 2)
            pygame.draw.line(arrow_surf, arr_color, (sx, sy - int(h * 0.05)), (ex, ey + int(h * 0.05)), 2)
            head1 = [(ex, ey - int(h * 0.05)), (ex - int(w * 0.06), ey - int(h * 0.10)), (ex - int(w * 0.06), ey)]
            head2 = [(ex, ey + int(h * 0.05)), (ex - int(w * 0.06), ey + int(h * 0.10)), (ex - int(w * 0.06), ey)]
            pygame.draw.polygon(arrow_surf, arr_color, head1)
            pygame.draw.polygon(arrow_surf, arr_color, head2)
            surf.blit(arrow_surf, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)


def _draw_black_king_zero(surf, w, h, color):
    cx, cy = w // 2, h // 2
    th = theme.active()
    badge_r = int(h * 0.13)
    pygame.draw.circle(surf, (*color[:3], 50), (cx, cy + int(h * 0.30)), badge_r)
    pygame.draw.circle(surf, color, (cx, cy + int(h * 0.30)), badge_r, 2)
    z_font = _serif_font(max(14, int(20 * w / CARD_WIDTH)), bold=True)
    z = z_font.render("0", True, color)
    surf.blit(z, z.get_rect(center=(cx, cy + int(h * 0.30))))


def paint_face(card, w=CARD_WIDTH, h=CARD_HEIGHT):
    th = theme.active()
    cache_key = (card.rank, card.suit, w, h, th.name, th.high_contrast,
                 tuple(th.ink_red), tuple(th.ink_black), tuple(th.paper_warm))
    if cache_key in _FACE_CACHE:
        return _FACE_CACHE[cache_key]

    real = _load_png_face(card)
    if real is not None:
        scaled = _scaled_to_card(real, w, h)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                         border_radius=CORNER_RADIUS)
        surf.blit(scaled, (0, 0))
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        if card.rank == "K" and not card.is_red:
            badge_r = max(7, int(h * 0.10))
            cx, cy = int(w * 0.82), int(h * 0.18)
            pygame.draw.circle(surf, (20, 20, 20), (cx, cy), badge_r)
            pygame.draw.circle(surf, (220, 195, 110), (cx, cy), badge_r, 2)
            zfont = _serif_font(max(10, int(badge_r * 1.4)), bold=True)
            z = zfont.render("0", True, (220, 195, 110))
            surf.blit(z, z.get_rect(center=(cx, cy)))
        if getattr(card, "power", None):
            from config import POWER_COLORS
            glow_color = POWER_COLORS.get(card.power, (180, 180, 180))
            pygame.draw.rect(surf, (*glow_color, 90), surf.get_rect(),
                             2, border_radius=CORNER_RADIUS)
        pygame.draw.rect(surf, (40, 40, 40, 200), surf.get_rect(), 1,
                         border_radius=CORNER_RADIUS)
        _FACE_CACHE[cache_key] = surf
        return surf

    surf = _paper(w, h)
    color = th.ink_red if card.is_red else th.ink_black

    bar = pygame.Surface((6, h - 8), pygame.SRCALPHA)
    pygame.draw.rect(bar, (*color[:3], 200), bar.get_rect(), border_radius=2)
    surf.blit(bar, (3, 4))

    pad = 5
    _draw_corner_index(surf, pad, pad, card.rank, card.suit, color, w, h, mirrored=False)
    _draw_corner_index(surf, w - pad, h - pad, card.rank, card.suit, color, w, h, mirrored=True)

    if card.rank in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10"):
        if card.rank == "A":
            big_pip_size = int(min(w, h) * 0.25)
            _draw_pip(surf, w // 2, h // 2, card.suit, color, size=big_pip_size)
        else:
            for nx, ny, flipped in _pip_layout(card.rank):
                px = int(w * (0.18 + (nx - 0.18) * 1.0))
                py = int(h * ny)
                _draw_pip(surf, px, py, card.suit, color, size=int(min(w, h) * 0.075), flipped=flipped)
    elif card.rank in ("J", "Q", "K"):
        _draw_face_card(surf, card.rank, card.suit, color, w, h)
        if card.rank == "K" and not card.is_red:
            _draw_black_king_zero(surf, w, h, color)

    if getattr(card, "power", None):
        from config import POWER_COLORS
        glow_color = POWER_COLORS.get(card.power, (180, 180, 180))
        flourish = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(flourish, (*glow_color, 70), pygame.Rect(0, 0, w, h),
                         2, border_radius=CORNER_RADIUS)
        surf.blit(flourish, (0, 0))

    pygame.draw.rect(surf, (*th.paper_edge, 220), surf.get_rect(), 1,
                     border_radius=CORNER_RADIUS)

    _FACE_CACHE[cache_key] = surf
    return surf


def paint_back(style="classic", w=CARD_WIDTH, h=CARD_HEIGHT):
    th = theme.active()
    cache_key = (style, w, h, th.name, th.high_contrast,
                 tuple(th.card_back_a), tuple(th.card_back_b))
    if cache_key in _BACK_CACHE:
        return _BACK_CACHE[cache_key]

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    a, b, motif = _back_palette(style, th)

    # ----- 1. Gradient base, masked to rounded rect -----
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    if style == "deco_obsidian":
        # Radial gradient: lighter at center, near-black at edges
        cx_g, cy_g = w / 2, h / 2
        max_r = math.hypot(cx_g, cy_g)
        for i in range(h):
            for j_step in range(0, w, 2):
                d = math.hypot(j_step - cx_g, i - cy_g) / max_r
                t = min(1.0, d * 1.2)
                r = int(b[0] + (a[0] - b[0]) * t)
                g = int(b[1] + (a[1] - b[1]) * t)
                bl = int(b[2] + (a[2] - b[2]) * t)
                pygame.draw.line(grad, (r, g, bl, 255), (j_step, i), (j_step + 2, i))
    else:
        # Vertical gradient
        for i in range(h):
            t = i / max(1, h - 1)
            r = int(a[0] + (b[0] - a[0]) * t)
            g = int(a[1] + (b[1] - a[1]) * t)
            bl = int(a[2] + (b[2] - a[2]) * t)
            pygame.draw.line(grad, (r, g, bl, 255), (0, i), (w, i))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=CORNER_RADIUS)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, (0, 0))

    # ----- 2. Per-style pattern overlay -----
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    if style == "deco_emerald":
        # Diamond-lattice: rows of small rotated diamonds.
        cell = max(10, w // 12)
        for row in range(-1, h // cell + 2):
            for col in range(-1, w // cell + 2):
                ox = col * cell + (cell // 2 if row % 2 else 0)
                oy = row * cell
                pts = [(ox, oy - cell // 4), (ox + cell // 4, oy),
                       (ox, oy + cell // 4), (ox - cell // 4, oy)]
                pygame.draw.polygon(overlay, (*motif[:3], 18), pts, 1)
    elif style == "deco_brass":
        # Sunburst rays from the top center
        ray_origin = (w // 2, h // 8)
        for k in range(-9, 10):
            angle = math.pi / 2 + k * (math.pi / 24)
            x_end = ray_origin[0] + int(math.cos(angle) * h * 1.3)
            y_end = ray_origin[1] + int(math.sin(angle) * h * 1.3)
            pygame.draw.line(overlay, (*motif[:3], 14),
                             ray_origin, (x_end, y_end), 1)
    elif style == "deco_obsidian":
        # Hex/honeycomb pattern in muted gold
        hr = max(8, w // 14)
        for row in range(-1, h // hr + 2):
            for col in range(-1, w // hr + 2):
                hx = col * int(hr * 1.7) + (hr if row % 2 else 0)
                hy = row * int(hr * 1.5)
                pts = []
                for kk in range(6):
                    aa = math.pi / 3 * kk + math.pi / 6
                    pts.append((hx + math.cos(aa) * hr,
                                hy + math.sin(aa) * hr))
                pygame.draw.polygon(overlay, (*motif[:3], 16), pts, 1)
        # Small "starfield" specks
        rng = random.Random(7)
        for _ in range(int(w * h / 600)):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, h - 1)
            sa = rng.randint(40, 120)
            pygame.draw.circle(overlay, (*motif[:3], sa), (sx, sy), 1)
    else:
        # Classic: cross-hatch
        spacing = 12
        for x_step in range(-h, w + h, spacing):
            pygame.draw.line(overlay, (*motif[:3], 22), (x_step, 0), (x_step + h, h), 1)
            pygame.draw.line(overlay, (*motif[:3], 22), (x_step, h), (x_step + h, 0), 1)
    overlay.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(overlay, (0, 0))

    # ----- 3. Inner double border -----
    inner = pygame.Rect(5, 5, w - 10, h - 10)
    pygame.draw.rect(surf, (*motif[:3], 80), inner, 2, border_radius=CORNER_RADIUS - 2)
    inner2 = pygame.Rect(8, 8, w - 16, h - 16)
    pygame.draw.rect(surf, (*motif[:3], 40), inner2, 1, border_radius=CORNER_RADIUS - 4)

    # ----- 4. Central medallion + per-style ornament -----
    cx, cy = w // 2, h // 2
    medallion_w = int(w * 0.55)
    medallion_h = int(h * 0.40)
    medallion = pygame.Rect(cx - medallion_w // 2, cy - medallion_h // 2,
                            medallion_w, medallion_h)

    if style == "deco_emerald":
        # Stacked emerald-cut ovals
        for i in range(5):
            t = i / 4
            inner_e = pygame.Rect(
                medallion.x + int(medallion.width * 0.08 * i),
                medallion.y + int(medallion.height * 0.08 * i),
                medallion.width - int(medallion.width * 0.16 * i),
                medallion.height - int(medallion.height * 0.16 * i),
            )
            alpha = int(140 - i * 20)
            pygame.draw.ellipse(surf, (*motif[:3], alpha), inner_e, 2 if i == 0 else 1)
        # 8 facet lines suggesting a cut gem
        gem_r_x, gem_r_y = medallion_w // 4, medallion_h // 4
        for k in range(8):
            ang = math.pi * 2 * k / 8
            pygame.draw.line(surf, (*motif[:3], 110),
                             (cx, cy),
                             (cx + int(math.cos(ang) * gem_r_x),
                              cy + int(math.sin(ang) * gem_r_y)), 1)
        # Inner sparkle
        pygame.draw.circle(surf, (255, 255, 255, 200), (cx - 2, cy - 2), 2)

    elif style == "deco_obsidian":
        # Sun-burst rosette: 16 rays + central rosette
        sun_r = min(medallion_w, medallion_h) // 4
        # Outer ray ring
        for k in range(16):
            ang = math.pi * 2 * k / 16
            inner_pt = (cx + int(math.cos(ang) * sun_r),
                        cy + int(math.sin(ang) * sun_r))
            outer_pt = (cx + int(math.cos(ang) * (sun_r * 1.9)),
                        cy + int(math.sin(ang) * (sun_r * 1.9)))
            width = 2 if k % 2 == 0 else 1
            pygame.draw.line(surf, motif, inner_pt, outer_pt, width)
        # Central concentric rings
        pygame.draw.circle(surf, motif, (cx, cy), sun_r, 2)
        pygame.draw.circle(surf, (*motif[:3], 160), (cx, cy), int(sun_r * 0.65), 1)
        pygame.draw.circle(surf, (*motif[:3], 200), (cx, cy), int(sun_r * 0.30))
        # Tiny pearl highlight
        pygame.draw.circle(surf, (255, 255, 255, 220), (cx - 1, cy - 2), 2)

    elif style == "deco_brass":
        # Octagonal medallion with stepped corners + monogram
        oct_pts = []
        ow, oh = medallion_w // 2, medallion_h // 2
        chamfer = min(ow, oh) // 3
        oct_pts = [
            (cx - ow + chamfer, cy - oh), (cx + ow - chamfer, cy - oh),
            (cx + ow, cy - oh + chamfer), (cx + ow, cy + oh - chamfer),
            (cx + ow - chamfer, cy + oh), (cx - ow + chamfer, cy + oh),
            (cx - ow, cy + oh - chamfer), (cx - ow, cy - oh + chamfer),
        ]
        pygame.draw.polygon(surf, (*motif[:3], 100), oct_pts)
        pygame.draw.polygon(surf, motif, oct_pts, 2)
        # Inner octagonal frame
        i_pts = [(int(cx + (px - cx) * 0.78), int(cy + (py - cy) * 0.78))
                 for (px, py) in oct_pts]
        pygame.draw.polygon(surf, (*motif[:3], 80), i_pts, 1)
        # Monogram diamond at center
        d_size = min(ow, oh) // 3
        d_pts = [(cx, cy - d_size), (cx + d_size, cy),
                 (cx, cy + d_size), (cx - d_size, cy)]
        pygame.draw.polygon(surf, motif, d_pts)
        pygame.draw.polygon(surf, (255, 255, 255, 60), d_pts, 1)
        # Vertical brass bars flanking the diamond
        for sign in (-1, 1):
            pygame.draw.line(surf, (*motif[:3], 180),
                             (cx + sign * (d_size + 6), cy - d_size + 2),
                             (cx + sign * (d_size + 6), cy + d_size - 2), 2)

    else:
        # Classic: oval medallion with central diamond
        pygame.draw.ellipse(surf, (*motif[:3], 90), medallion)
        pygame.draw.ellipse(surf, motif, medallion, 2)
        d_pts = [(cx, cy - 10), (cx + 6, cy), (cx, cy + 10), (cx - 6, cy)]
        pygame.draw.polygon(surf, motif, d_pts)

    # ----- 5. Corner ornaments (per-style) -----
    corner_inset = max(8, w // 18)
    if style == "deco_emerald":
        for cx_o, cy_o in [(corner_inset, corner_inset), (w - corner_inset, corner_inset),
                            (corner_inset, h - corner_inset), (w - corner_inset, h - corner_inset)]:
            d = max(3, w // 50)
            pts = [(cx_o, cy_o - d), (cx_o + d, cy_o), (cx_o, cy_o + d), (cx_o - d, cy_o)]
            pygame.draw.polygon(surf, motif, pts)
    elif style == "deco_obsidian":
        for cx_o, cy_o in [(corner_inset, corner_inset), (w - corner_inset, corner_inset),
                            (corner_inset, h - corner_inset), (w - corner_inset, h - corner_inset)]:
            r = max(2, w // 70)
            pygame.draw.circle(surf, motif, (cx_o, cy_o), r, 1)
            pygame.draw.circle(surf, motif, (cx_o, cy_o), max(1, r // 2))
    elif style == "deco_brass":
        # Trefoil flourishes in each corner
        size = max(6, w // 26)
        for sx, sy, fx, fy in [
            (corner_inset, corner_inset, 1, 1),
            (w - corner_inset, corner_inset, -1, 1),
            (corner_inset, h - corner_inset, 1, -1),
            (w - corner_inset, h - corner_inset, -1, -1),
        ]:
            pygame.draw.circle(surf, motif, (sx, sy), max(2, size // 4))
            pygame.draw.line(surf, motif, (sx, sy),
                             (sx + fx * size, sy), 1)
            pygame.draw.line(surf, motif, (sx, sy),
                             (sx, sy + fy * size), 1)

    # ----- 6. Outer frame + top/left highlight -----
    pygame.draw.rect(surf, (*motif[:3], 220), surf.get_rect(), 1, border_radius=CORNER_RADIUS)
    pygame.draw.line(surf, (255, 255, 255, 70), (4, 3), (w - 5, 3), 1)
    pygame.draw.line(surf, (255, 255, 255, 35), (3, 4), (3, h - 5), 1)

    _BACK_CACHE[cache_key] = surf
    return surf


def _back_palette(style, th):
    if style == "deco_emerald":
        return ((10, 60, 40), (30, 110, 70), (220, 200, 130))
    if style == "deco_obsidian":
        return ((18, 18, 22), (40, 40, 50), (220, 200, 130))
    if style == "deco_brass":
        return ((40, 30, 18), (90, 65, 30), (240, 200, 110))
    return (th.card_back_a, th.card_back_b, th.card_back_motif)


def paint_back_glow(style="classic", w=CARD_WIDTH, h=CARD_HEIGHT, t=0.0):
    """Animated card-back shimmer overlay; called per-frame for the active deck."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    band_y = int(h * (0.5 + 0.5 * math.sin(t * 0.6)))
    for offs in range(-12, 13):
        a = max(0, 30 - abs(offs) * 2)
        if a <= 0:
            continue
        pygame.draw.line(surf, (255, 230, 170, a),
                         (0, band_y + offs), (w, band_y + offs), 1)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=CORNER_RADIUS)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return surf
