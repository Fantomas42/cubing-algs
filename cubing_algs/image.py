"""Cube image rendering in SVG and PNG formats."""
from __future__ import annotations

import math
import operator
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm
    from cubing_algs.vcube import VCube

_ROTATION_PATTERN = re.compile(r'^([xyz]-?[0-9]+)+$')
_ROTATION_PARTS = re.compile(r'([xyz])(-?[0-9]+)')

_Point3D = tuple[float, float, float]
_Point2D = tuple[float, float]


def _parse_rotation(rotation: str) -> list[tuple[str, int]]:
    """
    Parse a rotation string into axis-angle pairs.

    Args:
        rotation: Rotation string like "y45x-25".

    Returns:
        List of (axis, degrees) tuples.

    Raises:
        ValueError: If the rotation string is invalid.

    """
    if not _ROTATION_PATTERN.match(rotation):
        msg = (
            f'Invalid rotation string: {rotation!r}. '
            f'Expected format like "y45x-25".'
        )
        raise ValueError(msg)

    return [
        (m.group(1), int(m.group(2)))
        for m in _ROTATION_PARTS.finditer(rotation)
    ]


def _rotate_point(
    point: _Point3D,
    rotations: list[tuple[str, int]],
) -> _Point3D:
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


def _project(point: _Point3D) -> _Point2D:
    """
    Orthographic projection: drop z coordinate.

    Args:
        point: The (x, y, z) point to project.

    Returns:
        The (x, y) projected point.

    """
    return (point[0], point[1])


# Vertices of unit cube at (+/-1, +/-1, +/-1)
_CUBE_VERTICES: list[_Point3D] = [
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
_FACE_DEFS: list[tuple[str, _Point3D, list[int], int]] = [
    ('U', (0, 1, 0), [3, 2, 6, 7], 0),
    ('D', (0, -1, 0), [4, 5, 1, 0], 3),
    ('R', (1, 0, 0), [6, 2, 1, 5], 1),
    ('L', (-1, 0, 0), [3, 7, 4, 0], 4),
    ('F', (0, 0, 1), [7, 6, 5, 4], 2),
    ('B', (0, 0, -1), [2, 3, 0, 1], 5),
]

_FaceData = tuple[str, list[_Point2D], int]


def _compute_visible_faces(
    rotations: list[tuple[str, int]],
) -> list[_FaceData]:
    """
    Compute which faces are visible and their projected corners.

    Args:
        rotations: List of (axis, degrees) rotation pairs.

    Returns:
        List of (face_name, corner_2d_points, face_state_index)
        sorted back-to-front by average z-depth.

    """
    rotated = [
        _rotate_point(v, rotations) for v in _CUBE_VERTICES
    ]

    visible: list[tuple[str, list[_Point2D], int, float]] = []

    for name, normal, indices, state_idx in _FACE_DEFS:
        rn = _rotate_point(normal, rotations)

        if rn[2] > _VISIBILITY_EPSILON:
            corners_3d = [rotated[i] for i in indices]
            corners_2d = [_project(c) for c in corners_3d]
            avg_z = sum(c[2] for c in corners_3d) / 4
            visible.append(
                (name, corners_2d, state_idx, avg_z),
            )

    visible.sort(key=operator.itemgetter(3))

    return [
        (name, corners, idx)
        for name, corners, idx, _ in visible
    ]


# Color mapping: facelet letter -> base hex color
_FACE_COLORS: dict[str, str] = {
    'U': '#ffffff',
    'R': '#ff0000',
    'F': '#00d800',
    'D': '#ffff00',
    'L': '#ff8c00',
    'B': '#0000ff',
}

# Gap between stickers as a fraction of face size (divided by 3 per cell)
_STICKER_GAP = 0.08
_VISIBILITY_EPSILON = 1e-9


def _hex_to_rgb(
    hex_color: str,
) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Returns:
        Tuple of (red, green, blue) values 0-255.

    """
    h = hex_color.lstrip('#')
    return (
        int(h[0:2], 16),
        int(h[2:4], 16),
        int(h[4:6], 16),
    )


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB tuple to hex color.

    Returns:
        Hex color string like "#ff0000".

    """
    return f'#{r:02x}{g:02x}{b:02x}'


def _tint_color(hex_color: str, factor: float) -> str:
    """
    Lighten a color by mixing with white.

    Returns:
        Lightened hex color string.

    """
    r, g, b = _hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return _rgb_to_hex(r, g, b)


def _shade_color(hex_color: str, factor: float) -> str:
    """
    Darken a color by reducing brightness.

    Returns:
        Darkened hex color string.

    """
    r, g, b = _hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return _rgb_to_hex(r, g, b)


def _lerp_2d(
    p0: _Point2D, p1: _Point2D, t: float,
) -> _Point2D:
    """
    Linear interpolation between two 2D points.

    Returns:
        Interpolated 2D point.

    """
    return (
        p0[0] + (p1[0] - p0[0]) * t,
        p0[1] + (p1[1] - p0[1]) * t,
    )


def _points_to_svg(points: list[_Point2D]) -> str:
    """
    Convert 2D points to an SVG points attribute string.

    Returns:
        Space-separated "x,y" coordinate pairs.

    """
    return ' '.join(
        f'{x:.2f},{y:.2f}' for x, y in points
    )


_GradientCoords = tuple[float, float, float, float]


def _build_sticker_gradient(
    grad_id: str,
    base_color: str,
    coords: _GradientCoords,
) -> str:
    """
    Build an SVG linearGradient element for a sticker.

    Returns:
        SVG linearGradient element string.

    """
    light_color = _tint_color(base_color, 0.15)
    dark_color = _shade_color(base_color, 0.20)
    gx1, gy1, gx2, gy2 = coords

    return (
        f'  <linearGradient id="{grad_id}"'
        f' x1="{gx1:.1f}"'
        f' y1="{gy1:.1f}"'
        f' x2="{gx2:.1f}"'
        f' y2="{gy2:.1f}"'
        f' gradientUnits="userSpaceOnUse">'
        f'<stop offset="0%"'
        f' stop-color="{light_color}"/>'
        f'<stop offset="100%"'
        f' stop-color="{dark_color}"/>'
        f'</linearGradient>'
    )


def _build_sticker_polygon(
    svg_corners: list[_Point2D],
    row: int,
    col: int,
    grad_id: str,
    cube_size: int,
) -> str:
    """
    Build an SVG polygon element for a single sticker.

    Returns:
        SVG polygon element string.

    """
    n = cube_size
    t0_col = col / n
    t1_col = (col + 1) / n
    t0_row = row / n
    t1_row = (row + 1) / n

    # Gap is per-cell: divide by n since the face is an nxn grid
    gap = _STICKER_GAP / 3
    t0_col += gap
    t1_col -= gap
    t0_row += gap
    t1_row -= gap

    top_edge_0 = _lerp_2d(
        svg_corners[0], svg_corners[1], t0_col,
    )
    top_edge_1 = _lerp_2d(
        svg_corners[0], svg_corners[1], t1_col,
    )
    bot_edge_0 = _lerp_2d(
        svg_corners[3], svg_corners[2], t0_col,
    )
    bot_edge_1 = _lerp_2d(
        svg_corners[3], svg_corners[2], t1_col,
    )

    s_tl = _lerp_2d(top_edge_0, bot_edge_0, t0_row)
    s_tr = _lerp_2d(top_edge_1, bot_edge_1, t0_row)
    s_br = _lerp_2d(top_edge_1, bot_edge_1, t1_row)
    s_bl = _lerp_2d(top_edge_0, bot_edge_0, t1_row)

    pts = _points_to_svg([s_tl, s_tr, s_br, s_bl])
    return (
        f'  <polygon'
        f' points="{pts}"'
        f' fill="url(#{grad_id})"/>'
    )


def _build_face_elements(
    face_name: str,
    svg_corners: list[_Point2D],
    facelets: str,
    size: int,
    cube_size: int,
) -> tuple[list[str], list[str]]:
    """
    Build gradient defs and sticker polygons for one face.

    Returns:
        Tuple of (gradient_defs, sticker_elements).

    """
    defs: list[str] = []
    stickers: list[str] = []

    top_mid = _lerp_2d(
        svg_corners[0], svg_corners[1], 0.5,
    )
    left_mid = _lerp_2d(
        svg_corners[0], svg_corners[3], 0.5,
    )

    gx1 = (left_mid[0] + top_mid[0]) / 2
    gy1 = (left_mid[1] + top_mid[1]) / 2
    gx2 = size - gx1
    gy2 = size - gy1
    coords: _GradientCoords = (gx1, gy1, gx2, gy2)

    for row in range(cube_size):
        for col in range(cube_size):
            idx = row * cube_size + col
            color_key = facelets[idx]
            base_color = _FACE_COLORS.get(
                color_key, '#888888',
            )
            grad_id = f'g-{face_name}-{row}-{col}'

            defs.append(_build_sticker_gradient(
                grad_id, base_color, coords,
            ))
            stickers.append(_build_sticker_polygon(
                svg_corners, row, col, grad_id,
                cube_size,
            ))

    return defs, stickers


def _build_svg(
    state: str,
    size: int,
    rotations: list[tuple[str, int]],
    cube_size: int = 3,
) -> str:
    """
    Build an SVG string for the cube state.

    Args:
        state: Facelet string (6 * cube_size² characters).
        size: Image dimension in pixels.
        rotations: List of (axis, degrees) rotation pairs.
        cube_size: Cube dimension (2 for 2x2, 3 for 3x3, etc.).

    Returns:
        Complete SVG document as a string.

    """
    visible = _compute_visible_faces(rotations)

    margin = size * 0.10
    max_extent = math.sqrt(3)
    scale = (size - 2 * margin) / (2 * max_extent)
    cx, cy = size / 2, size / 2

    def to_svg_coords(p: _Point2D) -> _Point2D:
        return (cx + p[0] * scale, cy - p[1] * scale)

    defs_parts: list[str] = []
    face_groups: list[str] = []
    face_size = cube_size * cube_size

    for face_name, corners_2d, face_state_idx in visible:
        svg_corners = [
            to_svg_coords(c) for c in corners_2d
        ]

        body_polygon = (
            f'  <polygon'
            f' points="{_points_to_svg(svg_corners)}"'
            f' fill="#111111" stroke="#111111"'
            f' stroke-width="0.5"/>'
        )

        face_start = face_state_idx * face_size
        facelets = state[face_start:face_start + face_size]

        face_defs, face_stickers = _build_face_elements(
            face_name, svg_corners, facelets, size,
            cube_size,
        )
        defs_parts.extend(face_defs)

        face_groups.append(
            f'<g class="face-{face_name}">\n'
            + body_polygon + '\n'
            + '\n'.join(face_stickers)
            + '\n</g>',
        )

    return _assemble_svg(
        size, defs_parts, face_groups,
    )


def _assemble_svg(
    size: int,
    defs_parts: list[str],
    face_groups: list[str],
) -> str:
    """
    Assemble final SVG document from parts.

    Returns:
        Complete SVG document string.

    """
    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="0 0 {size} {size}"'
            f' width="{size}" height="{size}">'
        ),
    ]

    if defs_parts:
        lines.append('<defs>')
        lines.extend(defs_parts)
        lines.append('</defs>')

    lines.extend(face_groups)
    lines.append('</svg>')

    return '\n'.join(lines)


def _get_state(
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
    from cubing_algs.algorithm import Algorithm as Algo  # noqa: PLC0415
    from cubing_algs.vcube import VCube as Cube  # noqa: PLC0415

    if isinstance(source, Cube):
        n = cube_size if cube_size is not None else source.size
        return source.state, n

    if isinstance(source, Algo):
        n = cube_size if cube_size is not None else 3
        cube = Cube(size=n)
        if source:
            cube.rotate(source)
        return cube.state, n

    msg = (
        f'source must be VCube or Algorithm, '
        f'got {type(source).__name__}'
    )
    raise TypeError(msg)


def render_cube(
    source: VCube | Algorithm,
    *,
    size: int = 200,
    rotation: str = 'y45x-25',
    path: str | Path | None = None,
    cube_size: int | None = None,
) -> str | None:
    """
    Render a 3D isometric cube image.

    Args:
        source: VCube or Algorithm to render.
        size: Image dimension in pixels.
        rotation: Axis-angle rotation string.
        path: If provided, write to file (SVG or PNG).
            Returns None. If None, return SVG string.
        cube_size: Cube dimension (2 for 2x2, 3 for 3x3,
            etc.). Inferred from source if None.

    Returns:
        SVG string if path is None, otherwise None.

    Raises:
        ValueError: If size <= 0, rotation is invalid,
            or file extension is unsupported.

    """
    if size <= 0:
        msg = f'size must be positive, got {size}'
        raise ValueError(msg)

    rotations = _parse_rotation(rotation)
    state, n = _get_state(source, cube_size)
    svg = _build_svg(state, size, rotations, n)

    if path is None:
        return svg

    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == '.svg':
        path.write_text(svg, encoding='utf-8')
    elif suffix == '.png':
        _to_png(svg, path, size)
    else:
        msg = (
            f'Unsupported file extension: {suffix!r}. '
            f'Use .svg or .png.'
        )
        raise ValueError(msg)

    return None


def _to_png(
    svg_str: str, path: Path, size: int,
) -> None:
    """
    Convert SVG to PNG using cairosvg.

    Args:
        svg_str: SVG content as string.
        path: Output PNG file path.
        size: Output image dimension.

    Raises:
        ImportError: If cairosvg is not installed.

    """
    try:
        import cairosvg  # type: ignore[import-not-found]  # noqa: PLC0415
    except ImportError as e:
        msg = (
            'PNG export requires cairosvg. '
            'Install it with: '
            'pip install cubing-algs[image]'
        )
        raise ImportError(msg) from e

    cairosvg.svg2png(
        bytestring=svg_str.encode('utf-8'),
        write_to=str(path),
        output_width=size,
        output_height=size,
    )
