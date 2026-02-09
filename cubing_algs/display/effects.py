"""Visual effects and color transformations for cube display rendering."""
import math
import re
from collections.abc import Callable
from typing import TypedDict
from typing import Unpack

from cubing_algs.exceptions import EffectAlreadyExistsError

FACE_POSITIONS = {
    0: [0, 1],
    1: [1, 2],
    2: [1, 1],
    3: [2, 1],
    4: [1, 0],
    5: [1, 3],
}

type RGB = tuple[int, int, int]


class EffectParams(TypedDict, total=False):
    """Parameters for visual effects on cube facelets."""

    intensity: float
    facelet_mode: str
    position_mode: str
    saturation: float
    metallic: float
    warmth: float
    reduction: float
    direction: str
    frequency: int
    sepia: float
    desaturation: float
    factor: float
    lighten: float
    darken: float


class EffectConfig(TypedDict, total=False):
    """Configuration for a visual effect, including function and parameters."""

    function: Callable[
        [
            RGB,
            RGB,
            int, int,
        ],
        tuple[
            RGB,
            RGB,
        ],
    ]
    parameters: dict[str, float | int | str | bool]


# Positioning


def global_light_position_factor(facelet_index: int, cube_size: int) -> float:
    """
    Calculate global lighting position factor
    based on facelet position across the entire cube.

    Args:
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).

    Returns:
        Position factor value between 0.0 and 1.0 for lighting.

    """
    face_size = cube_size * cube_size

    face_index = facelet_index // face_size
    face_positions = FACE_POSITIONS[face_index]

    index = facelet_index % face_size

    col = index % cube_size
    row = index // cube_size

    pos = (
        face_positions[1] * cube_size + col
    ) + (
        face_positions[0] * cube_size + row
    )

    # 12 is a factor to offset radius
    return max(min(pos / 12, 1.0), 0)


def get_position_factor(facelet_index: int, cube_size: int,
                        **kw: Unpack[EffectParams]) -> float:
    """
    Calculate position factor for effect application
    based on mode and facelet location.

    Args:
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including facelet_mode and position_mode.

    Returns:
        Position factor value for effect calculations.

    """
    face_size = cube_size * cube_size

    facelet_mode = kw.get('facelet_mode', 'local')
    position_mode = kw.get('position_mode', 'numeral')

    if position_mode == 'numeral':
        if facelet_mode == 'local':
            position_factor = (facelet_index % face_size) / face_size
        else:
            position_factor = facelet_index / (face_size * 6)
    elif facelet_mode == 'local':  # Light local
        index = facelet_index % face_size

        col = index % cube_size
        row = index // cube_size

        position_factor = (col + row) / ((cube_size - 1) * 2)
    else:  # Light global
        position_factor = global_light_position_factor(
            facelet_index, cube_size,
        )

    return position_factor

# Effects


def shine(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply shine effect with smooth brightness variation
    across the surface.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with shine effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    shine_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )

    # Brighten the color
    r = min(255, max(0, int(r + (255 - r) * shine_factor)))
    g = min(255, max(0, int(g + (255 - g) * shine_factor)))
    b = min(255, max(0, int(b + (255 - b) * shine_factor)))

    return (r, g, b), foreground_rgb


def neon(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply neon glow effect with saturated colors and bright highlights.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity and saturation.

    Returns:
        Modified RGB color tuple with neon effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    glow_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )
    saturation = kw.get('saturation', 1.0)

    max_component = max(r, g, b)
    if max_component > 0:
        r = min(255, max(0, int(r * saturation + glow_factor * 100)))
        g = min(255, max(0, int(g * saturation + glow_factor * 100)))
        b = min(255, max(0, int(b * saturation + glow_factor * 100)))

    return (r, g, b), foreground_rgb


def chrome(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply chrome effect with metallic highlights
    and reflective appearance.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity and metallic.

    Returns:
        Modified RGB color tuple with chrome effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    shine_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )

    metallic = kw.get('metallic', 0.5)

    if shine_factor > 0.5:  # noqa: PLR2004
        # Bright metallic highlight
        r = min(255, max(0, int(r * (1 - metallic) + 255 * metallic)))
        g = min(255, max(0, int(g * (1 - metallic) + 255 * metallic)))
        b = min(255, max(0, int(b * (1 - metallic) + 255 * metallic)))
    else:
        # Subtle enhancement
        r = min(255, max(0, int(r + (200 - r) * shine_factor)))
        g = min(255, max(0, int(g + (200 - g) * shine_factor)))
        b = min(255, max(0, int(b + (200 - b) * shine_factor)))

    return (r, g, b), foreground_rgb


def gold(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply golden metallic effect with warm yellow highlights.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity and warmth.

    Returns:
        Modified RGB color tuple with gold effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    shine_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )

    warmth = kw.get('warmth', 0.5)

    r = min(255, max(0, int(r + (255 - r) * shine_factor * warmth)))
    g = min(255, max(0, int(g + (200 - g) * shine_factor)))
    b = min(255, max(0, int(b + (100 - b) * shine_factor * 0.5)))

    return (r, g, b), foreground_rgb


def silver(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply silver metallic effect with cool highlights.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with silver effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.7)

    shine_factor = math.sin(position_factor * math.pi) * intensity

    # Cool metallic highlights
    average = (r + g + b) / 3
    metallic_boost = (255 - average) * shine_factor * 0.8

    r = min(255, max(0, int(r + metallic_boost * 0.9)))
    g = min(255, max(0, int(g + metallic_boost)))
    b = min(255, max(0, int(b + metallic_boost * 1.1)))

    return (r, g, b), foreground_rgb


def copper(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply copper metallic effect with warm red-orange tints.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity and warmth.

    Returns:
        Modified RGB color tuple with copper effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.6)
    warmth = kw.get('warmth', 1.0)

    shine_factor = math.sin(position_factor * math.pi) * intensity

    # Copper coloring: red-orange with green tints
    r = min(255, max(0, int(r + (220 - r) * shine_factor * warmth)))
    g = min(255, max(0, int(g + (140 - g) * shine_factor * 0.8)))
    b = min(255, max(0, int(b + (80 - b) * shine_factor * 0.4)))

    return (r, g, b), foreground_rgb


def diamond(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply diamond effect with bright sparkle points at specific positions.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with diamond effect applied.

    """
    r, g, b = background_rgb

    local_index = facelet_index % (cube_size * cube_size)

    row = local_index // cube_size
    col = local_index % cube_size

    sparkle_pos = [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0)]
    if (row, col) in sparkle_pos:
        # Bright sparkle points
        factor = 0.9
        r = min(255, max(0, int(r * 0.2 + 255 * factor)))
        g = min(255, max(0, int(g * 0.2 + 255 * factor)))
        b = min(255, max(0, int(b * 0.2 + 255 * factor)))
    else:
        # Subtle base shine
        shine_factor = kw.get('intensity', 0.5) * 0.3
        r = min(255, max(0, int(r + (255 - r) * shine_factor)))
        g = min(255, max(0, int(g + (255 - g) * shine_factor)))
        b = min(255, max(0, int(b + (255 - b) * shine_factor)))

    return (r, g, b), foreground_rgb


def rainbow(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply rainbow prismatic effect with color shifting based on position.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters.

    Returns:
        Modified RGB color tuple with rainbow effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    # Rainbow prismatic effect
    base_intensity = sum([r, g, b]) / 3

    # Create rainbow colors based on position
    rainbow_r = int(
        base_intensity * (
            1 + 0.5 * math.sin(position_factor * 2 * math.pi)
        ),
    )
    rainbow_g = int(
        base_intensity * (
            1 + 0.5 * math.sin(position_factor * 2 * math.pi + 2.09)
        ),
    )
    rainbow_b = int(
        base_intensity * (
            1 + 0.5 * math.sin(position_factor * 2 * math.pi + 4.18)
        ),
    )

    r = min(255, max(r, rainbow_r))
    g = min(255, max(g, rainbow_g))
    b = min(255, max(b, rainbow_b))

    return (r, g, b), foreground_rgb


def matte(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply matte effect by reducing brightness for a flat,
    non-reflective appearance.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including reduction.

    Returns:
        Modified RGB color tuple with matte effect applied.

    """
    r, g, b = background_rgb

    reduction = kw.get('reduction', 0.3)

    # Reduce brightness variations for flat look
    r = min(255, max(0, int(r * (1 - reduction))))
    g = min(255, max(0, int(g * (1 - reduction))))
    b = min(255, max(0, int(b * (1 - reduction))))

    return (r, g, b), foreground_rgb


def glossy(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply glossy effect with sharp highlights like polished plastic.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with glossy effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.8)

    # Sharp highlights like polished plastic
    highlight = (math.sin(position_factor * math.pi) ** 3) * intensity

    r = min(255, max(0, int(r + (255 - r) * highlight)))
    g = min(255, max(0, int(g + (255 - g) * highlight)))
    b = min(255, max(0, int(b + (255 - b) * highlight)))

    return (r, g, b), foreground_rgb


def frosted(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply frosted effect with soft, diffused lighting.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with frosted effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.4)

    # Soft, diffused lighting
    diffuse = math.cos(position_factor * math.pi / 2) * intensity

    r = min(255, max(0, int(r + (255 - r) * diffuse)))
    g = min(255, max(0, int(g + (255 - g) * diffuse)))
    b = min(255, max(0, int(b + (255 - b) * diffuse)))

    return (r, g, b), foreground_rgb


def checkerboard(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply checkerboard pattern with alternating light and dark squares.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with checkerboard pattern applied.

    """
    r, g, b = background_rgb

    local_index = facelet_index % (cube_size * cube_size)
    row = local_index // cube_size
    col = local_index % cube_size

    intensity = kw.get('intensity', 0.5)

    factor = 1 + intensity if (row + col) % 2 == 0 else 1 - intensity

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return (r, g, b), foreground_rgb


def stripes(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply stripe pattern in horizontal, vertical, or diagonal directions.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including direction, frequency, and intensity.

    Returns:
        Modified RGB color tuple with stripe pattern applied.

    """
    r, g, b = background_rgb

    local_index = facelet_index % (cube_size * cube_size)
    direction = kw.get('direction', 'horizontal')
    frequency = kw.get('frequency', 2)
    intensity = kw.get('intensity', 0.4)

    if direction == 'horizontal':
        position = (local_index // cube_size) % frequency
    elif direction == 'vertical':
        position = (local_index % cube_size) % frequency
    else:  # Diagonal
        row = local_index // cube_size
        col = local_index % cube_size
        position = (row + col) % frequency

    factor = 1 + intensity if position < frequency / 2 else 1 - intensity

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return (r, g, b), foreground_rgb


def spiral(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply spiral pattern radiating from the center of each face.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with spiral pattern applied.

    """
    r, g, b = background_rgb

    local_index = facelet_index % (cube_size * cube_size)
    row = local_index // cube_size
    col = local_index % cube_size

    intensity = kw.get('intensity', 0.5)

    # Distance from center
    center = (cube_size - 1) / 2
    dx = col - center
    dy = row - center
    angle = math.atan2(dy, dx)
    distance = math.sqrt(dx * dx + dy * dy)

    # Spiral pattern
    spiral_factor = math.sin(angle * 2 + distance) * intensity

    r = min(255, max(0, int(r + (255 - r) * spiral_factor)))
    g = min(255, max(0, int(g + (255 - g) * spiral_factor)))
    b = min(255, max(0, int(b + (255 - b) * spiral_factor)))

    return (r, g, b), foreground_rgb


def plasma(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply plasma effect with multiple interference wave patterns.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with plasma effect applied.

    """
    r, g, b = background_rgb

    local_index = facelet_index % (cube_size * cube_size)
    row = local_index // cube_size
    col = local_index % cube_size

    intensity = kw.get('intensity', 0.4)

    # Multiple interference patterns
    plasma1 = math.sin(row * 0.5) * math.cos(col * 0.5)
    plasma2 = math.sin(math.sqrt(row * row + col * col) * 0.3)
    plasma3 = math.sin((row + col) * 0.4)

    plasma_factor = (plasma1 + plasma2 + plasma3) / 3 * intensity

    r = min(255, max(0, int(r + (255 - r) * plasma_factor)))
    g = min(255, max(0, int(g + (255 - g) * plasma_factor)))
    b = min(255, max(0, int(b + (255 - b) * plasma_factor)))

    return (r, g, b), foreground_rgb


def holographic(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply holographic effect with color shifting
    that simulates viewing angle changes.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including intensity.

    Returns:
        Modified RGB color tuple with holographic effect applied.

    """
    r, g, b = background_rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.6)

    # Simulate color shifting based on viewing angle
    shift_r = math.sin(position_factor * 4 * math.pi) * intensity
    shift_g = math.sin(position_factor * 4 * math.pi + 2.09) * intensity
    shift_b = math.sin(position_factor * 4 * math.pi + 4.18) * intensity

    r = min(255, max(0, int(r + shift_r * 100)))
    g = min(255, max(0, int(g + shift_g * 100)))
    b = min(255, max(0, int(b + shift_b * 100)))

    return (r, g, b), foreground_rgb


def dim(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Reduce brightness uniformly across all color channels.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including factor.

    Returns:
        Modified RGB color tuple with dimming applied.

    """
    # Merge with brighten
    r, g, b = background_rgb

    factor = kw.get('factor', 0.7)

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return (r, g, b), foreground_rgb


def brighten(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Increase brightness uniformly across all color channels.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including factor.

    Returns:
        Modified RGB color tuple with brightening applied.

    """
    r, g, b = background_rgb

    factor = kw.get('factor', 1.3)

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return (r, g, b), foreground_rgb


def contrast(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Enhance contrast by amplifying differences from middle gray.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including factor.

    Returns:
        Modified RGB color tuple with contrast adjustment applied.

    """
    r, g, b = background_rgb

    factor = kw.get('factor', 1.5)

    # Enhance differences from middle gray (128)
    r = min(255, max(0, int(128 + (r - 128) * factor)))
    g = min(255, max(0, int(128 + (g - 128) * factor)))
    b = min(255, max(0, int(128 + (b - 128) * factor)))

    return (r, g, b), foreground_rgb


def face_visible(
        background_rgb: RGB,
        foreground_rgb: RGB,
        facelet_index: int, cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Adjust brightness based on face visibility
    with front faces brighter than back faces.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including lighten and darken.

    Returns:
        Modified RGB color tuple with visibility-based brightness adjustment.

    """
    face_size = cube_size * cube_size

    face_index = facelet_index // face_size
    kw['factor'] = kw.get('darken', 0.7)

    if face_index < 3:
        kw['factor'] = kw.get('lighten', 1.0)

    return dim(background_rgb, foreground_rgb, facelet_index, cube_size, **kw)


def vintage(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    Apply vintage effect with desaturation and sepia tinting.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **kw: Effect parameters including sepia and desaturation.

    Returns:
        Modified RGB color tuple with vintage effect applied.

    """
    r, g, b = background_rgb

    sepia_strength = kw.get('sepia', 0.5)
    desaturation = kw.get('desaturation', 0.3)

    # Desaturate
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    r = int(r * (1 - desaturation) + gray * desaturation)
    g = int(g * (1 - desaturation) + gray * desaturation)
    b = int(b * (1 - desaturation) + gray * desaturation)

    # Apply sepia tint
    sepia_r = min(255, int(r + sepia_strength * 40))
    sepia_g = min(255, int(g + sepia_strength * 20))
    sepia_b = max(0, int(b - sepia_strength * 30))

    return (sepia_r, sepia_g, sepia_b), foreground_rgb


def noop(
        background_rgb: RGB,
        foreground_rgb: RGB,
        _facelet_index: int, _cube_size: int,
        **_kw: Unpack[EffectParams],
) -> tuple[RGB, RGB]:
    """
    No-operation effect that returns the input color unchanged.

    Args:
        background_rgb: Background RGB color tuple.
        foreground_rgb: Foreground RGB color tuple.
        facelet_index: Index of the facelet in the cube's state.
        cube_size: Size of the cube (3 for 3x3x3).
        **_kw: Unused effect parameters.

    Returns:
        Unmodified RGB color tuple.

    """
    return background_rgb, foreground_rgb

# Configuration


EFFECTS: dict[str, EffectConfig] = {
    'shine': {
        'function': shine,
        'parameters': {
            'intensity': 0.6,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'soft': {
        'function': shine,
        'parameters': {
            'intensity': 0.3,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'gradient': {
        'function': shine,
        'parameters': {
            'intensity': 0.6,
            'facelet_mode': 'local',
            'position_mode': 'numeral',
        },
    },
    'neon': {
        'function': neon,
        'parameters': {
            'intensity': 0.7,
            'saturation': 1.2,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'chrome': {
        'function': chrome,
        'parameters': {
            'intensity': 0.8,
            'metallic': 0.7,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'gold': {
        'function': gold,
        'parameters': {
            'intensity': 0.6,
            'warmth': 1.2,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'silver': {
        'function': silver,
        'parameters': {
            'intensity': 0.7,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'copper': {
        'function': copper,
        'parameters': {
            'intensity': 0.6,
            'warmth': 1.0,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'diamond': {
        'function': diamond,
        'parameters': {
            'intensity': 0.9,
        },
    },
    'rainbow': {
        'function': rainbow,
        'parameters': {
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'matte': {
        'function': matte,
        'parameters': {
            'reduction': 0.3,
        },
    },
    'glossy': {
        'function': glossy,
        'parameters': {
            'intensity': 0.8,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'frosted': {
        'function': frosted,
        'parameters': {
            'intensity': 0.4,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'checkerboard': {
        'function': checkerboard,
        'parameters': {
            'intensity': 0.5,
        },
    },
    'h-stripes': {
        'function': stripes,
        'parameters': {
            'direction': 'horizontal',
            'frequency': 2,
            'intensity': 0.4,
        },
    },
    'v-stripes': {
        'function': stripes,
        'parameters': {
            'direction': 'vertical',
            'frequency': 2,
            'intensity': 0.4,
        },
    },
    'd-stripes': {
        'function': stripes,
        'parameters': {
            'direction': 'diagonal',
            'frequency': 2,
            'intensity': 0.4,
        },
    },
    'spiral': {
        'function': spiral,
        'parameters': {
            'intensity': 0.5,
        },
    },
    'plasma': {
        'function': plasma,
        'parameters': {
            'intensity': 0.4,
        },
    },
    'holographic': {
        'function': holographic,
        'parameters': {
            'intensity': 0.6,
            'facelet_mode': 'local',
            'position_mode': 'light',
        },
    },
    'dim': {
        'function': dim,
        'parameters': {
            'factor': 0.7,
        },
    },
    'brighten': {
        'function': brighten,
        'parameters': {
            'factor': 1.3,
        },
    },
    'contrast': {
        'function': contrast,
        'parameters': {
            'factor': 1.5,
        },
    },
    'vintage': {
        'function': vintage,
        'parameters': {
            'sepia': 0.5,
            'desaturation': 0.3,
        },
    },
    'face-visible': {
        'function': face_visible,
        'parameters': {
            'lighten': 1.0,
            'darken': 0.7,
        },
    },
    'noop': {
        'function': noop,
    },
}


def register_effect(name: str, config: EffectConfig) -> None:
    """
    Register a custom visual effect.

    Args:
        name: Unique name for the effect.
        config: Effect configuration with function and optional parameters.

    Raises:
        EffectAlreadyExistsError: If the effect's name already exists.

    """
    if name in EFFECTS:
        msg = f'Effect already exists: {name}'
        raise EffectAlreadyExistsError(msg)

    EFFECTS[name] = config


def parse_effect_parameters(param_string: str) -> dict[
        str, float | int | str | bool]:
    """
    Parse parameter string in format "param1=value1,param2=value2".
    Supports int, float, and string values.

    Args:
        param_string: String containing comma-separated parameter assignments.

    Returns:
        Dictionary mapping parameter names to typed values.

    """
    parameters: dict[str, float | int | str | bool] = {}
    if not param_string:
        return parameters

    for param_part in param_string.split(','):
        param = param_part.strip()
        if '=' not in param:
            continue

        key, value = param.split('=', 1)
        key = key.strip()
        value = value.strip()

        # Try to convert to appropriate type
        if value.lower() in {'true', 'false'}:
            parameters[key] = value.lower() == 'true'
        elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
            if '.' in value:
                parameters[key] = float(value)
            else:
                parameters[key] = int(value)
        else:
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            parameters[key] = value

    return parameters


def parse_effect_name(effect_name: str) -> tuple[str, dict[
        str, float | int | str | bool]]:
    """
    Parse effect name with optional parameters.
    Format: "effect_name(param1=value1,param2=value2)".

    Args:
        effect_name: Effect name string with optional parameter specification.

    Returns:
        Tuple of (effect_name, parameters_dict).

    """
    # Match pattern: effect_name(parameters)
    match = re.match(r'^([^(]+)(?:\(([^)]*)\))?$', effect_name.strip())
    if not match:
        return effect_name.strip(), {}

    name = match.group(1).strip()
    param_string = match.group(2) or ''

    return name, parse_effect_parameters(param_string)


def load_single_effect(
        effect_name: str,
        custom_params: dict[str, float | int | str | bool],
        palette_name: str,
) -> Callable[
    [RGB, RGB, int, int],
    tuple[RGB, RGB],
] | None:
    """
    Load and configure a single effect function with its parameters.

    Args:
        effect_name: Name of the effect to load.
        custom_params: Custom parameter overrides for the effect.
        palette_name: Name of the palette being used.

    Returns:
        Configured effect function or None if effect not found.

    """
    if not effect_name or effect_name not in EFFECTS:
        return None

    effect_config: EffectConfig = EFFECTS[effect_name]
    effect_function: Callable[..., tuple[
        RGB,
        RGB]] = effect_config[
            'function'
        ]

    effect_parameters: dict[str, float | int | str | bool] = (
        effect_config.get('parameters', {}).copy()
    )

    # Check for palette-specific parameter overrides
    # (EffectConfig may have additional keys beyond the typed ones)
    if palette_name in effect_config:
        palette_override = effect_config.get(palette_name)
        if isinstance(palette_override, dict):
            effect_parameters.update(palette_override)

    effect_parameters.update(custom_params)

    def effect(background_rgb: RGB,
               foreground_rgb: RGB,
               facelet_index: int, cube_size: int) -> tuple[
                   RGB, RGB,
               ]:
        """
        Apply the configured effect function with pre-loaded parameters.

        Args:
            background_rgb: Background RGB color tuple.
            foreground_rgb: Foreground RGB color tuple.
            facelet_index: Index of the facelet in the cube's state.
            cube_size: Size of the cube (3 for 3x3x3).

        Returns:
            Modified RGB color tuple with effect applied.

        """
        return effect_function(
            background_rgb, foreground_rgb,
            facelet_index, cube_size,
            **effect_parameters,
        )

    return effect


def load_effect(effect_name: str, palette_name: str) -> Callable[
        [RGB, RGB, int, int],
        tuple[RGB, RGB]] | None:
    """
    Load and configure effect function(s) with parameters.
    Supports chaining multiple effects using pipe separator.

    Args:
        effect_name: Effect name or chain of effects separated by pipes.
        palette_name: Name of the palette being used.

    Returns:
        Configured effect function or None if no valid effects found.

    Examples:
        'shine' - Single effect
        'shine(intensity=0.8)' - Single effect with custom parameter
        'shine|dim' - Chained effects
        'shine(intensity=0.8)|dim(factor=0.6)' - Chained effects with parameters

    """
    if not effect_name:
        return None

    effect_parts = [part.strip() for part in effect_name.split('|')]

    effects = []
    for part in effect_parts:
        name, custom_params = parse_effect_name(part)
        effect_func = load_single_effect(name, custom_params, palette_name)
        if effect_func is not None:
            effects.append(effect_func)

    if not effects:
        return None

    if len(effects) == 1:
        return effects[0]

    def chained_effect(background_rgb: RGB,
                       foreground_rgb: RGB,
                       facelet_index: int, cube_size: int) -> tuple[
                           RGB, RGB,
                       ]:
        """
        Apply multiple effects in sequence to create combined visuals.

        Args:
            background_rgb: Background RGB color tuple.
            foreground_rgb: Foreground RGB color tuple.
            facelet_index: Index of the facelet in the cube's state.
            cube_size: Size of the cube (3 for 3x3x3).

        Returns:
            Modified RGB color tuple with all chained effects applied.

        """
        result_bg = background_rgb
        result_fg = foreground_rgb

        for effect_func in effects:
            result_bg, result_fg = effect_func(
                result_bg, result_fg,
                facelet_index, cube_size,
            )
        return result_bg, result_fg

    return chained_effect
