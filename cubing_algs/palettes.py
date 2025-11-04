"""Color palette management and conversion utilities for cube visualization."""

from typing import TypedDict

from cubing_algs.constants import FACE_ORDER

LOADED_PALETTES: dict[str, dict[str, str]] = {}


class PaletteConfig(TypedDict, total=False):
    """
    Configuration structure for cube face color palettes.

    Defines the complete color scheme for a cube display, including face colors,
    font settings, and various background states used in different contexts.
    """

    faces: tuple[str | dict[str, str], ...]
    font: str
    masked_background: str
    adjacent_background: str
    hidden_ansi: str


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hexadecimal color string to RGB tuple.

    Args:
        hex_color: Hexadecimal color string (e.g., '#FF0000' or 'F00').

    Returns:
        Tuple of (red, green, blue) values (0-255).

    Raises:
        ValueError: If hex color format is invalid.

    """
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)

    if len(hex_color) != 6:
        msg = f'Invalid hex color format: { hex_color }'
        raise ValueError(msg)

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError as e:
        msg = f'Invalid hex color format: { hex_color }'
        raise ValueError(msg) from e

    return (r, g, b)


def hex_to_ansi(domain: str, hex_color: str) -> str:
    """
    Convert hexadecimal color value to ANSI escape code.

    Args:
        domain: ANSI domain code ('38' for foreground, '48' for background).
        hex_color: Hexadecimal color string.

    Returns:
        ANSI escape sequence for the color.

    """
    r, g, b = hex_to_rgb(hex_color)
    return f'\x1b[{ domain };2;{ r };{ g };{ b }m'


def background_hex_to_ansi(hex_color: str) -> str:
    """
    Convert hexadecimal color value to ANSI background color code.

    Args:
        hex_color: Hexadecimal color string.

    Returns:
        ANSI background color escape sequence.

    """
    return hex_to_ansi('48', hex_color)


def foreground_hex_to_ansi(hex_color: str) -> str:
    """
    Convert hexadecimal color value to ANSI foreground color code.

    Args:
        hex_color: Hexadecimal color string.

    Returns:
        ANSI foreground color escape sequence.

    """
    return hex_to_ansi('38', hex_color)


def build_ansi_color(background_hex: str, foreground_hex: str) -> str:
    """
    Build a complete ANSI escape sequence with background and foreground.

    Args:
        background_hex: Hexadecimal background color.
        foreground_hex: Hexadecimal foreground color.

    Returns:
        Combined ANSI escape sequence for both colors.

    """
    return (
        background_hex_to_ansi(background_hex)
        + foreground_hex_to_ansi(foreground_hex)
    )


PALETTES: dict[str, PaletteConfig] = {
    'default': {
        'faces': (
            '#F5F5F5',
            '#FF0000',
            '#00D700',
            '#FFFF00',
            {
                'background': '#FF8700',
                'font_masked': '#FFAA00',
            },
            {
                'background': '#0000FF',
                'font': '#FFFFFF',
                'font_masked': '#007FFF',
                'font_adjacent': '#007FFF',
            },
        ),
    },
    'rgb': {
        'faces': (
            '#FFFFFF',
            '#FF0000',
            '#00FF00',
            '#FFFF00',
            '#FF7F00',
            '#0000FF',
        ),
        'font': '#000000',
        'masked_background': '#000000',
        'adjacent_background': '#7F7F7F',
        'hidden_ansi': build_ansi_color('#000', '#fff'),
    },
    'vibrant': {
        'faces': (
            '#FFFFFF',
            '#FF4136',
            '#2ED573',
            '#FFEAA7',
            '#FF9F43',
            '#74B9FF',
        ),
    },
    'neon': {
        'faces': (
            '#FFFFFF',
            '#FF1493',
            '#00FF7F',
            '#FFFF00',
            '#FF8C00',
            '#00BFFF',
        ),
    },
    'metal': {
        'faces': (
            '#DCDCDC',
            '#B4643C',
            '#788C50',
            '#C8A032',
            '#C87850',
            '#64A0C8',
        ),
        'adjacent_background': '#3F3F3F',
    },
    'pastel': {
        'faces': (
            '#FFFFFF',
            '#FFB6C1',
            '#98FB98',
            '#FFF192',
            '#FFDAB9',
            '#ADD8E6',
        ),
        'adjacent_background': '#666694',
    },
    'retro': {
        'faces': (
            '#FFF8DC',
            '#CC6666',
            '#90EE90',
            '#FFFF9A',
            '#FFA500',
            '#87CEFA',
        ),
        'adjacent_background': '#5555A4',
    },
    'minecraft': {
        'faces': (
            {
                'background': '#717171',
                'font_masked': '#C8C8C8',
            },
            '#E51A02',
            '#8FCA5C',
            {
                'background': '#FAE544',
                'font': '#3C3C3C',
            },
            {
                'background': '#854F2B',
                'font_masked': '#D59F7B',
            },
            '#81ACFF',
        ),
        'font': '#FFFFFF',
        'masked_background': '#575757',
        'adjacent_background': '#000016',
        'hidden_ansi': build_ansi_color('#363636', '#DDDDDD'),
    },
    'colorblind': {
        'faces': (
            '#FFFFFF',
            '#FF2120',
            '#21FF90',
            {
                'background': '#000',
                'font': '#FFF',
                'font_masked': '#C8C8C8',
            },
            '#FFA1FF',
            {
                'background': '#1A1BFF',
                'font': '#FFF',
            },
        ),
        'font': '#000',
        'masked_background': '#202020',
        'adjacent_background': '#4B0092',
        'hidden_ansi': build_ansi_color('#5D3A9B', '#FFFFFF'),
    },
    # Known palettes
    'dracula': {
        'faces': (
            '#F8F8F2',
            '#FF5555',
            '#50FA7B',
            '#F1FA8C',
            '#FFB86C',
            '#8BE9FD',
        ),
        'font': '#282A36',
        'masked_background': '#44475A',
        'adjacent_background': '#6272A4',
        'hidden_ansi': build_ansi_color('#282A36', '#F8F8F2'),
    },
    'alucard': {
        'faces': (
            {
                'background': '#FFFBEB',
                'font': '#1F1F1F',
            },
            '#CB3A2A',
            '#14710A',
            '#846E15',
            '#A34D14',
            '#036A96',
        ),
        'font': '#FFFBEB',
        'masked_background': '#1F1F1F',
        'adjacent_background': '#CFCFDE',
        'hidden_ansi': build_ansi_color('#6C664B', '#FFFBEB'),
    },
    'solarized-dark': {
        'faces': (
            {
                'background': '#073642',
                'font_masked': '#FDF6E3',
                'font_adjacent': '#FDF6E3',
            },
            '#DC322F',
            '#859900',
            '#B58900',
            '#CB4B16',
            '#268BD2',
        ),
        'font': '#FDF6E3',
        'masked_background': '#002B36',
        'adjacent_background': '#073642',
        'hidden_ansi': build_ansi_color('#002B36', '#839496'),
    },
    'solarized-light': {
        'faces': (
            {
                'background': '#EEE8D5',
                'font_masked': '#002B36',
                'font_adjacent': '#FDF6E3',
            },
            '#DC322F',
            '#859900',
            '#B58900',
            '#CB4B16',
            '#268BD2',
        ),
        'font': '#002B36',
        'masked_background': '#EEE8D5',
        'adjacent_background': '#FDF6E3',
        'hidden_ansi': build_ansi_color('#FDF6E3', '#657B83'),
    },
    # Env
    'halloween': {
        'faces': (
            '#F8F8FF',
            '#FF4500',
            '#32CD32',
            '#FFD700',
            '#FF8C00',
            {
                'background': '#483D8B',
                'font': '#DCDCDC',
                'font_masked': '#8479C7',
                'font_adjacent': '#8479C7',
            },
        ),
        'font': '#191919',
        'masked_background': '#282828',
        'hidden_ansi': build_ansi_color('#191919', '#FFA500'),
    },
    'galaxy': {
        'faces': (
            {
                'background': '#191970',
                'font_masked': '#4141FF',
                'font_adjacent': '#6666FF',
            },
            '#FF1493',
            '#8A2BE2',
            {
                'background': '#FFD700',
                'font': '#4B4B4B',
            },
            '#FF69B4',
            {
                'background': '#483D8B',
                'font_masked': '#706FD1',
                'font_adjacent': '#AAAAFF',
            },
        ),
        'font': '#FFFFFF',
        'masked_background': '#282846',
        'hidden_ansi': build_ansi_color('#141428', '#FFE1AA'),
    },
    # Dark / Goth
    'vampire': {
        'faces': (
            '#141414',
            '#181818',
            '#222222',
            '#262626',
            '#303030',
            '#343434',
        ),
        'font': '#DB0000',
        'masked_background': '#AE3030',
        'adjacent_background': '#AE6060',
        'hidden_ansi': build_ansi_color('#000000', '#AE0000'),
    },
    'ghoul': {
        'faces': (
            '#141414',
            '#181818',
            '#222222',
            '#262626',
            '#303030',
            '#343434',
        ),
        'font': '#26C4EC',
        'masked_background': '#297E97',
        'adjacent_background': '#8BD8F3',
        'hidden_ansi': build_ansi_color('#000000', '#26C4EC'),
    },
    'goblin': {
        'faces': (
            '#141414',
            '#181818',
            '#222222',
            '#262626',
            '#303030',
            '#343434',
        ),
        'font': '#00F253',
        'masked_background': '#5CA165',
        'adjacent_background': '#2AE464',
        'hidden_ansi': build_ansi_color('#000000', '#00F253'),
    },
    # Futuristic
    'cyberpunk': {
        'faces': (
            {
                'background': '#0F0F0F',
                'font_masked': '#00FFFF',
                'font_adjacent': '#00FFFF',
            },
            '#FF10F0',
            {
                'background': '#00FF96',
                'font': '#FF10F0',
            },
            {
                'background': '#FFEA00',
                'font': '#FF10F0',
            },
            '#FF4500',
            '#00BFFF',
        ),
        'font': '#00FFFF',
        'masked_background': '#2D2D2D',
        'hidden_ansi': build_ansi_color('#711C91', '#00FFFF'),
    },
    'synthwave': {
        'faces': (
            {
                'background': '#141428',
                'font_masked': '#FFFFFF',
            },
            '#FF1493',
            '#FF69B4',
            {
                'background': '#FFD700',
                'font': '#000',
            },
            '#FF4500',
            '#8A2BE2',
        ),
        'font': '#FFFFFF',
        'masked_background': '#3C3C64',
        'hidden_ansi': build_ansi_color('#282850', '#FF1493'),
    },
    'matrix': {
        'faces': (
            {
                'background': '#141414',
                'font': '#00FF00',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
            {
                'background': '#141414',
                'font': '#64FF64',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
            {
                'background': '#141414',
                'font': '#C8FFC8',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
            {
                'background': '#64FF64',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
            {
                'background': '#96FF96',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
            {
                'background': '#B8FFB8',
                'font_masked': '#009600',
                'font_adjacent': '#B8FFB8',
            },
        ),
        'font': '#000000',
        'masked_background': '#141414',
        'adjacent_background': '#003200',
        'hidden_ansi': build_ansi_color('#003400', '#00FF00'),
    },
    # Nature
    'sunset': {
        'faces': (
            '#FFFFFF',
            '#FF5E4D',
            '#BACB4D',
            '#FFCE54',
            '#FF7675',
            '#6C63FF',
        ),
    },
    'ocean': {
        'faces': (
            '#F0F8FF',
            '#FF6384',
            '#4BC0C0',
            '#FFCD56',
            '#72A2EB',
            '#1E90FF',
        ),
    },
    'forest': {
        'faces': (
            '#F5F5DC',
            '#DC143C',
            '#228B22',
            '#FFD700',
            {
                'background': '#8B4513',
                'font': '#C8C8C8',
                'font_masked': '#B36D45',
                'font_adjacent': '#B36D45',
            },
            {
                'background': '#191970',
                'font': '#C8C8C8',
                'font_masked': '#9B9BFF',
                'font_adjacent': '#6969FF',
            },
        ),
        'adjacent_background': '#003200',
    },
    'fire': {
        'faces': (
            '#FFFAF0',
            '#DC143C',
            '#FF4500',
            '#FFD700',
            '#FF8C00',
            '#8B0000',
        ),
        'adjacent_background': '#320000',
    },
    'ice': {
        'faces': (
            '#F0F8FF',
            '#B0C4DE',
            '#ADD8E6',
            '#E0FFFF',
            '#AFEEEE',
            '#5F9EA0',
        ),
        'adjacent_background': '#2D6CC8',
    },
    # Monochrome
    'white': {
        'faces': (
            '#FFFFFF',
            '#F8F8F8',
            '#F0F0F0',
            '#E8E8E8',
            '#E0E0E0',
            '#D8D8D8',
        ),
        'font': '#000000',
        'masked_background': '#A2A2A2',
        'adjacent_background': '#000000',
        'hidden_ansi': build_ansi_color('#FFFFFF', '#404040'),
    },
    'black': {
        'faces': (
            '#000000',
            '#202020',
            '#303030',
            '#404040',
            '#505050',
            '#606060',
        ),
        'font': '#FFFFFF',
        'masked_background': '#989898',
        'adjacent_background': '#C8C8C8',
        'hidden_ansi': build_ansi_color('#000000', '#C0C0C0'),
    },
    'red': {
        'faces': (
            '#200000',
            '#300000',
            '#400000',
            '#500000',
            '#600000',
            '#800000',
        ),
        'font': '#FFFFFF',
        'masked_background': '#AA7070',
        'adjacent_background': '#F8C8C8',
        'hidden_ansi': build_ansi_color('#000000', '#00BB00'),
    },
    'green': {
        'faces': (
            '#002000',
            '#003000',
            '#004000',
            '#005000',
            '#006000',
            '#008000',
        ),
        'font': '#FFFFFF',
        'masked_background': '#70AA70',
        'adjacent_background': '#C8F8C8',
        'hidden_ansi': build_ansi_color('#000000', '#00BB00'),
    },
    'blue': {
        'faces': (
            '#000020',
            '#000030',
            '#000040',
            '#000050',
            '#000060',
            '#000080',
        ),
        'font': '#FFFFFF',
        'masked_background': '#7070AA',
        'adjacent_background': '#C8C8F8',
        'hidden_ansi': build_ansi_color('#000000', '#0000BB'),
    },
}

DEFAULT_FONT = '#080808'

DEFAULT_MASKED_BACKGROUND = '#444444'

DEFAULT_ADJACENT_BACKGROUND = '#00004E'

DEFAULT_HIDDEN_ANSI = build_ansi_color('#303030', '#DADADA')


def build_ansi_palette(
        faces: tuple[str | dict[str, str], ...],
        font: str = DEFAULT_FONT,
        masked_background: str = DEFAULT_MASKED_BACKGROUND,
        adjacent_background: str = DEFAULT_ADJACENT_BACKGROUND,
        hidden_ansi: str = DEFAULT_HIDDEN_ANSI,
) -> dict[str, str]:
    """
    Build a complete ANSI color palette for cube face display.

    Creates ANSI escape sequences for each cube face in three states:
      normal, masked, and adjacent.

    Each face can be defined as a simple hex color string
    or a dictionary with custom background, font, and masked font colors.

    Args:
        faces: Tuple of 6 face colors (U/R/F/D/L/B order).
        font: Default font color hex string.
        masked_background: Background color for masked facelets.
        adjacent_background: Background color for adjacent faces.
        hidden_ansi: ANSI sequence for hidden facelets.

    Returns:
        Dictionary mapping color keys to ANSI escape sequences.

    """
    palette = {
        'reset': '\x1b[0;0m',
        'hidden': hidden_ansi,
    }

    for face, face_config in zip(FACE_ORDER, faces, strict=True):
        if isinstance(face_config, dict):
            background = face_config['background']
            font_ansi = foreground_hex_to_ansi(
                face_config.get(
                    'font',
                    font,
                ),
            )
            font_masked_ansi = foreground_hex_to_ansi(
                face_config.get(
                    'font_masked',
                    background,
                ),
            )
            font_adjacent_ansi = foreground_hex_to_ansi(
                face_config.get(
                    'font_adjacent',
                    background,
                ),
            )
        else:
            background = face_config
            font_ansi = foreground_hex_to_ansi(font)
            font_masked_ansi = foreground_hex_to_ansi(background)
            font_adjacent_ansi = foreground_hex_to_ansi(background)

        ansi_face = (
            background_hex_to_ansi(background)
            + font_ansi
        )
        ansi_face_masked = (
            background_hex_to_ansi(masked_background)
            + font_masked_ansi
        )
        ansi_face_adjacent = (
            background_hex_to_ansi(adjacent_background)
            + font_adjacent_ansi
        )

        palette[face] = ansi_face
        palette[f'{ face }_masked'] = ansi_face_masked
        palette[f'{ face }_adjacent'] = ansi_face_adjacent

    return palette


def load_palette(palette_name: str) -> dict[str, str]:
    """
    Load and cache an ANSI color palette by name.

    Returns a cached palette if already loaded, otherwise builds
    and caches the palette from the PALETTES dictionary.

    Falls back to 'default' palette if the requested palette name is not found.

    Args:
        palette_name: Name of the palette to load.

    Returns:
        Dictionary mapping color keys to ANSI escape sequences.

    """
    if palette_name not in PALETTES:
        palette_name = 'default'

    if palette_name in LOADED_PALETTES:
        return LOADED_PALETTES[palette_name]

    palette = build_ansi_palette(
        **PALETTES[palette_name],
    )

    LOADED_PALETTES[palette_name] = palette

    return palette
