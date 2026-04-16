"""Cube image rendering in SVG and PNG formats."""
import math
import operator
import re
from typing import TYPE_CHECKING
from typing import cast

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import CubeMask
from cubing_algs.annotations import CubeOrientation
from cubing_algs.annotations import FaceFacelets
from cubing_algs.annotations import Facelet
from cubing_algs.annotations import FaceMask
from cubing_algs.annotations import RegexPattern
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.constants import DEFAULT_PALETTE
from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.constants import IMAGE_SIZE
from cubing_algs.display.constants import MIN_DISTANCE
from cubing_algs.display.constants import ROTATION
from cubing_algs.display.constants import STICKER_GAP
from cubing_algs.display.constants import STRIP_DEPTH
from cubing_algs.display.constants import STRIP_TAPER
from cubing_algs.display.constants import VISIBILITY_EPSILON
from cubing_algs.display.mode import ModeDisplay
from cubing_algs.display.palettes import DEFAULT_ARROW_COLOR
from cubing_algs.display.palettes import DEFAULT_CUBE_COLOR
from cubing_algs.display.palettes import DEFAULT_MASKED_BACKGROUND
from cubing_algs.display.palettes import PALETTES
from cubing_algs.display.palettes import hex_to_rgb
from cubing_algs.display.palettes import hex_to_rgba

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube

Point3D = tuple[float, float, float]
Point2D = tuple[float, float]
FaceData = tuple[Facelet, list[Point2D], int]

ROTATION_PATTERN: RegexPattern = re.compile(r'^([xyz]-?[0-9]+)+$')
ROTATION_PARTS: RegexPattern = re.compile(r'([xyz])(-?[0-9]+)')
ARROW_PATTERN: RegexPattern = re.compile(
    r'^([URFDLB])(\d+)([URFDLB])(\d+)'
    r'(?:-(#[0-9a-fA-F]+|[a-zA-Z]+))?$',
)

# Adjacent face layout positions relative to the U face in top view
TOP_VIEW_LAYOUT: dict[Facelet, str] = {
    'B': 'top',
    'L': 'left',
    'R': 'right',
    'F': 'bottom',
}

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
FACE_DEFS: list[tuple[Facelet, Point3D, list[int], int]] = [
    ('U', (0, 1, 0), [3, 2, 6, 7], 0),
    ('D', (0, -1, 0), [4, 5, 1, 0], 3),
    ('R', (1, 0, 0), [6, 2, 1, 5], 1),
    ('L', (-1, 0, 0), [3, 7, 4, 0], 4),
    ('F', (0, 0, 1), [7, 6, 5, 4], 2),
    ('B', (0, 0, -1), [2, 3, 0, 1], 5),
]


class ImageDisplay(ModeDisplay):  # noqa: PLR0904
    """
    Handle image representation and generation.

    Provides methods to render cube states with different display modes,
    color palettes, in SVG format.
    """

    def __init__(
            self,
            cube: 'VCube',
            palette_name: str = '',
    ) -> None:
        """Initialize display handler with cube instance and color settings."""
        self.cube = cube
        self.cube_size: int = cube.size
        self.face_size: int = cube.face_size
        self.face_number: int = cube.face_number

        self.palette_name = (palette_name or DEFAULT_PALETTE).lower()

        self.palette = self.load_palette()

    def load_palette(self) -> dict[str, str]:
        """
        Build a face-letter to hex-color mapping from a palette.

        Returns:
            Dictionary mapping face letters (U/R/F/D/L/B)
            to hex color strings.

        """
        config = PALETTES.get(self.palette_name, PALETTES['default'])
        faces = config['faces']

        palette = {
            face: (
                entry['background']
                if isinstance(entry, dict)
                else entry
            )
            for face, entry in zip(FACE_ORDER, faces, strict=True)
        }
        palette['masked'] = config.get(
            'masked_background',
            DEFAULT_MASKED_BACKGROUND,
        )
        palette['cube_color'] = config.get(
            'cube_color',
            DEFAULT_CUBE_COLOR,
        )
        palette['arrow'] = config.get(
            'arrow',
            DEFAULT_ARROW_COLOR,
        )

        return palette

    def render(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            mask: CubeMask = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
            arrows: str = '',
    ) -> str:
        """
        Generate a SVG visual representation of the cube state.

        ``mode`` is a convenient shorthand that presets ``mask``,
        ``orientation``, and ``layout`` for common solving stages.
        Any explicit argument overrides what ``mode`` would have implied.

        Args:
            mode: Display preset that sets layout, orientation, and mask
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            layout: Display layout; 'top' renders a flat 2D top-view,
                    otherwise a 3D perspective view is used.
            orientation: Cube orientation string for reorienting the view
                         before rendering.
            mask: Mask to filter which facelets are displayed.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string for the 3D view, composed of
                      axis-angle pairs (e.g., 'y45x-30').
            distance: Camera distance from the cube center for the 3D view.
            arrows: Comma-separated arrow definitions of the form
                    ``<face><index><face><index>`` with an optional
                    ``-<color>`` suffix (e.g., 'U0U2,R6R2-red,U2U8-#ff0000').
                    The color may be a CSS named color or a hex value;
                    when omitted, the palette arrow color is used.
                    Arrows must stay on a single face; invalid entries
                    raise ``ValueError``.

        Returns:
            SVG string of the cube.

        """
        mode_mask, mode_layout, mode_orientation = self.resolve_mode(
            mode.lower(),
        )

        final_orientation = orientation or mode_orientation
        if final_orientation:
            cube = self.cube.oriented_copy(final_orientation, full=True)
        else:
            cube = self.cube

        mapped_mask = self.map_mask(
            cube,
            mask or mode_mask,
        )

        parsed_arrows = self.parse_arrows(arrows)

        if (layout or mode_layout) == 'top':
            return self.render_top(
                image_size or IMAGE_SIZE,
                cube.state,
                mapped_mask,
                parsed_arrows,
            )

        return self.render_cube(
            image_size or IMAGE_SIZE,
            cube.state,
            mapped_mask,
            rotation or ROTATION,
            distance or DISTANCE,
            parsed_arrows,
        )

    def render_cube(  # noqa: PLR0913, PLR0914, PLR0917
            self,
            image_size: int,
            state: CubeFacelets,
            mask: CubeDisplayMask,
            rotation: str = '',
            distance: float = 0.0,
            arrows: (
                list[tuple[Facelet, int, Facelet, int, str]] | None
            ) = None,
    ) -> str:
        """
        Build a 3D SVG cube.

        Args:
            image_size: Output image dimension in pixels (width and height).
            state: Complete cube state string representing all facelets.
            mask: Mask to filter which facelets are displayed.
            rotation: Camera rotation string for the 3D view, composed of
                      axis-angle pairs (e.g., 'y45x-30').
            distance: Camera distance from the cube center for the 3D view.
            arrows: Pre-parsed arrow tuples ``(from_face, from_idx,
                    to_face, to_idx, color)``. An empty ``color`` falls
                    back to the palette arrow color. ``None`` means no
                    arrows.

        Returns:
            Complete SVG document as a string.

        """
        distance = max(distance, MIN_DISTANCE + 0.01)

        rotations = self.parse_rotation(rotation)
        visible = self.compute_visible_faces(rotations, distance)

        margin = image_size * 0.002
        max_extent = math.sqrt(
            3 * distance ** 2 / (distance ** 2 - 3),
        )
        scale = (image_size - 2 * margin) / (2 * max_extent)
        cx, cy = image_size / 2, image_size / 2

        cr, cg, cb, ca = hex_to_rgba(self.palette['cube_color'])
        body_fill = f'rgba({cr},{cg},{cb},{ca:.2f})'

        # Draw each visible face back-to-front: the face body polygon
        # first, then its stickers on top. Per-face body polygons cover
        # exactly the projected face area, so near edge-on faces do not
        # leave gaps that would show through a larger silhouette fill.
        face_groups: list[str] = []
        for face_name, corners_2d, face_state_idx in visible:
            svg_corners = [
                self.point_to_svg_coords(c, cx, cy, scale)
                for c in corners_2d
            ]
            face_start = face_state_idx * self.face_size
            face_stickers = self.build_face_stickers(
                svg_corners,
                state[face_start:face_start + self.face_size],
                mask[face_start:face_start + self.face_size],
            )
            body = self.build_polygon(svg_corners, body_fill)
            face_groups.append(
                f'<g class="face-{ face_name }">\n'
                f'{ body }\n{ "\n".join(face_stickers) }\n</g>',
            )

        if arrows:
            visible_by_face: dict[Facelet, list[Point2D]] = {
                face_name: [
                    self.point_to_svg_coords(c, cx, cy, scale)
                    for c in corners_2d
                ]
                for face_name, corners_2d, _ in visible
            }
            arrow_group = self.build_arrows_group(
                arrows,
                visible_by_face,
                image_size,
            )
            if arrow_group:
                face_groups.append(arrow_group)

        return self.assemble_svg(image_size, face_groups)

    def render_top(  # noqa: PLR0914
            self,
            image_size: int,
            state: CubeFacelets,
            mask: CubeDisplayMask,
            arrows: (
                list[tuple[Facelet, int, Facelet, int, str]] | None
            ) = None,
    ) -> str:
        """
        Build a flat 2D top-face SVG showing top face and adjacent strips.

        Renders the top face as a central square with projected
        trapezoid strips from the adjacent faces flush against
        the top face edges.

        Args:
            image_size: Output image dimension in pixels (width and height).
            state: Complete cube state string representing all facelets.
            mask: Mask to filter which facelets are displayed.
            arrows: Pre-parsed arrow tuples. Only U-face arrows render
                    in the top view; other faces are silently skipped.

        Returns:
            Complete SVG document as a string.

        """
        margin = image_size * 0.05
        total_cells = self.cube_size + 2 * STRIP_DEPTH
        cell = (image_size - 2 * margin) / total_cells

        cr, cg, cb, ca = hex_to_rgba(self.palette['cube_color'])
        body_fill = f'rgba({cr},{cg},{cb},{ca:.2f})'

        u_origin = margin + STRIP_DEPTH * cell
        u_size = self.cube_size * cell
        depth = STRIP_DEPTH * cell
        taper = STRIP_TAPER * u_size

        # U face
        u_corners: list[Point2D] = [
            (u_origin, u_origin),
            (u_origin + u_size, u_origin),
            (u_origin + u_size, u_origin + u_size),
            (u_origin, u_origin + u_size),
        ]
        body = self.build_polygon(u_corners, body_fill)

        stickers: list[str] = []
        for row in range(self.cube_size):
            for col in range(self.cube_size):
                sticker_corners = self.build_top_sticker_points(
                    u_corners,
                    row,
                    col,
                )
                index = row * self.cube_size + col

                fill = self.get_sticker_fill(state[index], mask[index])
                stickers.append(
                    self.build_polygon(
                        sticker_corners,
                        fill,
                    ),
                )

        face_groups: list[str] = [
            f'<g class="face-U">\n{ body }\n{ "\n".join(stickers) }\n</g>',
        ]

        # Adjacent strips as projected trapezoids
        for face_name, layout in TOP_VIEW_LAYOUT.items():
            face_start = FACE_INDEXES[face_name] * self.face_size
            top_row = state[face_start : face_start + self.cube_size]
            mask_row = mask[face_start : face_start + self.cube_size]
            corners = self.strip_corners(
                layout,
                u_origin,
                u_origin,
                u_size,
                depth,
                taper,
            )
            face_groups.append(
                self.build_strip_group(
                    face_name,
                    top_row,
                    mask_row,
                    layout,
                    corners,
                    body_fill,
                ),
            )

        if arrows:
            arrow_group = self.build_top_arrows_group(
                arrows,
                u_corners,
                image_size,
            )
            if arrow_group:
                face_groups.append(arrow_group)

        return self.assemble_svg(image_size, face_groups)

    def build_polygon(
            self,
            corners: list[Point2D],
            fill: str,
    ) -> str:
        """
        Build an SVG polygon element from corner points.

        Returns:
            SVG polygon element string.

        """
        return (
            f'  <polygon'
            f' points="{self.points_to_svg(corners)}"'
            f' fill="{ fill }"/>'
        )

    @staticmethod
    def build_arrow_svg(
            from_point: Point2D,
            to_point: Point2D,
            color: str,
            image_size: int,
    ) -> str:
        """
        Build SVG elements for a single arrow.

        Emits an inline line and a triangular arrowhead at the tip,
        scaled to the image size. Returns an empty string if the arrow
        has zero length.

        Args:
            from_point: Start point of the arrow in SVG coordinates.
            to_point: End point of the arrow in SVG coordinates.
            color: Stroke and fill color (hex or CSS color string).
            image_size: Output image dimension used for scaling.

        Returns:
            SVG snippet containing a ``<line>`` followed by a ``<polygon>``.

        """
        fx, fy = from_point
        tx, ty = to_point
        length = math.hypot(tx - fx, ty - fy)

        if length == 0:
            return ''

        head_length = image_size / 25
        ux, uy = (tx - fx) / length, (ty - fy) / length
        px, py = -uy, ux

        line_end_x = tx - ux * head_length
        line_end_y = ty - uy * head_length
        hw = head_length * 0.3

        return '\n'.join([
            (
                f'  <line'
                f' x1="{fx:.2f}" y1="{fy:.2f}"'
                f' x2="{line_end_x:.2f}" y2="{line_end_y:.2f}"'
                f' stroke="{color}"'
                f' stroke-width="{image_size / 100:.2f}"'
                f' stroke-linecap="round"/>'
            ),
            (
                f'  <polygon'
                f' points="'
                f'{tx:.2f},{ty:.2f} '
                f'{line_end_x + px * hw:.2f},{line_end_y + py * hw:.2f} '
                f'{line_end_x - px * hw:.2f},{line_end_y - py * hw:.2f}'
                f'" fill="{color}"/>'
            ),
        ])

    def get_sticker_fill(self, color_key: str, mask_char: str) -> str:
        """
        Resolve the SVG fill color for a facelet given its mask value.

        Args:
            color_key: Face letter identifying the facelet color in the palette.
            mask_char: Mask character; '0' uses masked color, '2' applies
                       50% transparency, '1' uses the normal color.

        Returns:
            SVG fill color string.

        """
        if mask_char == '2':
            return self.palette['masked']

        if mask_char == '3':
            return 'rgb(0,0,0,0.0)'

        fill = self.palette[color_key]

        if mask_char == '0':
            r, g, b = hex_to_rgb(fill)
            return f'rgba({r},{g},{b},0.25)'

        return fill

    def build_face_stickers(
            self,
            svg_corners: list[Point2D],
            facelets: FaceFacelets,
            mask: FaceMask,
    ) -> list[str]:
        """
        Build sticker polygon elements for one face.

        Returns:
            List of SVG polygon element strings.

        """
        stickers: list[str] = []

        for row in range(self.cube_size):
            for col in range(self.cube_size):
                idx = row * self.cube_size + col

                fill = self.get_sticker_fill(facelets[idx], mask[idx])

                stickers.append(
                    self.build_sticker_polygon(
                        svg_corners,
                        row,
                        col,
                        fill,
                    ),
                )

        return stickers

    def build_arrows_group(
            self,
            arrows: list[tuple[Facelet, int, Facelet, int, str]],
            face_corners: dict[Facelet, list[Point2D]],
            image_size: int,
    ) -> str:
        """
        Build the arrows SVG group for the 3D view.

        Arrows whose face is not in ``face_corners`` are silently
        skipped (typically because they fall on a hidden face at the
        current rotation).

        Args:
            arrows: Parsed arrow tuples. The 5th element is the per-arrow
                    color; an empty string falls back to the palette
                    arrow color.
            face_corners: Visible face name to its 4 projected
                          SVG corners.
            image_size: Output image dimension used for arrow scaling.

        Returns:
            SVG group element string, or empty string if no arrows
            are visible.

        """
        default_color = self.palette['arrow']
        snippets: list[str] = []

        for arrow in arrows:
            from_face = arrow[0]
            from_idx = arrow[1]
            to_idx = arrow[3]
            color = arrow[4] or default_color

            corners = face_corners.get(from_face)

            if corners is None:
                continue

            from_row, from_col = divmod(from_idx, self.cube_size)
            to_row, to_col = divmod(to_idx, self.cube_size)

            from_center = self.sticker_center(
                self.build_sticker_polygon_points(
                    corners, from_row, from_col,
                ),
            )
            to_center = self.sticker_center(
                self.build_sticker_polygon_points(
                    corners, to_row, to_col,
                ),
            )

            snippet = self.build_arrow_svg(
                from_center, to_center, color, image_size,
            )
            if snippet:
                snippets.append(snippet)

        if not snippets:
            return ''

        return (
            '<g class="arrows">\n'
            + '\n'.join(snippets)
            + '\n</g>'
        )

    def build_top_arrows_group(
            self,
            arrows: list[tuple[Facelet, int, Facelet, int, str]],
            u_corners: list[Point2D],
            image_size: int,
    ) -> str:
        """
        Build the arrows SVG group for the top view.

        Only U-face arrows are rendered; arrows targeting other faces
        are silently skipped.

        Args:
            arrows: Parsed arrow tuples. The 5th element is the per-arrow
                    color; an empty string falls back to the palette
                    arrow color.
            u_corners: The 4 corners of the U face in SVG coordinates.
            image_size: Output image dimension used for arrow scaling.

        Returns:
            SVG group element string, or empty string if no arrows
            are rendered.

        """
        default_color = self.palette['arrow']
        snippets: list[str] = []

        for arrow in arrows:
            from_face = arrow[0]
            from_idx = arrow[1]
            to_idx = arrow[3]
            color = arrow[4] or default_color

            if from_face != 'U':
                continue

            from_row, from_col = divmod(from_idx, self.cube_size)
            to_row, to_col = divmod(to_idx, self.cube_size)

            from_center = self.sticker_center(
                self.build_top_sticker_points(
                    u_corners, from_row, from_col,
                ),
            )
            to_center = self.sticker_center(
                self.build_top_sticker_points(
                    u_corners, to_row, to_col,
                ),
            )

            snippet = self.build_arrow_svg(
                from_center, to_center, color, image_size,
            )
            if snippet:
                snippets.append(snippet)

        if not snippets:
            return ''

        return (
            '<g class="arrows">\n'
            + '\n'.join(snippets)
            + '\n</g>'
        )

    def build_sticker_polygon(
            self,
            svg_corners: list[Point2D],
            row: int,
            col: int,
            fill: str,
    ) -> str:
        """
        Build an SVG polygon element for a single sticker.

        Returns:
            SVG polygon element string.

        """
        corners = self.build_sticker_polygon_points(
            svg_corners, row, col,
        )
        pts = self.points_to_svg(corners)

        return (
            f'  <polygon'
            f' points="{pts}"'
            f' fill="{fill}"/>'
        )

    def build_sticker_polygon_points(
            self,
            svg_corners: list[Point2D],
            row: int,
            col: int,
    ) -> list[Point2D]:
        """
        Compute corner points for a single sticker within a face quad.

        Uses bilinear interpolation with gap insets to position
        the sticker within the face grid.

        Returns:
            Four corner points [TL, TR, BR, BL] of the sticker.

        """
        t0_col = col / self.cube_size
        t1_col = (col + 1) / self.cube_size
        t0_row = row / self.cube_size
        t1_row = (row + 1) / self.cube_size

        # Gap is per-cell: divide by n since the face is an nxn grid
        gap = STICKER_GAP / self.cube_size
        t0_col += gap
        t1_col -= gap
        t0_row += gap
        t1_row -= gap

        top_edge_0 = self.lerp_2d(
            svg_corners[0], svg_corners[1], t0_col,
        )
        top_edge_1 = self.lerp_2d(
            svg_corners[0], svg_corners[1], t1_col,
        )
        bot_edge_0 = self.lerp_2d(
            svg_corners[3], svg_corners[2], t0_col,
        )
        bot_edge_1 = self.lerp_2d(
            svg_corners[3], svg_corners[2], t1_col,
        )

        return [
            self.lerp_2d(top_edge_0, bot_edge_0, t0_row),
            self.lerp_2d(top_edge_1, bot_edge_1, t0_row),
            self.lerp_2d(top_edge_1, bot_edge_1, t1_row),
            self.lerp_2d(top_edge_0, bot_edge_0, t1_row),
        ]

    def build_top_sticker_points(
            self,
            svg_corners: list[Point2D],
            row: int,
            col: int,
    ) -> list[Point2D]:
        """
        Compute sticker corner points for the top-view U face.

        Uses reduced inner gaps so that inner and outer margins
        look visually balanced in the flat 2D layout.

        Returns:
            Four corner points [TL, TR, BR, BL] of the sticker.

        """
        n = self.cube_size
        gap = STICKER_GAP / n
        inner_gap = gap * 2 / 3

        t0_col = col / n + (gap if col == 0 else inner_gap)
        t1_col = (col + 1) / n - (gap if col == n - 1 else inner_gap)
        t0_row = row / n + (gap if row == 0 else inner_gap)
        t1_row = (row + 1) / n - (gap if row == n - 1 else inner_gap)

        top_edge_0 = self.lerp_2d(
            svg_corners[0], svg_corners[1], t0_col,
        )
        top_edge_1 = self.lerp_2d(
            svg_corners[0], svg_corners[1], t1_col,
        )
        bot_edge_0 = self.lerp_2d(
            svg_corners[3], svg_corners[2], t0_col,
        )
        bot_edge_1 = self.lerp_2d(
            svg_corners[3], svg_corners[2], t1_col,
        )

        return [
            self.lerp_2d(top_edge_0, bot_edge_0, t0_row),
            self.lerp_2d(top_edge_1, bot_edge_1, t0_row),
            self.lerp_2d(top_edge_1, bot_edge_1, t1_row),
            self.lerp_2d(top_edge_0, bot_edge_0, t1_row),
        ]

    def build_strip_group(  # noqa: PLR0913, PLR0917
            self,
            face_name: str,
            top_row: FaceFacelets,
            mask_row: FaceMask,
            layout: str,
            corners: list[Point2D],
            body_fill: str,
    ) -> str:
        """
        Build SVG group for one projected adjacent strip.

        Returns:
            SVG group element string.

        """
        is_horizontal = layout in {'top', 'bottom'}

        if layout in {'top', 'right'}:
            indices = list(range(self.cube_size - 1, -1, -1))
        else:
            indices = list(range(self.cube_size))

        body = self.build_polygon(corners, body_fill)

        stickers = [
            self.build_polygon(
                self.subdivide_quad(
                    corners,
                    pos,
                    self.cube_size,
                    horizontal=is_horizontal,
                    gap_frac=STICKER_GAP,
                ),
                self.get_sticker_fill(top_row[idx], mask_row[idx]),
            )
            for pos, idx in enumerate(indices)
        ]

        return (
            f'<g class="face-{ face_name }">\n'
            f'{ body }\n{ "\n".join(stickers) }\n</g>'
        )

    def subdivide_quad(
            self,
            corners: list[Point2D],
            idx: int, count: int,
            *,
            horizontal: bool,
            gap_frac: float,
    ) -> list[Point2D]:
        """
        Subdivide a quadrilateral into one cell of a 1xN or Nx1 grid.

        Uses bilinear interpolation with gap insets, matching the
        approach used by :method:`build_sticker_polygon`.

        Returns:
            Four corner points of the subdivided sticker.

        """
        if horizontal:
            gap = gap_frac / count
            inner_gap = gap * 2 / 3
            t0 = idx / count + (gap if idx == 0 else inner_gap)
            t1 = (idx + 1) / count - (gap if idx == count - 1 else inner_gap)
            top0 = self.lerp_2d(corners[0], corners[1], t0)
            top1 = self.lerp_2d(corners[0], corners[1], t1)
            bot0 = self.lerp_2d(corners[3], corners[2], t0)
            bot1 = self.lerp_2d(corners[3], corners[2], t1)

            return [
                self.lerp_2d(top0, bot0, gap_frac),
                self.lerp_2d(top1, bot1, gap_frac),
                self.lerp_2d(top1, bot1, 1 - gap_frac),
                self.lerp_2d(top0, bot0, 1 - gap_frac),
            ]

        gap = gap_frac / count
        inner_gap = gap * 2 / 3
        t0 = idx / count + (gap if idx == 0 else inner_gap)
        t1 = (idx + 1) / count - (gap if idx == count - 1 else inner_gap)
        left0 = self.lerp_2d(corners[0], corners[3], t0)
        left1 = self.lerp_2d(corners[0], corners[3], t1)
        right0 = self.lerp_2d(corners[1], corners[2], t0)
        right1 = self.lerp_2d(corners[1], corners[2], t1)

        return [
            self.lerp_2d(left0, right0, gap_frac),
            self.lerp_2d(left0, right0, 1 - gap_frac),
            self.lerp_2d(left1, right1, 1 - gap_frac),
            self.lerp_2d(left1, right1, gap_frac),
        ]

    def compute_visible_faces(
            self,
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
            self.rotate_point(v, rotations) for v in CUBE_VERTICES
        ]

        visible: list[tuple[Facelet, list[Point2D], int, float]] = []

        for name, normal, indices, state_idx in FACE_DEFS:
            rn = self.rotate_point(normal, rotations)

            if rn[2] > VISIBILITY_EPSILON:
                corners_3d = [rotated[i] for i in indices]
                corners_2d = [
                    self.project(c, distance)
                    for c in corners_3d
                ]
                avg_z = sum(c[2] for c in corners_3d) / 4
                visible.append(
                    (name, corners_2d, state_idx, avg_z),
                )

        visible.sort(key=operator.itemgetter(3))

        return [
            (name, corners, idx)
            for name, corners, idx, _ in visible
        ]

    @staticmethod
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

    @staticmethod
    def strip_corners(  # noqa: PLR0913, PLR0917
            layout: str,
            u_left: float,
            u_top: float,
            u_size: float,
            depth: float,
            taper: float,
    ) -> list[Point2D]:
        """
        Compute trapezoid corners for an adjacent strip.

        Corners are ordered top-left, top-right, bottom-right,
        bottom-left for consistent bilinear interpolation.
        A small overlap into the U face eliminates anti-aliasing seams.

        Returns:
            Four corner points of the strip trapezoid.

        """
        u_right = u_left + u_size
        u_bottom = u_top + u_size
        # Overlap to prevent anti-aliasing gaps between strips and U face
        overlap = 0.5

        if layout == 'top':
            return [
                (u_left + taper, u_top - depth),
                (u_right - taper, u_top - depth),
                (u_right, u_top + overlap),
                (u_left, u_top + overlap),
            ]
        if layout == 'bottom':
            return [
                (u_left, u_bottom - overlap),
                (u_right, u_bottom - overlap),
                (u_right - taper, u_bottom + depth),
                (u_left + taper, u_bottom + depth),
            ]
        if layout == 'left':
            return [
                (u_left - depth, u_top + taper),
                (u_left + overlap, u_top),
                (u_left + overlap, u_bottom),
                (u_left - depth, u_bottom - taper),
            ]
        # right
        return [
            (u_right - overlap, u_top),
            (u_right + depth, u_top + taper),
            (u_right + depth, u_bottom - taper),
            (u_right - overlap, u_bottom),
        ]

    @staticmethod
    def lerp_2d(
            p0: Point2D,
            p1: Point2D,
            t: float,
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

    @staticmethod
    def sticker_center(
            corners: list[Point2D],
    ) -> Point2D:
        """
        Compute the centroid of a sticker polygon.

        Returns:
            Mean (x, y) of the corner points.

        """
        sx = sum(p[0] for p in corners) / len(corners)
        sy = sum(p[1] for p in corners) / len(corners)
        return (sx, sy)

    @staticmethod
    def points_to_svg(points: list[Point2D]) -> str:
        """
        Convert 2D points to an SVG points attribute string.

        Returns:
            Space-separated "x,y" coordinate pairs.

        """
        return ' '.join(
            f'{x:.2f},{y:.2f}' for x, y in points
        )

    @staticmethod
    def point_to_svg_coords(
            p: Point2D,
            cx: float,
            cy: float,
            scale: float,
    ) -> Point2D:
        """
        Convert 2D point to SVG coordonates.

        Returns:
            Converted 2D point.

        """
        return (cx + p[0] * scale, cy - p[1] * scale)

    @staticmethod
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

    @staticmethod
    def parse_rotation(rotation: str) -> list[tuple[str, int]]:
        """
        Parse a rotation string into axis-angle pairs.

        Args:
            rotation: Rotation string like "y45x-34".

        Returns:
            List of (axis, degrees) tuples.

        """
        if not ROTATION_PATTERN.match(rotation):
            rotation = ROTATION

        return [
            (m.group(1), int(m.group(2)))
            for m in ROTATION_PARTS.finditer(rotation)
        ]

    def parse_arrows(
            self,
            arrows: str,
    ) -> list[tuple[Facelet, int, Facelet, int, str]]:
        """
        Parse an arrows specification string into structured tuples.

        Each arrow entry has the form ``<face><index><face><index>`` with
        an optional ``-<color>`` suffix, where face is one of U/R/F/D/L/B,
        index is a non-negative integer within the current face size, and
        color is either a CSS named color (e.g. ``red``) or a hex value
        (e.g. ``#ff0000``). Entries are comma-separated.

        Args:
            arrows: Arrows specification string; empty means no arrows.

        Returns:
            List of ``(from_face, from_idx, to_face, to_idx, color)``
            tuples. ``color`` is an empty string when no color was given,
            in which case the palette default is used at render time.

        Raises:
            ValueError: If any entry is malformed, crosses two different
                faces, has an out-of-range index, or has identical endpoints.

        """
        if not arrows:
            return []

        parsed: list[tuple[Facelet, int, Facelet, int, str]] = []

        for raw in arrows.split(','):
            entry = raw.strip()
            match = ARROW_PATTERN.match(entry)

            if match is None:
                msg = f'Invalid arrow definition: {entry!r}'
                raise ValueError(msg)

            from_face = cast('Facelet', match.group(1))
            from_idx = int(match.group(2))
            to_face = cast('Facelet', match.group(3))
            to_idx = int(match.group(4))
            color = match.group(5) or ''

            if from_face != to_face:
                msg = f'Cross-face arrows are not supported: {entry!r}'
                raise ValueError(msg)

            if from_idx >= self.face_size or to_idx >= self.face_size:
                msg = f'Arrow index out of range for cube size: {entry!r}'
                raise ValueError(msg)

            if from_idx == to_idx:
                msg = f'Arrow endpoints are identical: {entry!r}'
                raise ValueError(msg)

            parsed.append((from_face, from_idx, to_face, to_idx, color))

        return parsed

    @staticmethod
    def assemble_svg(
            image_size: int,
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
                f' viewBox="0 0 { image_size } { image_size }"'
                f' width="{ image_size }" height="{ image_size }">'
            ),
        ]

        lines.extend(face_groups)
        lines.append('</svg>')

        return '\n'.join(lines)
