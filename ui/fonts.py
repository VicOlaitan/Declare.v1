import os
import urllib.request
import zipfile
import tempfile
import shutil
from config import FONT_PATHS, FONTS_DIR, FONT_FALLBACKS

FONT_URLS = {
    'Cinzel': 'https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf',
    'Inter': 'https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bwght%5D.ttf',
    'Roboto': 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto%5Bwdth%2Cwght%5D.ttf',
}

FONT_WEIGHTS = {
    'Cinzel': {'Regular': 400, 'Bold': 700},
    'Inter': {'Regular': 400, 'SemiBold': 600},
    'Roboto': {'Regular': 400, 'Bold': 700},
}

FONT_FILE_MAP = {
    'Cinzel-Bold.ttf': 'Cinzel',
    'Cinzel-Regular.ttf': 'Cinzel',
    'Inter-Regular.ttf': 'Inter',
    'Inter-SemiBold.ttf': 'Inter',
    'Roboto-Regular.ttf': 'Roboto',
    'Roboto-Bold.ttf': 'Roboto',
}


def download_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    downloaded = []
    for filename, family in FONT_FILE_MAP.items():
        dest = os.path.join(FONTS_DIR, filename)
        if os.path.exists(dest):
            continue
        url = FONT_URLS[family]
        print(f"Downloading {family} -> {filename}...")
        try:
            urllib.request.urlretrieve(url, dest)
            downloaded.append(filename)
        except Exception as e:
            print(f"  Failed to download {family}: {e}")
            print(f"  Falling back to system fonts for {family}")
    if downloaded:
        print(f"\nDownloaded {len(downloaded)} font file(s) to {FONTS_DIR}")
    else:
        print("All fonts already present or download failed.")
    return downloaded


def get_font(role, size, bold=False):
    import pygame
    path = FONT_PATHS.get(role, '')
    if bold and role in FONT_PATHS:
        bold_key = role + '_bold' if role + '_bold' in FONT_PATHS else role
        path = FONT_PATHS.get(bold_key, path)
    if path and os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except Exception:
            pass
    fallback = FONT_FALLBACKS.get(role, 'arial')
    return pygame.font.SysFont(fallback, size, bold=bold)


if __name__ == '__main__':
    download_fonts()
