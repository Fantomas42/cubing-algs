import math

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


def get_position_factor(facelet_index: int, cube_size: int, **kw) -> float:
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
          **kw) -> tuple[int, int, int]:
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
         **kw) -> tuple[int, int, int]:
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
           **kw) -> tuple[int, int, int]:
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
         **kw) -> tuple[int, int, int]:
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


def diamond(rgb: tuple[int, int, int], facelet_index: int, cube_size: int,
            **kw) -> tuple[int, int, int]:
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
            **kw) -> tuple[int, int, int]:
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
}


def load_effect(effect_name: str, palette_name: str):
    if not effect_name or effect_name not in EFFECTS:
        return None

    effect_function = EFFECTS[effect_name]['function']
    effect_parameters = EFFECTS[effect_name]['parameters']

    if palette_name in EFFECTS[effect_name]:
        effect_parameters.update(EFFECTS[effect_name][palette_name])

    def effect(rgb, facelet_index, cube_size):
        return effect_function(
            rgb, facelet_index, cube_size,
            **effect_parameters,
        )

    return effect
