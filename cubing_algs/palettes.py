import os

from cubing_algs.constants import FACE_ORDER

LOADED_PALETTES: dict[str, dict[str, str]] = {}


def rgb_to_ansi(domain: str, r: int, g: int, b: int) -> str:
    """Convert RGB values to ANSI escape code."""
    return f'\x1b[{ domain };2;{ r };{ g };{ b }m'


def background_rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB value to ANSI background color code."""
    return rgb_to_ansi('48', r, g, b)


def foreground_rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB value to ANSI foreground color code."""
    return rgb_to_ansi('38', r, g, b)


def build_ansi_color(
        background_rgb: tuple[int, int, int],
        foreground_rgb: tuple[int, int, int]) -> str:
    """Build a complete ANSI color scheme"""
    return (
        background_rgb_to_ansi(*background_rgb)
        + foreground_rgb_to_ansi(*foreground_rgb)
    )


PALETTES = {
    'default': {
        'faces_background_rgb': (
            (228, 228, 228),
            (255, 0, 0),
            (0, 215, 0),
            (255, 255, 0),
            (255, 135, 0),
            (0, 0, 255),
        ),
        'extra': {
            'B': build_ansi_color(
                (0, 0, 255),
                (255, 255, 215),
            ),
            'B_hidden': build_ansi_color(
                (68, 68, 68),
                (0, 185, 255),
            ),
            'L_hidden': build_ansi_color(
                (68, 68, 68),
                (255, 170, 0),
            ),
        },
    },
    'rgb': {
        'faces_background_rgb': (
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (255, 127, 0),
            (0, 0, 255),
        ),
    },
    'vibrant': {
        'faces_background_rgb': (
            (255, 255, 255),
            (255, 65, 54),
            (46, 213, 115),
            (255, 234, 167),
            (255, 159, 67),
            (116, 185, 255),
        ),
    },
    'neon': {
        'faces_background_rgb': (
            (255, 255, 255),
            (255, 20, 147),
            (0, 255, 127),
            (255, 255, 0),
            (255, 140, 0),
            (0, 191, 255),
        ),
    },
    'metal': {
        'faces_background_rgb': (
            (220, 220, 220),
            (180, 100, 60),
            (120, 140, 80),
            (200, 160, 50),
            (200, 120, 80),
            (100, 160, 200),
        ),
    },
    'pastel': {
        'faces_background_rgb': (
            (255, 255, 255),
            (255, 182, 193),
            (152, 251, 152),
            (255, 241, 146),
            (255, 218, 185),
            (173, 216, 230),
        ),
    },
    'dracula': {
        'faces_background_rgb': (
            (248, 248, 242),
            (255, 85, 85),
            (80, 250, 123),
            (241, 250, 140),
            (255, 184, 108),
            (139, 233, 253),
        ),
        'font_foreground_ansi': foreground_rgb_to_ansi(
            40, 42, 54,
        ),
        'hidden_background_ansi': background_rgb_to_ansi(
            68, 71, 90,
        ),
        'masked_ansi': build_ansi_color(
            (40, 42, 54),
            (248, 248, 242),
        ),
    },
    'alucard': {
        'faces_background_rgb': (
            (255, 251, 235),
            (203, 58, 42),
            (20, 113, 10),
            (132, 110, 21),
            (163, 77, 20),
            (3, 106, 150),
        ),
        'font_foreground_ansi': foreground_rgb_to_ansi(
            255, 251, 235,
        ),
        'hidden_background_ansi': background_rgb_to_ansi(
            207, 207, 222,
        ),
        'masked_ansi': build_ansi_color(
            (108, 102, 75),
            (255, 251, 235),
        ),
        'extra': {
            'U': build_ansi_color(
                (255, 251, 235),
                (31, 31, 31),
            ),
        },
    },
}

DEFAULT_FONT_FOREGROUND_ANSI = foreground_rgb_to_ansi(
    8, 8, 8,
)

DEFAULT_HIDDEN_BACKGROUND_ANSI = background_rgb_to_ansi(
    68, 68, 68,
)

DEFAULT_MASKED_ANSI = build_ansi_color(
    (48, 48, 48),
    (208, 208, 208),
)


def build_ansi_palette(
        faces_background_rgb: tuple[tuple[int, int, int]],
        font_foreground_ansi: str = DEFAULT_FONT_FOREGROUND_ANSI,
        hidden_background_ansi: str = DEFAULT_HIDDEN_BACKGROUND_ANSI,
        masked_ansi: str = DEFAULT_MASKED_ANSI,
        extra: dict | None = None,
) -> dict[str, str]:
    palette = {
        'reset': '\x1b[0;0m',
        'masked': masked_ansi,
    }

    for face, color in zip(FACE_ORDER, faces_background_rgb, strict=True):
        ansi_face = rgb_to_ansi('48', *color) + font_foreground_ansi
        ansi_face_hidden = hidden_background_ansi + rgb_to_ansi('38', *color)

        palette[face] = ansi_face
        palette[f'{ face }_hidden'] = ansi_face_hidden

    if extra:
        palette.update(extra)

    return palette


def load_palette(palette_name: str) -> dict[str, str]:
    if palette_name not in PALETTES:
        palette_name = os.getenv('CUBING_ALGS_PALETTE', 'default')

    if palette_name in LOADED_PALETTES:
        return LOADED_PALETTES[palette_name]

    palette = build_ansi_palette(
        **PALETTES[palette_name],
    )

    LOADED_PALETTES[palette_name] = palette

    return palette
