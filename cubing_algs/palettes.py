from cubing_algs.constants import FACE_ORDER

LOADED_PALETTES: dict[str, dict[str, str]] = {}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hexadecimal color string to RGB tuple."""
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
    """Convert hexadecimal color value to ANSI escape code."""
    r, g, b = hex_to_rgb(hex_color)
    return f'\x1b[{ domain };2;{ r };{ g };{ b }m'


def background_hex_to_ansi(hex_color: str) -> str:
    """Convert hexadecimal color value to ANSI background color code."""
    return hex_to_ansi('48', hex_color)


def foreground_hex_to_ansi(hex_color: str) -> str:
    """Convert hexadecimal color value to ANSI foreground color code."""
    return hex_to_ansi('38', hex_color)


def build_ansi_color(background_hex: str, foreground_hex: str) -> str:
    """Build a complete ANSI color scheme"""
    return (
        background_hex_to_ansi(background_hex)
        + foreground_hex_to_ansi(foreground_hex)
    )


PALETTES: dict[str, dict[str, str | tuple[str | dict[str, str], ...]]] = {
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
        'hidden_ansi': build_ansi_color('#282A36', '#F8F8F2')
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
    # Dark
    # 'vampire': {
    #     'faces_background_rgb': (
    #         (20, 20, 20),
    #         (40, 40, 40),
    #         (32, 32, 32),
    #         (48, 48, 48),
    #         (24, 24, 24),
    #         (36, 36, 36),
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         219, 0, 0,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         80, 80, 110,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (0, 0, 0),
    #         (139, 0, 0),
    #     ),
    # },
    # 'halloween': {
    #     'faces_background_rgb': (
    #         (248, 248, 255),  # U
    #         (255, 69, 0),     # R
    #         (50, 205, 50),    # F
    #         (255, 215, 0),    # D
    #         (255, 140, 0),    # L
    #         {   # B - with custom font and hidden colors
    #             'background_rgb': (72, 61, 139),
    #             'font_ansi': foreground_rgb_to_ansi(220, 220, 220),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(132, 121, 199),
    #         },
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         25, 25, 25,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         40, 40, 40,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (25, 25, 25),
    #         (255, 165, 0),
    #     ),
    # },
    # 'cyberpunk': {
    #     'faces_background_rgb': (
    #         {   # U - with custom hidden colors
    #             'background_rgb': (15, 15, 15),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 255, 255),
    #         },
    #         (255, 16, 240),   # R
    #         {   # F - with custom font (magenta on green)
    #             'background_rgb': (0, 255, 150),
    #             'font_ansi': foreground_rgb_to_ansi(255, 16, 240),
    #         },
    #         {   # D - with custom font (magenta on yellow)
    #             'background_rgb': (255, 234, 0),
    #             'font_ansi': foreground_rgb_to_ansi(255, 16, 240),
    #         },
    #         (255, 69, 0),     # L
    #         (0, 191, 255),    # B
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         0, 255, 255,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         45, 45, 45,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (113, 28, 145),
    #         (0, 255, 255),
    #     ),
    # },
    # 'synthwave': {
    #     'faces_background_rgb': (
    #         {   # U - with custom hidden colors
    #             'background_rgb': (20, 20, 40),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(255, 255, 255),
    #         },
    #         (255, 20, 147),   # R
    #         (255, 105, 180),  # F
    #         (255, 215, 0),    # D
    #         (255, 69, 0),     # L
    #         (138, 43, 226),   # B
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         255, 255, 255,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         60, 60, 100,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (40, 40, 80),
    #         (255, 20, 147),
    #     ),
    # },
    # 'galaxy': {
    #     'faces_background_rgb': (
    #         {   # U - with custom hidden font
    #             'background_rgb': (25, 25, 112),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(65, 65, 255),
    #         },
    #         (255, 20, 147),   # R
    #         (138, 43, 226),   # F
    #         {   # D - with custom font (dark on yellow)
    #             'background_rgb': (255, 215, 0),
    #             'font_ansi': foreground_rgb_to_ansi(75, 75, 75),
    #         },
    #         (255, 105, 180),  # L
    #         {   # B - with custom hidden font
    #             'background_rgb': (72, 61, 139),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(112, 111, 209),
    #         },
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         255, 255, 255,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         40, 40, 70,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (20, 20, 40),
    #         (255, 225, 170),
    #     ),
    # },
    # 'matrix': {
    #     'faces_background_rgb': (
    #         {
    #             'background_rgb': (20, 20, 20),
    #             'font_ansi': foreground_rgb_to_ansi(0, 255, 0),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #         {
    #             'background_rgb': (20, 20, 20),
    #             'font_ansi': foreground_rgb_to_ansi(100, 255, 100),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #         {
    #             'background_rgb': (20, 20, 20),
    #             'font_ansi': foreground_rgb_to_ansi(200, 255, 200),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #         {
    #             'background_rgb': (100, 255, 100),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #         {
    #             'background_rgb': (150, 255, 150),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #         {
    #             'background_rgb': (200, 255, 200),
    #             'hidden_font_ansi': foreground_rgb_to_ansi(0, 150, 0),
    #         },
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         0, 0, 0,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         20, 20, 20,
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         0, 50, 0,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (0, 20, 0),
    #         (0, 255, 0),
    #     ),
    # },
    # 'sunset': {
    #     'faces_background_rgb': (
    #         (255, 255, 255),
    #         (255, 94, 77),
    #         (186, 203, 77),
    #         (255, 206, 84),
    #         (255, 118, 117),
    #         (108, 99, 255),
    #     ),
    # },
    # 'ocean': {
    #     'faces_background_rgb': (
    #         (240, 248, 255),
    #         (255, 99, 132),
    #         (75, 192, 192),
    #         (255, 205, 86),
    #         (114, 162, 235),
    #         (30, 144, 255),
    #     ),
    # },
    # 'forest': {
    #     'faces_background_rgb': (
    #         (245, 245, 220),
    #         (220, 20, 60),
    #         (34, 139, 34),
    #         (255, 215, 0),
    #         {
    #             'background_rgb': (139, 69, 19),
    #             'font_ansi': foreground_rgb_to_ansi(200, 200, 200),
    #             'hidden_font_ansi': rgb_to_ansi('38', 179, 109, 69),
    #             'adjacent_font_ansi': rgb_to_ansi('38', 179, 109, 69),
    #         },
    #         {
    #             'background_rgb': (25, 25, 112),
    #             'font_ansi': foreground_rgb_to_ansi(200, 200, 200),
    #             'hidden_font_ansi': rgb_to_ansi('38', 155, 155, 255),
    #             'adjacent_font_ansi': rgb_to_ansi('38', 105, 105, 255),
    #         },
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         0, 50, 0,
    #     ),
    # },
    # 'fire': {
    #     'faces_background_rgb': (
    #         (255, 250, 240),
    #         (220, 20, 60),
    #         (255, 69, 0),
    #         (255, 215, 0),
    #         (255, 140, 0),
    #         (139, 0, 0),
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         50, 0, 0,
    #     ),
    # },
    # 'ice': {
    #     'faces_background_rgb': (
    #         (240, 248, 255),
    #         (176, 196, 222),
    #         (173, 216, 230),
    #         (224, 255, 255),
    #         (175, 238, 238),
    #         (95, 158, 160),
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         45, 108, 200,
    #     ),
    # },
    # 'white': {
    #     'faces_background_rgb': (
    #         (255, 255, 255),
    #         (248, 248, 248),
    #         (240, 240, 240),
    #         (232, 232, 232),
    #         (224, 224, 224),
    #         (216, 216, 216),
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         0, 0, 0,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         162, 162, 162,
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         0, 0, 0,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (255, 255, 255),
    #         (64, 64, 64),
    #     ),
    # },
    # 'black': {
    #     'faces_background_rgb': (
    #         (0, 0, 0),
    #         (32, 32, 32),
    #         (48, 48, 48),
    #         (64, 64, 64),
    #         (80, 80, 80),
    #         (96, 96, 96),
    #     ),
    #     'font_foreground_ansi': foreground_rgb_to_ansi(
    #         255, 255, 255,
    #     ),
    #     'hidden_background_ansi': background_rgb_to_ansi(
    #         152, 152, 152,
    #     ),
    #     'adjacent_background_ansi': background_rgb_to_ansi(
    #         200, 200, 200,
    #     ),
    #     'masked_ansi': build_ansi_color(
    #         (0, 0, 0),
    #         (192, 192, 192),
    #     ),
    # },
}

DEFAULT_FONT = '#080808'

DEFAULT_MASKED_BACKGROUND = '#444444'

DEFAULT_ADJACENT_BACKGROUND = '#00004E'

DEFAULT_HIDDEN_ANSI = build_ansi_color('#303030', '#DADADA')


def build_ansi_palette(
        faces: tuple[str | dict[str, str]],
        font: str = DEFAULT_FONT,
        masked_background: str = DEFAULT_MASKED_BACKGROUND,
        adjacent_background: str = DEFAULT_ADJACENT_BACKGROUND,
        hidden_ansi: str = DEFAULT_HIDDEN_ANSI,
) -> dict[str, str]:
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
    if palette_name not in PALETTES:
        palette_name = 'default'

    if palette_name in LOADED_PALETTES:
        return LOADED_PALETTES[palette_name]

    palette = build_ansi_palette(
        **PALETTES[palette_name],
    )

    LOADED_PALETTES[palette_name] = palette

    return palette
