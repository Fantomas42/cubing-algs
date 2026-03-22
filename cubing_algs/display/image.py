"""Cube image rendering in SVG and PNG formats."""
import math
import operator
import re

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.palettes import hex_to_rgb
from cubing_algs.display.vcube import DEFAULT_PALETTE
from cubing_algs.vcube import VCube

Point3D = tuple[float, float, float]
Point2D = tuple[float, float]
FaceData = tuple[str, list[Point2D], int]

ROTATION_PATTERN = re.compile(r'^([xyz]-?[0-9]+)+$')
ROTATION_PARTS = re.compile(r'([xyz])(-?[0-9]+)')

CUBE_COLOR = '#111111'

# Gap between stickers as a fraction of face size (divided by 3 per cell)
STICKER_GAP = 0.08
VISIBILITY_EPSILON = 1e-9
CAMERA_DISTANCE = 10.0

# Vertices of unit cube at (+/-1, +/-1, +/-1)
CUBE_VERTICES: list[Point3D] = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1),
]

# Face definitions: (name, normal, vertex_indices, face_state_index)
FACE_DEFS: list[tuple[str, Point3D, list[int], int]] = [
    ('U', (0, 1, 0), [3, 2, 6, 7], 0),
    ('D', (0, -1, 0), [4, 5, 1, 0], 3),
    ('R', (1, 0, 0), [6, 2, 1, 5], 1),
    ('L', (-1, 0, 0), [3, 7, 4, 0], 4),
    ('F', (0, 0, 1), [7, 6, 5, 4], 2),
    ('B', (0, 0, -1), [2, 3, 0, 1], 5),
]


def parse_rotation(rotation: str) -> list[tuple[str, int]]:
    """
    Parse a rotation string into axis-angle pairs.

    Args:
        rotation: Rotation string like "y45x-34".

    Returns:
        List of (axis, degrees) tuples.

    Raises:
        ValueError: If the rotation string is invalid.

    """
    if not ROTATION_PATTERN.match(rotation):
        msg = (
            f'Invalid rotation string: {rotation!r}. '
            'Expected format like "y45x-34".'
        )
        raise ValueError(msg)

    return [
        (m.group(1), int(m.group(2)))
        for m in ROTATION_PARTS.finditer(rotation)
    ]


def rotate_point(
    point: Point3D,
    rotations: list[tuple[str, int]],
) -> Point3D:
    """
    Apply sequential axis-angle rotations to a 3D point.

    Args:
        point: The (x, y, z) point to rotate.
        rotations: List of (axis, degrees) tuples.

    Returns:
        The rotated (x, y, z) point.

    """
    x, y, z = point

    for axis, degrees in rotations:
        rad = math.radians(-degrees)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        if axis == 'x':
            y, z = (
                cos_a * y - sin_a * z,
                sin_a * y + cos_a * z,
            )
        elif axis == 'y':
            x, z = (
                cos_a * x + sin_a * z,
                -sin_a * x + cos_a * z,
            )
        elif axis == 'z':
            x, y = (
                cos_a * x - sin_a * y,
                sin_a * x + cos_a * y,
            )

    return (x, y, z)


def project(point: Point3D, distance: float) -> Point2D:
    """
    Perspective projection onto the xy plane.

    The camera sits at z = distance, looking toward the origin.
    Points closer to the camera appear larger.

    Args:
        point: The (x, y, z) point to project.
        distance: Camera distance from origin along z-axis.

    Returns:
        The (x, y) projected point.

    """
    scale = distance / (distance - point[2])
    return (point[0] * scale, point[1] * scale)


def compute_visible_faces(
    rotations: list[tuple[str, int]],
    distance: float,
) -> list[FaceData]:
    """
    Compute which faces are visible and their projected corners.

    Args:
        rotations: List of (axis, degrees) rotation pairs.
        distance: Camera distance for perspective projection.

    Returns:
        List of (face_name, corner_2d_points, face_state_index)
        sorted back-to-front by average z-depth.

    """
    rotated = [
        rotate_point(v, rotations) for v in CUBE_VERTICES
    ]

    visible: list[tuple[str, list[Point2D], int, float]] = []

    for name, normal, indices, state_idx in FACE_DEFS:
        rn = rotate_point(normal, rotations)

        if rn[2] > VISIBILITY_EPSILON:
            corners_3d = [rotated[i] for i in indices]
            corners_2d = [project(c, distance) for c in corners_3d]
            avg_z = sum(c[2] for c in corners_3d) / 4
            visible.append(
                (name, corners_2d, state_idx, avg_z),
            )

    visible.sort(key=operator.itemgetter(3))

    return [
        (name, corners, idx)
        for name, corners, idx, _ in visible
    ]


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, float]:
    """
    Convert hex color to RGBA tuple.

    Accepts ``#rrggbb`` or ``#rrggbbaa`` format.

    Returns:
        Tuple of (red, green, blue, opacity) where RGB
        values are 0-255 and opacity is 0.0-1.0.

    """
    h = hex_color.lstrip('#')
    alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
    r, g, b = hex_to_rgb(hex_color[:7] if len(h) == 8 else hex_color)
    return r, g, b, alpha


def lerp_2d(
    p0: Point2D, p1: Point2D, t: float,
) -> Point2D:
    """
    Linear interpolation between two 2D points.

    Returns:
        Interpolated 2D point.

    """
    return (
        p0[0] + (p1[0] - p0[0]) * t,
        p0[1] + (p1[1] - p0[1]) * t,
    )


def points_to_svg(points: list[Point2D]) -> str:
    """
    Convert 2D points to an SVG points attribute string.

    Returns:
        Space-separated "x,y" coordinate pairs.

    """
    return ' '.join(
        f'{x:.2f},{y:.2f}' for x, y in points
    )


def build_sticker_polygon(
    svg_corners: list[Point2D],
    row: int,
    col: int,
    fill: str,
    cube_size: int,
) -> str:
    """
    Build an SVG polygon element for a single sticker.

    Returns:
        SVG polygon element string.

    """
    t0_col = col / cube_size
    t1_col = (col + 1) / cube_size
    t0_row = row / cube_size
    t1_row = (row + 1) / cube_size

    # Gap is per-cell: divide by n since the face is an nxn grid
    gap = STICKER_GAP / cube_size
    t0_col += gap
    t1_col -= gap
    t0_row += gap
    t1_row -= gap

    top_edge_0 = lerp_2d(
        svg_corners[0], svg_corners[1], t0_col,
    )
    top_edge_1 = lerp_2d(
        svg_corners[0], svg_corners[1], t1_col,
    )
    bot_edge_0 = lerp_2d(
        svg_corners[3], svg_corners[2], t0_col,
    )
    bot_edge_1 = lerp_2d(
        svg_corners[3], svg_corners[2], t1_col,
    )

    s_tl = lerp_2d(top_edge_0, bot_edge_0, t0_row)
    s_tr = lerp_2d(top_edge_1, bot_edge_1, t0_row)
    s_br = lerp_2d(top_edge_1, bot_edge_1, t1_row)
    s_bl = lerp_2d(top_edge_0, bot_edge_0, t1_row)

    pts = points_to_svg([s_tl, s_tr, s_br, s_bl])
    return (
        f'  <polygon'
        f' points="{pts}"'
        f' fill="{fill}"/>'
    )


def resolve_face_colors(palette_name: str) -> dict[str, str]:
    """
    Build a face-letter to hex-color mapping from a palette.

    Args:
        palette_name: Name of a palette defined in
            :mod:`cubing_algs.display.palettes`.

    Returns:
        Dictionary mapping face letters (U/R/F/D/L/B)
        to hex color strings.

    """
    from cubing_algs.display.palettes import PALETTES  # noqa: PLC0415

    config = PALETTES.get(palette_name, PALETTES['default'])
    faces = config['faces']

    return {
        face: (
            entry['background']
            if isinstance(entry, dict)
            else entry
        )
        for face, entry in zip(FACE_ORDER, faces, strict=True)
    }


def build_face_stickers(
    svg_corners: list[Point2D],
    facelets: str,
    cube_size: int,
    face_colors: dict[str, str],
) -> list[str]:
    """
    Build sticker polygon elements for one face.

    Returns:
        List of SVG polygon element strings.

    """
    stickers: list[str] = []

    for row in range(cube_size):
        for col in range(cube_size):
            idx = row * cube_size + col
            color_key = facelets[idx]
            base_color = face_colors.get(
                color_key, '#888888',
            )
            stickers.append(build_sticker_polygon(
                svg_corners, row, col, base_color,
                cube_size,
            ))

    return stickers


def build_svg(  # noqa: PLR0913, PLR0914, PLR0917
    state: str,
    size: int,
    rotations: list[tuple[str, int]],
    cube_size: int = 3,
    distance: float = CAMERA_DISTANCE,
    cube_color: str = CUBE_COLOR,
    palette_name: str = DEFAULT_PALETTE,
) -> str:
    """
    Build an SVG string for the cube state.

    Args:
        state: Facelet string (6 * cube_size² characters).
        size: Image dimension in pixels.
        rotations: List of (axis, degrees) rotation pairs.
        cube_size: Cube dimension (2 for 2x2, 3 for 3x3, etc.).
        distance: Camera distance for perspective projection.
        cube_color: Hex color for cube body between stickers.
            Supports alpha channel (``#rrggbbaa``).
        palette_name: Color palette name for sticker colors.

    Returns:
        Complete SVG document as a string.

    """
    face_colors = resolve_face_colors(palette_name)
    visible = compute_visible_faces(rotations, distance)

    margin = size * 0.002
    max_extent = math.sqrt(
        3 * distance ** 2 / (distance ** 2 - 3),
    )
    scale = (size - 2 * margin) / (2 * max_extent)
    cx, cy = size / 2, size / 2

    def to_svg_coords(p: Point2D) -> Point2D:
        return (cx + p[0] * scale, cy - p[1] * scale)

    face_groups: list[str] = []
    face_size = cube_size * cube_size

    cr, cg, cb, body_opacity = hex_to_rgba(cube_color)
    body_rgb = f'#{cr:02x}{cg:02x}{cb:02x}'
    opacity_attr = (
        f' fill-opacity="{body_opacity:.2f}"'
        if body_opacity < 1.0
        else ''
    )

    for face_name, corners_2d, face_state_idx in visible:
        svg_corners = [
            to_svg_coords(c) for c in corners_2d
        ]

        body_polygon = (
            '  <polygon'
            f' points="{points_to_svg(svg_corners)}"'
            f' fill="{body_rgb}"{opacity_attr} />'
        )

        face_start = face_state_idx * face_size
        facelets = state[face_start:face_start + face_size]

        face_stickers = build_face_stickers(
            svg_corners, facelets,
            cube_size, face_colors,
        )

        face_groups.append(
            f'<g class="face-{ face_name }">\n'
            + body_polygon + '\n'
            + '\n'.join(face_stickers)
            + '\n</g>',
        )

    return assemble_svg(size, face_groups)


def assemble_svg(
    size: int,
    face_groups: list[str],
) -> str:
    """
    Assemble final SVG document from parts.

    Returns:
        Complete SVG document string.

    """
    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="0 0 {size} {size}"'
            f' width="{size}" height="{size}">'
        ),
    ]

    lines.extend(face_groups)
    lines.append('</svg>')

    return '\n'.join(lines)


def get_state(
    source: VCube | Algorithm,
    cube_size: int | None,
) -> tuple[str, int]:
    """
    Extract facelet state and cube size from source.

    Args:
        source: VCube instance or Algorithm.
        cube_size: Explicit cube size, or None to infer.

    Returns:
        Tuple of (facelet state string, cube_size).

    Raises:
        TypeError: If source is not VCube or Algorithm.

    """
    if isinstance(source, VCube):
        n = cube_size if cube_size is not None else source.size
        return source.state, n

    if isinstance(source, Algorithm):
        n = cube_size if cube_size is not None else 3
        cube = VCube(size=n)
        if source:
            cube.rotate(source)
        return cube.state, n

    msg = (
        'source must be VCube or Algorithm, '
        f'got {type(source).__name__}'
    )
    raise TypeError(msg)


def render_cube(  # noqa: PLR0913
    source: VCube | Algorithm,
    *,
    size: int = 200,
    cube_size: int | None = None,
    rotation: str = 'y45x-34',
    distance: float = CAMERA_DISTANCE,
    cube_color: str = CUBE_COLOR,
    palette_name: str = DEFAULT_PALETTE,
) -> str:
    """
    Render a 3D perspective cube image.

    Args:
        source: VCube or Algorithm to render.
        size: Image dimension in pixels.
        rotation: Axis-angle rotation string.
        cube_size: Cube dimension (2 for 2x2, 3 for 3x3,
            etc.). Inferred from source if None.
        distance: Camera distance for perspective projection.
            Larger values produce a flatter image closer to
            orthographic; smaller values exaggerate depth.
        cube_color: Hex color for cube body between stickers.
            Supports alpha channel (``#rrggbbaa``), e.g.
            ``#11111180`` for semi-transparent black.
        palette_name: Color palette name for sticker colors.

    Returns:
        SVG string of the cube.

    Raises:
        ValueError: if size is not positive or distance is
            too small.

    """
    min_distance = math.sqrt(3)
    if distance <= min_distance:
        msg = (
            f'distance must be greater than sqrt(3) '
            f'(~{min_distance:.3f}), got {distance}'
        )
        raise ValueError(msg)

    if size < 1:
        msg = f'size must be positive, got {size}'
        raise ValueError(msg)

    rotations = parse_rotation(rotation)
    state, n = get_state(source, cube_size)

    return build_svg(
        state, size, rotations, n, distance,
        cube_color, palette_name,
    )
