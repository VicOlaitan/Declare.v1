#!/usr/bin/env python3
"""Download Google Fonts for the Declare card game.
Run this once to fetch Cinzel, Inter, and Roboto font files.
Falls back to system fonts if download fails.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.fonts import download_fonts

if __name__ == '__main__':
    download_fonts()
