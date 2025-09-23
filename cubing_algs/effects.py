import math
import re
from collections.abc import Callable
from typing import Any

FACE_POSITIONS = {
    0: [0, 1],
    1: [1, 2],
    2: [1, 1],
    3: [2, 1],
    4: [1, 0],
    5: [1, 3],
}

# Positioning


def global_light_position_factor(facelet_index: int, cube_size: int) -> float:
    """
    Calculate global lighting position factor
    based on facelet position across the entire cube.
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


def get_position_factor(facelet_index: int, cube_size: int, **kw: Any) -> float:
    """
    Calculate position factor for effect application
    based on mode and facelet location.
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


def shine(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
          **kw: Any) -> tuple[int, int, int]:
    """
    Apply shine effect with smooth brightness variation across the surface.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    shine_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )

    # Brighten the color
    r = min(255, max(0, int(r + (255 - r) * shine_factor)))
    g = min(255, max(0, int(g + (255 - g) * shine_factor)))
    b = min(255, max(0, int(b + (255 - b) * shine_factor)))

    return r, g, b


def neon(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
         **kw: Any) -> tuple[int, int, int]:
    """
    Apply neon glow effect with saturated colors and bright highlights.
    """
    r, g, b = rgb

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

    return r, g, b


def chrome(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply chrome effect with metallic highlights and reflective appearance.
    """
    r, g, b = rgb

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

    return r, g, b


def gold(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
         **kw: Any) -> tuple[int, int, int]:
    """
    Apply golden metallic effect with warm yellow highlights.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)

    shine_factor = (
        math.sin(position_factor * math.pi)
        * kw.get('intensity', 0.5)
    )

    warmth = kw.get('warmth', 0.5)

    r = min(255, max(0, int(r + (255 - r) * shine_factor * warmth)))
    g = min(255, max(0, int(g + (200 - g) * shine_factor)))
    b = min(255, max(0, int(b + (100 - b) * shine_factor * 0.5)))

    return r, g, b


def silver(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply silver metallic effect with cool highlights.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.7)

    shine_factor = math.sin(position_factor * math.pi) * intensity

    # Cool metallic highlights
    average = (r + g + b) / 3
    metallic_boost = (255 - average) * shine_factor * 0.8

    r = min(255, max(0, int(r + metallic_boost * 0.9)))
    g = min(255, max(0, int(g + metallic_boost)))
    b = min(255, max(0, int(b + metallic_boost * 1.1)))

    return r, g, b


def copper(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply copper metallic effect with warm red-orange tints.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.6)
    warmth = kw.get('warmth', 1.0)

    shine_factor = math.sin(position_factor * math.pi) * intensity

    # Copper coloring: red-orange with green tints
    r = min(255, max(0, int(r + (220 - r) * shine_factor * warmth)))
    g = min(255, max(0, int(g + (140 - g) * shine_factor * 0.8)))
    b = min(255, max(0, int(b + (80 - b) * shine_factor * 0.4)))

    return r, g, b


def diamond(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
            **kw: Any) -> tuple[int, int, int]:
    """
    Apply diamond effect with bright sparkle points at specific positions.
    """
    r, g, b = rgb

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

    return r, g, b


def rainbow(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
            **kw: Any) -> tuple[int, int, int]:
    """
    Apply rainbow prismatic effect with color shifting based on position.
    """
    r, g, b = rgb

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

    return r, g, b


def matte(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
          **kw: Any) -> tuple[int, int, int]:
    """
    Apply matte effect by reducing brightness for a flat,
    non-reflective appearance.
    """
    r, g, b = rgb

    reduction = kw.get('reduction', 0.3)

    # Reduce brightness variations for flat look
    r = min(255, max(0, int(r * (1 - reduction))))
    g = min(255, max(0, int(g * (1 - reduction))))
    b = min(255, max(0, int(b * (1 - reduction))))

    return r, g, b


def glossy(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply glossy effect with sharp highlights like polished plastic.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.8)

    # Sharp highlights like polished plastic
    highlight = (math.sin(position_factor * math.pi) ** 3) * intensity

    r = min(255, max(0, int(r + (255 - r) * highlight)))
    g = min(255, max(0, int(g + (255 - g) * highlight)))
    b = min(255, max(0, int(b + (255 - b) * highlight)))

    return r, g, b


def frosted(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
            **kw: Any) -> tuple[int, int, int]:
    """
    Apply frosted effect with soft, diffused lighting.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.4)

    # Soft, diffused lighting
    diffuse = math.cos(position_factor * math.pi / 2) * intensity

    r = min(255, max(0, int(r + (255 - r) * diffuse)))
    g = min(255, max(0, int(g + (255 - g) * diffuse)))
    b = min(255, max(0, int(b + (255 - b) * diffuse)))

    return r, g, b


def checkerboard(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
                 **kw: Any) -> tuple[int, int, int]:
    """
    Apply checkerboard pattern with alternating light and dark squares.
    """
    r, g, b = rgb

    local_index = facelet_index % (cube_size * cube_size)
    row = local_index // cube_size
    col = local_index % cube_size

    intensity = kw.get('intensity', 0.5)

    factor = 1 + intensity if (row + col) % 2 == 0 else 1 - intensity

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return r, g, b


def stripes(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
            **kw: Any) -> tuple[int, int, int]:
    """
    Apply stripe pattern in horizontal, vertical, or diagonal directions.
    """
    r, g, b = rgb

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

    return r, g, b


def spiral(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply spiral pattern radiating from the center of each face.
    """
    r, g, b = rgb

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

    return r, g, b


def plasma(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
           **kw: Any) -> tuple[int, int, int]:
    """
    Apply plasma effect with multiple interference wave patterns.
    """
    r, g, b = rgb

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

    return r, g, b


def holographic(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
                **kw: Any) -> tuple[int, int, int]:
    """
    Apply holographic effect with color shifting
    that simulates viewing angle changes.
    """
    r, g, b = rgb

    position_factor = get_position_factor(facelet_index, cube_size, **kw)
    intensity = kw.get('intensity', 0.6)

    # Simulate color shifting based on viewing angle
    shift_r = math.sin(position_factor * 4 * math.pi) * intensity
    shift_g = math.sin(position_factor * 4 * math.pi + 2.09) * intensity
    shift_b = math.sin(position_factor * 4 * math.pi + 4.18) * intensity

    r = min(255, max(0, int(r + shift_r * 100)))
    g = min(255, max(0, int(g + shift_g * 100)))
    b = min(255, max(0, int(b + shift_b * 100)))

    return r, g, b


def dim(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
        **kw: Any) -> tuple[int, int, int]:
    """
    Reduce brightness uniformly across all color channels.
    """
    # Merge with brighten
    r, g, b = rgb

    factor = kw.get('factor', 0.7)

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return r, g, b


def brighten(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
             **kw: Any) -> tuple[int, int, int]:
    """
    Increase brightness uniformly across all color channels.
    """
    r, g, b = rgb

    factor = kw.get('factor', 1.3)

    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))

    return r, g, b


def contrast(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
             **kw: Any) -> tuple[int, int, int]:
    """
    Enhance contrast by amplifying differences from middle gray.
    """
    r, g, b = rgb

    factor = kw.get('factor', 1.5)

    # Enhance differences from middle gray (128)
    r = min(255, max(0, int(128 + (r - 128) * factor)))
    g = min(255, max(0, int(128 + (g - 128) * factor)))
    b = min(255, max(0, int(128 + (b - 128) * factor)))

    return r, g, b


def face_visible(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
             **kw: Any) -> tuple[int, int, int]:
    """
    Adjust brightness based on face visibility
    with front faces brighter than back faces.
    """
    face_size = cube_size * cube_size

    face_index = facelet_index // face_size
    kw['factor'] = kw.get('darken', 0.7)

    if face_index < 3:
        kw['factor'] = kw.get('lighten', 1.5)

    return dim(rgb, facelet_index, cube_size, **kw)


def vintage(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
            **kw: Any) -> tuple[int, int, int]:
    """
    Apply vintage effect with desaturation and sepia tinting.
    """
    r, g, b = rgb

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

    return sepia_r, sepia_g, sepia_b


def noop(rgb: tuple[int, int, int], _facelet_index: int, _cube_size: int,
         **_kw: Any) -> tuple[int, int, int]:
    """
    No-operation effect that returns the input color unchanged.
    """
    return rgb

# Configuration


EFFECTS = {
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
            'factor': 1.3,
        },
    },
    'noop': {
        'function': noop,
    },
}


def parse_effect_parameters(param_string: str) -> dict[
        str, float | int | str | bool]:
    """
    Parse parameter string in format "param1=value1,param2=value2".
    Supports int, float, and string values.
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
    Format: "effect_name(param1=value1,param2=value2)"
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
) -> Callable[[tuple[int, int, int], int, int], tuple[int, int, int]] | None:
    """
    Load and configure a single effect function with its parameters.
    """
    if not effect_name or effect_name not in EFFECTS:
        return None

    effect_config: dict[str, Any] = EFFECTS[effect_name]  # type: ignore[assignment]
    effect_function: Callable[..., tuple[int, int, int]] = effect_config[
        'function'
    ]
    effect_parameters = effect_config.get('parameters', {}).copy()

    if palette_name in effect_config:
        effect_parameters.update(effect_config[palette_name])

    effect_parameters.update(custom_params)

    def effect(rgb: tuple[int, int, int], facelet_index: int,
               cube_size: int) -> tuple[int, int, int]:
        """
        Apply the configured effect function with pre-loaded parameters.
        """
        return effect_function(
            rgb, facelet_index, cube_size,
            **effect_parameters,
        )

    return effect


def load_effect(effect_name: str, palette_name: str) -> Callable[
        [tuple[int, int, int], int, int], tuple[int, int, int]] | None:
    """
    Load and configure effect function(s) with parameters.
    Supports chaining multiple effects using pipe separator.

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

    def chained_effect(rgb: tuple[int, int, int], facelet_index: int,
                       cube_size: int) -> tuple[int, int, int]:
        """
        Apply multiple effects in sequence to create combined visuals.
        """
        result = rgb
        for effect_func in effects:
            result = effect_func(result, facelet_index, cube_size)
        return result

    return chained_effect
