"""Display constants."""
import math
import os
import re

from cubing_algs.annotations import RegexPattern

DEFAULT_EFFECT = os.getenv('CUBING_ALGS_EFFECT', '')
DEFAULT_PALETTE = os.getenv('CUBING_ALGS_PALETTE', 'default')
DEFAULT_STYLE = os.getenv('CUBING_ALGS_STYLE', 'default')

ANSI_TO_RGB: RegexPattern = re.compile(
    r'\x1b\[48;2;(\d+);(\d+);(\d+)m\x1b\[38;2;(\d+);(\d+);(\d+)m',
)

EMOJIS = {
    'U': '⬜',
    'D': '🟨',
    'F': '🟩',
    'B': '🟦',
    'L': '🟧',
    'R': '🟥',
    'masked': '⬛',
    'hidden': '❓',
}

LAYOUT_METHODS: dict[str, str] = {
    'top': 'display_top_face',
    'extended': 'display_extended_net',
    'linear': 'display_linear',
    'cube': 'display_cube',
}

F2L_FACE_ORIENTATIONS = {
    'FL': 'F',
    'FR': 'R',
    'BL': 'L',
    'BR': 'B',
}

F2L_ADJACENT_FACES = {
    'R': ('B', 'F'),
    'L': ('F', 'B'),
    'B': ('L', 'R'),
    'F': ('R', 'L'),
}

MIN_DISTANCE = math.sqrt(3)

IMAGE_SIZE = 200

DISTANCE = 10.0

ROTATION = 'y45x-34'

# Gap between stickers as a fraction of face size (divided by 3 per cell)
STICKER_GAP = 0.08
VISIBILITY_EPSILON = 1e-9

# Strip projection depth in cell units
STRIP_DEPTH = 0.4

# Inward taper per side as fraction of U face edge length
STRIP_TAPER = 0.05
