"""Letter style system for facelet piece types."""
from typing import TypedDict

from cubing_algs.annotations import FaceletPieceType
from cubing_algs.exceptions import StyleAlreadyExistsError

ANSI_STYLES: dict[str, str] = {
    'bold': '\x1b[1m',
    'dim': '\x1b[2m',
    'italic': '\x1b[3m',
    'underline': '\x1b[4m',
    'blink': '\x1b[5m',
    'hidden': '\x1b[8m',
    'strike': '\x1b[9m',
}


class StyleConfig(TypedDict, total=False):
    """Configuration for letter styles per facelet piece type."""

    corner: str
    edge: str
    center: str
    fixed_center: str
    midge: str
    wing: str


PIECE_TYPES: tuple[FaceletPieceType, ...] = (
    'corner', 'edge',
    'center', 'fixed_center',
    'midge', 'wing',
)

STYLES: dict[str, StyleConfig] = {
    'default': {
        'fixed_center': 'bold',
    },
    'detailed': {
        'corner': 'dim',
        'fixed_center': 'bold',
        'wing': 'dim',
    },
    'bold': {
        'corner': 'bold',
        'edge': 'bold',
        'center': 'bold',
        'fixed_center': 'bold',
        'midge': 'bold',
        'wing': 'bold',
    },
    'fixed_center': {
        'corner': 'hidden',
        'edge': 'hidden',
        'center': 'hidden',
        'midge': 'hidden',
        'wing': 'hidden',
    },
    'uniform': {},
}

LOADED_STYLES: dict[str, dict[FaceletPieceType, str]] = {}


def resolve_style_ansi(style_string: str) -> str:
    """
    Convert a style string to ANSI escape codes.

    Supports single styles ('bold') and combinations ('bold+italic').

    Args:
        style_string: Style descriptor like 'bold', 'dim', or 'bold+italic'.

    Returns:
        ANSI escape code string, empty string if no valid styles.

    """
    if not style_string:
        return ''

    parts = style_string.split('+')

    return ''.join(
        ANSI_STYLES[part.strip()]
        for part in parts
        if part.strip() in ANSI_STYLES
    )


def build_style(config: StyleConfig) -> dict[FaceletPieceType, str]:
    """
    Build resolved ANSI style mapping from a style configuration.

    Args:
        config: Style configuration mapping piece types to style strings.

    Returns:
        Dictionary mapping piece types to resolved ANSI escape codes.

    """
    return {
        piece_type: resolve_style_ansi(config.get(piece_type, ''))
        for piece_type in PIECE_TYPES
    }


def load_style(style_name: str) -> dict[FaceletPieceType, str]:
    """
    Load and cache a style by name.

    Falls back to 'default' style if the requested name is not found.

    Args:
        style_name: Name of the style to load.

    Returns:
        Dictionary mapping piece types to ANSI escape codes.

    """
    if style_name not in STYLES:
        style_name = 'default'

    if style_name in LOADED_STYLES:
        return LOADED_STYLES[style_name]

    style = build_style(STYLES[style_name])
    LOADED_STYLES[style_name] = style

    return style


def register_style(
        name: str,
        config: StyleConfig,
) -> None:
    """
    Register a custom letter style.

    Args:
        name: Unique name for the style.
        config: Style configuration mapping piece types to style strings.

    Raises:
        StyleAlreadyExistsError: If the style's name already exists.

    """
    if name in STYLES:
        msg = f'Style already exists: { name }'
        raise StyleAlreadyExistsError(msg)

    STYLES[name] = config


def get_piece_types(
        facelet_index: int, cube_size: int,
) -> list[FaceletPieceType]:
    """
    Determine the piece types for a facelet based on its position.

    Returns a list ordered from most specific to least specific,
    e.g. ['midge', 'edge'] or ['fixed_center', 'center'].

    Args:
        facelet_index: Global facelet index (0-based).
        cube_size: Size of the cube (e.g. 3 for 3x3).

    Returns:
        List of piece types from most specific to family.

    """
    face_size = cube_size * cube_size
    within_face = facelet_index % face_size
    row, col = divmod(within_face, cube_size)

    on_row_border = row == 0 or row == cube_size - 1
    on_col_border = col == 0 or col == cube_size - 1

    if on_row_border and on_col_border:
        return ['corner']

    if on_row_border or on_col_border:
        if cube_size > 3:
            if row == cube_size // 2 or col == cube_size // 2:
                return ['midge', 'edge']
            return ['wing', 'edge']
        return ['edge']

    if cube_size % 2 == 1 and row == cube_size // 2 and col == cube_size // 2:
        return ['fixed_center', 'center']

    return ['center']
