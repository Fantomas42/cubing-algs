import math


def gradient(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    grad_position = facelet_index / 9  # 8 ?

    # Add shine gradient based on position (0.0 to 1.0)
    shine_factor = math.sin(grad_position * math.pi) * kw['intensity']

    # Brighten the color
    r = min(255, max(0, int(r + (255 - r) * shine_factor)))
    g = min(255, max(0, int(g + (255 - g) * shine_factor)))
    b = min(255, max(0, int(b + (255 - b) * shine_factor)))

    return r, g, b


def chrome(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3
    position_factor = (row + col) / 4.0  # 0.0 to 1.0 diagonal

    shine_intensity = math.sin(position_factor * math.pi) * kw['intensity']
    metallic = kw['metallic_factor']

    if shine_intensity > 0.5:  # noqa: PLR2004
        # Bright metallic highlight
        r = min(255, max(0, int(r * (1 - metallic) + 255 * metallic)))
        g = min(255, max(0, int(g * (1 - metallic) + 255 * metallic)))
        b = min(255, max(0, int(b * (1 - metallic) + 255 * metallic)))
    else:
        # Subtle enhancement
        r = min(255, max(0, int(r + (200 - r) * shine_intensity)))
        g = min(255, max(0, int(g + (200 - g) * shine_intensity)))
        b = min(255, max(0, int(b + (200 - b) * shine_intensity)))

    return r, g, b


def gold(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3
    position_factor = (row + col) / 4.0  # 0.0 to 1.0 diagonal

    shine_intensity = math.sin(position_factor * math.pi) * kw['intensity']
    warmth = kw['warmth']

    r = min(255, max(0, int(r + (255 - r) * shine_intensity * warmth)))
    g = min(255, max(0, int(g + (200 - g) * shine_intensity)))
    b = min(255, max(0, int(b + (100 - b) * shine_intensity * 0.5)))

    return r, g, b


def diamond(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3

    sparkle_pos = [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0)]
    if (row, col) in sparkle_pos:
        # Bright sparkle points
        factor = 0.9
        r = min(255, max(0, int(r * 0.2 + 255 * factor)))
        g = min(255, max(0, int(g * 0.2 + 255 * factor)))
        b = min(255, max(0, int(b * 0.2 + 255 * factor)))
    else:
        # Subtle base shine
        shine_intensity = kw['intensity'] * 0.3
        r = min(255, max(0, int(r + (255 - r) * shine_intensity)))
        g = min(255, max(0, int(g + (255 - g) * shine_intensity)))
        b = min(255, max(0, int(b + (255 - b) * shine_intensity)))

    return r, g, b


def rainbow(rgb, facelet_index, cube_size, **_kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3
    position_factor = (row + col) / 4.0  # 0.0 to 1.0 diagonal

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


def soft(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3
    position_factor = (row + col) / 4.0  # 0.0 to 1.0 diagonal

    shine_intensity = math.sin(position_factor * math.pi) * kw['intensity']
    r = min(255, max(0, int(r + (255 - r) * shine_intensity)))
    g = min(255, max(0, int(g + (255 - g) * shine_intensity)))
    b = min(255, max(0, int(b + (255 - b) * shine_intensity)))

    return r, g, b


def neon(rgb, facelet_index, cube_size, **kw):
    r, g, b = rgb

    local_index = facelet_index % 9

    row = local_index // 3
    col = local_index % 3
    position_factor = (row + col) / 4.0  # 0.0 to 1.0 diagonal

    # Neon glow effect
    glow_intensity = math.sin(position_factor * math.pi) * kw['intensity']
    saturation = kw.get('saturation_boost', 1.0)

    # Boost saturation and brightness
    max_component = max(r, g, b)
    if max_component > 0:
        r = min(255, max(0, int(r * saturation + glow_intensity * 100)))
        g = min(255, max(0, int(g * saturation + glow_intensity * 100)))
        b = min(255, max(0, int(b * saturation + glow_intensity * 100)))

    return r, g, b


EFFECTS = {
    'gradient': {
        'function': gradient,
        'parameters': {
            'intensity': 0.6,
        },
    },
    'chrome': {
        'function': chrome,
        'parameters': {
            'intensity': 0.8,
            'metallic_factor': 0.7,
        },
    },
    'gold': {
        'function': gold,
        'parameters': {
            'intensity': 0.6,
            'warmth': 1.2,
        },
    },
    'diamond': {
        'function': diamond,
        'parameters': {
            'intensity': 0.9,
            'sparkle': True,
        },
    },
    'rainbow': {
        'function': rainbow,
        'parameters': {
            'intensity': 0.5,  # TODO: unused
            'prismatic': True,  # TODO: unused
        },
    },
    'soft': {
        'function': soft,
        'parameters': {
            'intensity': 0.3,
        },
    },
    'neon': {
        'function': neon,
        'parameters': {
            'intensity': 0.7,
            'saturation_boost': 1.5,
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
