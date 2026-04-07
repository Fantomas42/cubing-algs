"""Visual representation and display formatting for virtual cube states."""
import os
import re
from typing import TYPE_CHECKING
from typing import cast

from cubing_algs.annotations import Mask
from cubing_algs.annotations import RegexPattern
from cubing_algs.constants import F2L_ADJACENT_FACES
from cubing_algs.constants import F2L_FACE_ORIENTATIONS
from cubing_algs.constants import F2L_FACES
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.effects import load_effect
from cubing_algs.display.palettes import load_palette
from cubing_algs.display.styles import load_style
from cubing_algs.masks import CROSS_BOTTOM_MASK
from cubing_algs.masks import CROSS_TOP_MASK
from cubing_algs.masks import F2L_CLL_MASK
from cubing_algs.masks import F2L_ELL_MASK
from cubing_algs.masks import F2L_LL_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import L3_MASK
from cubing_algs.masks import OLL_MASK
from cubing_algs.masks import PLL_MASK

if TYPE_CHECKING:
    from collections.abc import Callable

    from cubing_algs.vcube import VCube  # pragma: no cover


def color_support() -> bool:
    """
    Return boolean telling if terminal support color.

    Returns:
       Is the terminal support colors.

    """
    if os.environ.get('COLORTERM', '') in {'truecolor', '24bit'}:
        return True
    return '256color' in os.environ.get('TERM', '')


USE_COLORS = color_support()

DEFAULT_EFFECT = os.getenv('CUBING_ALGS_EFFECT', '')
DEFAULT_PALETTE = os.getenv('CUBING_ALGS_PALETTE', 'default')
DEFAULT_STYLE = os.getenv('CUBING_ALGS_STYLE', 'default')

ANSI_TO_RGB: RegexPattern = re.compile(
    r'\x1b\[48;2;(\d+);(\d+);(\d+)m\x1b\[38;2;(\d+);(\d+);(\d+)m',
)

EMOJIS = {
    'U': '⬜',
    'D': '🟨',
    'F': '🟩',
    'B': '🟦',
    'L': '🟧',
    'R': '🟥',
    'masked': '⬛',
    'hidden': '❓',
}

LAYOUT_METHODS: dict[str, str] = {
    'top': 'display_top_face',
    'extended': 'display_extended_net',
    'linear': 'display_linear',
    'cube': 'display_cube',
}


class VCubeDisplay:
    """
    Handle visual representation and display formatting for virtual cubes.

    Provides methods to render cube states with different display modes,
    color palettes, and visual effects for terminal output.
    """

    facelet_size = 3

    def __init__(self, cube: 'VCube',
                 palette_name: str = '',
                 effect_name: str = '',
                 facelet_type: str = '',
                 style_name: str = '') -> None:
        """Initialize display handler with cube instance and visual settings."""
        self.cube = cube
        self.cube_size: int = cube.size
        self.face_size: int = self.cube_size * self.cube_size
        self.face_number: int = cube.face_number

        self.effect_name = (effect_name or DEFAULT_EFFECT).lower()
        self.palette_name = (palette_name or DEFAULT_PALETTE).lower()
        self.style_name = (style_name or DEFAULT_STYLE).lower()
        self.facelet_type = facelet_type.lower()

        self.palette = load_palette(self.palette_name)
        self.effect = load_effect(self.effect_name, self.palette_name)
        self.style = load_style(self.style_name)

        if self.facelet_type == 'compact':
            self.facelet_size = 2
        elif self.facelet_type in {'condensed', 'emoji'}:
            self.facelet_size = 1

    def compute_mask(self, cube: 'VCube', mask: Mask) -> Mask:
        """
        Convert mask string to facelets format for display filtering.

        Args:
            cube: The virtual cube instance to process.
            mask: Mask string in cubies format or empty string.

        Returns:
            Facelets format mask string where '1' indicates visible facelets.

        """
        if not mask:
            return '1' * (self.face_number * self.face_size)

        from cubing_algs.vcube import VCube  # noqa: PLC0415

        cube_mask = VCube(
            initial=mask,
            size=cube.size,
            check=False,
        )
        cube_mask.rotate(' '.join(cube.history))

        return cube_mask.state

    def compute_f2l_front_face(self) -> str:
        """
        Determine the optimal front face orientation for F2L display mode.

        Returns:
            Single character representing the optimal front face for F2L.

        """
        impacted_faces = ''
        saved_facelets = ''
        cube_d_top = self.cube.oriented_copy('D')

        for face in F2L_FACES:
            exclusion_pattern = face * 6
            facelets = cube_d_top.get_face_by_center(face)[
                self.cube_size:self.face_size
            ]

            if exclusion_pattern != facelets:
                impacted_faces += face
                saved_facelets = facelets

        if impacted_faces and len(impacted_faces) != 2:
            last_face = impacted_faces[-1]
            index = (
                0
                if saved_facelets[0] != last_face
                or saved_facelets[3] != last_face
                else 1
            )
            impacted_faces = (
                last_face
                + F2L_ADJACENT_FACES[last_face][index]
            )

        return F2L_FACE_ORIENTATIONS.get(
            ''.join(sorted(impacted_faces)),
            '',
        )

    def split_faces(self, state: str) -> list[str]:
        """
        Split cube state string into individual face strings.

        Args:
            state: Complete cube state string representing all facelets.

        Returns:
            List of face strings, one per face of the cube.

        """
        return [
            state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(self.face_number)
        ]

    def display(self, *,  # noqa: C901
                mode: str = '', layout: str = '',
                orientation: str = '', mask: Mask = '') -> str:
        """
        Generate formatted visual representation of the cube state.

        ``mode`` is a convenient shorthand that presets ``mask``,
        ``orientation``, and ``layout`` for common solving stages.
        Any explicit argument overrides what ``mode`` would have implied.

        Args:
            mode: Solving-stage preset (3x3x3 only).
                Sets mask, orientation, and layout together.
                Supported values: ``'oll'``, ``'pll'``, ``'ll'``,
                ``'cross'``, ``'f2l'``, ``'af2l'``, ``'f2l+ll'``,
                ``'f2l+cll'``, ``'f2l+ell'``.
            layout: Face arrangement for the output.
                One of ``'cube'`` (cross net, default),
                ``'top'`` (U face with one row of each adjacent face),
                ``'extended'`` (full unfolded net), or
                ``'linear'`` (every face printed side by side row by row).
            orientation: Two-character string that rotates the cube to change
                the viewer's point of view before rendering (e.g. ``'UF'``
                keeps U on top and F in front, ``'DF'`` puts D on top).
            mask: 54-character binary string in facelet-state format (same
                layout as ``VCube.state``). ``'1'`` facelets are shown
                normally; ``'0'`` facelets are greyed out. When provided
                directly, the mask is used as-is and only rotated through
                the cube's move history. When implied by ``mode``, the
                predefined mask is written in user-POV coordinates and first
                converted to internal cube coordinates (e.g. U-D after a z2)
                before being tracked through the history.

        Returns:
            Formatted string representation of the cube state.

        """
        mode_mask = ''
        mode_orientation = ''
        mode_layout = ''

        mode = mode.lower()
        layout = layout.lower()

        def rotata(mask: Mask) -> Mask:
            from cubing_algs.vcube import VCube

            cube = VCube(
                mask,
                size=self.cube.size,
                check=False,
            )
            cube.rotate(
                self.cube.compute_orientation_moves('UF'),
            )

            return cube.state

        # Only work for 3x3x3
        if mode == 'oll':
            mode_mask = OLL_MASK
            mode_layout = 'top'
        elif mode == 'pll':
            mode_mask = PLL_MASK
            mode_layout = 'top'
        elif mode == 'll':
            mode_mask = L3_MASK
            mode_layout = 'top'
        elif mode == 'cross-top':
            mode_mask = CROSS_TOP_MASK
            mode_orientation = 'FD'
        elif mode in {'cross', 'cross-bottom'}:
            mode_mask = CROSS_BOTTOM_MASK
            mode_orientation = 'FU'
        elif mode in {'f2l', 'af2l'}:
            mode_mask = F2L_MASK
            mode_orientation = f'D{ self.compute_f2l_front_face() }'
        elif mode == 'f2l+ll':
            mode_mask = F2L_LL_MASK
            mode_orientation = f'D{ self.compute_f2l_front_face() }'
        elif mode == 'f2l+cll':
            mode_mask = F2L_CLL_MASK
            mode_orientation = f'D{ self.compute_f2l_front_face() }'
        elif mode == 'f2l+ell':
            mode_mask = F2L_ELL_MASK
            mode_orientation = f'D{ self.compute_f2l_front_face() }'

        display_method = cast(
            'Callable[[list[str], list[str]], str]',
            getattr(
                self,
                LAYOUT_METHODS.get(
                    layout or mode_layout,
                    'display_cube',
                ),
            ),
        )

        final_orientation = orientation or mode_orientation
        if final_orientation:
            cube = self.cube.oriented_copy(final_orientation, full=True)
        else:
            cube = self.cube

        faces = self.split_faces(cube.state)
        masked_faces = self.split_faces(
            self.compute_mask(
                cube,
                mask or rotata(mode_mask),
            ),
        )

        return display_method(faces, masked_faces)

    def display_spaces(self, count: int) -> str:
        """
        Generate a string of spaces for display formatting.

        Args:
            count: Number of facelet-width units to create spaces for.

        Returns:
            String containing the appropriate number of spaces.

        """
        if self.facelet_type == 'emoji':
            return '  ' * (self.facelet_size * count)

        return ' ' * (self.facelet_size * count)

    def display_facelet(self, facelet: str, mask: str = '',  # noqa: C901, PLR0911, PLR0912
                        facelet_index: int | None = None,
                        *, adjacent: bool = False) -> str:
        """
        Format a single facelet with colors and effects for display.

        Args:
            facelet: Single character representing the facelet color.
            mask: Mask character ('0' for masked, otherwise visible).
            facelet_index: Position index for applying visual effects.
            adjacent: Whether this facelet is adjacent to the main display area.

        Returns:
            Formatted string with ANSI color codes for terminal display.

        """
        if self.facelet_type == 'emoji':
            if mask == '0':
                return EMOJIS['masked']
            if facelet not in FACE_ORDER:
                return EMOJIS['hidden']
            return EMOJIS[facelet]

        if not USE_COLORS or self.facelet_type == 'no-color':
            return f' { facelet } '

        if facelet not in FACE_ORDER:
            face_color = self.palette[
                'hidden_adjacent' if adjacent else 'hidden'
            ]
        else:
            face_key = facelet
            if adjacent:
                face_key += '_adjacent'
            elif mask == '0':
                face_key += '_masked'
            face_color = self.palette[face_key]

        if self.effect and not adjacent and facelet_index is not None:
            face_color = self.position_based_effect(
                face_color, facelet_index,
            )

        if self.facelet_type == 'unlettered':
            return (
                f'{ face_color }'
                f'   '
                f'{ self.palette["reset"] }'
            )

        if self.facelet_type == 'compact':
            return (
                f"\x1b{ face_color.split('\x1b')[1].replace('48', '38') }"
                f'◼︎ '
                f'{ self.palette["reset"] }'
            )

        if self.facelet_type == 'condensed':
            return (
                f'\x1b{ face_color.split("\x1b")[1].replace("48", "38") }'
                f'◼︎'
                f'{ self.palette["reset"] }'
            )

        style_start = ''
        style_end = ''

        if not adjacent and facelet_index is not None:
            style_start, style_end = self.letter_style_ansi(
                facelet_index, face_color,
            )

        return (
            f'{ face_color }'
            f' { style_start }{ facelet }{ style_end } '
            f'{ self.palette["reset"] }'
        )

    def display_face_row(self, faces: list[str], faces_mask: list[str],
                         face_key: str, row: int) -> str:
        """
        Display a complete row of a face.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.
            face_key: Single character identifying which face to display.
            row: Row number to display (0-indexed).

        Returns:
            Formatted string representing the face row with colors.

        """
        result = ''
        face_idx = FACE_INDEXES[face_key]

        for col in range(self.cube_size):
            index = row * self.cube_size + col
            result += self.display_facelet(
                faces[face_idx][index],
                faces_mask[face_idx][index],
                (face_idx * self.face_size) + index,
            )

        return result

    def display_facelet_by_face(self, faces: list[str], faces_mask: list[str],
                                face_key: str, index: int, *,
                                adjacent: bool = True) -> str:
        """
        Display a specific facelet from a face using face key and index.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.
            face_key: Single character identifying which face to use.
            index: Facelet index within the face.
            adjacent: Whether this facelet is adjacent to the main display area.

        Returns:
            Formatted string for the specified facelet.

        """
        face_idx = FACE_INDEXES[face_key]

        return self.display_facelet(
            faces[face_idx][index],
            faces_mask[face_idx][index],
            (face_idx * self.face_size) + index,
            adjacent=adjacent,
        )

    def display_face_indexes(self, faces: list[str], faces_mask: list[str],
                             face_key: str, indexes: list[int], *,
                             adjacent: bool = True) -> str:
        """
        Display multiple facelets from a face using specified indexes.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.
            face_key: Single character identifying which face to use.
            indexes: List of facelet indexes to display.
            adjacent: Whether these facelets are adjacent to the main display.

        Returns:
            Formatted string containing all specified facelets.

        """
        return ''.join(
            self.display_facelet_by_face(
                faces, faces_mask,
                face_key, idx,
                adjacent=adjacent,
            )
            for idx in indexes
        )

    def display_row_with_sides(self, faces: list[str], faces_mask: list[str],  # noqa: PLR0913 PLR0917
                               center_face: str,
                               left_indexes: list[int],
                               right_indexes: list[int],
                               row: int,
                               leading_spaces: int = 0, *,
                               adjacent: bool = True) -> str:
        """
        Display a row with center face and adjacent side facelets.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.
            center_face: Single character identifying the center face.
            left_indexes: Indexes for left side facelets.
            right_indexes: Indexes for right side facelets.
            row: Row number to display.
            leading_spaces: Number of leading space units to add.
            adjacent: Whether side facelets are adjacent to main display.

        Returns:
            Formatted string representing the complete row with sides.

        """
        row_result = self.display_spaces(leading_spaces)
        row_result += self.display_facelet_by_face(
            faces, faces_mask,
            'L', left_indexes[row],
            adjacent=adjacent,
        )

        row_result += self.display_face_row(
            faces, faces_mask,
            center_face, row,
        )

        row_result += self.display_facelet_by_face(
            faces, faces_mask,
            'R', right_indexes[row],
            adjacent=adjacent,
        )
        row_result += '\n'

        return row_result

    def display_top_down_face(self, face: str, face_mask: str,
                              face_index: int) -> str:
        """
        Display a complete face in top-down view with proper spacing.

        Args:
            face: Face string containing all facelets for this face.
            face_mask: Mask string for this face.
            face_index: Index of this face in the cube's face ordering.

        Returns:
            Formatted string representing the face in top-down layout.

        """
        result = ''

        for row in range(self.cube_size):
            result += self.display_spaces(self.cube_size)
            for col in range(self.cube_size):
                index = row * self.cube_size + col
                result += self.display_facelet(
                    face[index],
                    face_mask[index],
                    (face_index * self.face_size) + index,
                )
            result += '\n'

        return result

    def display_top_down_adjacent_facelets(self, face: str, face_mask: str,  # noqa: PLR0913
                                           face_index: int, *,
                                           top: bool = False,
                                           end: bool = False,
                                           spaces: int = 0,
                                           adjacent: bool = True,
                                           break_line: bool = True) -> str:
        """
        Display adjacent facelets in a linear arrangement.

        Args:
            face: Face string containing facelets to display.
            face_mask: Mask string for this face.
            face_index: Index of this face in the cube's face ordering.
            top: Whether to reverse the index range for top positioning.
            end: Whether to reverse the face string for end positioning.
            spaces: Number of leading space units to add.
            adjacent: Whether these facelets are adjacent to main display.
            break_line: Whether to add a newline at the end.

        Returns:
            Formatted string of adjacent facelets in linear arrangement.

        """
        result = self.display_spaces(spaces)
        index_range = list(range(self.cube_size))

        if end:
            face = face[::-1]
            face_mask = face_mask[::-1]

        if top:
            index_range.reverse()

        for index in index_range:
            result += self.display_facelet(
                face[index],
                face_mask[index],
                (face_index * self.face_size) + index,
                adjacent=adjacent,
            )

        if break_line:
            result += '\n'

        return result

    def display_cube(self, faces: list[str], faces_mask: list[str]) -> str:
        """
        Display cube in standard unfolded net layout.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.

        Returns:
            Formatted string showing cube in standard net layout.

        """
        middle_face_keys = ['L', 'F', 'R', 'B']

        # Top
        top_face_index = FACE_INDEXES['U']
        result = self.display_top_down_face(
            faces[top_face_index],
            faces_mask[top_face_index],
            top_face_index,
        )

        # Middle
        for row in range(self.cube_size):
            for face_key in middle_face_keys:
                result += self.display_face_row(
                    faces, faces_mask, face_key, row,
                )
            result += '\n'

        # Bottom
        bottom_face_index = FACE_INDEXES['D']
        result += self.display_top_down_face(
            faces[bottom_face_index],
            faces_mask[bottom_face_index],
            bottom_face_index,
        )

        return result

    def display_top_face(self, faces: list[str],
                         faces_mask: list[str]) -> str:
        """
        Display only the top face with surrounding adjacent facelets.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.

        Returns:
            Formatted string showing top face with adjacent facelets.

        """
        result = ''

        # Top
        top_adjacent_index = FACE_INDEXES['B']
        result = self.display_top_down_adjacent_facelets(
            faces[top_adjacent_index],
            faces_mask[top_adjacent_index],
            top_adjacent_index,
            top=True,
            end=False,
            spaces=self.cube_size,
            break_line=True,
            adjacent=False,
        )

        # Middle
        top_row = list(range(self.cube_size))
        l_indexes = top_row
        r_indexes = top_row[::-1]
        for row in range(self.cube_size):
            result += self.display_row_with_sides(
                faces, faces_mask, 'U',
                l_indexes, r_indexes,
                row, self.cube_size - 1,
                adjacent=False,
            )

        # Bottom
        bottom_adjacent_index = FACE_INDEXES['F']
        result += self.display_top_down_adjacent_facelets(
            faces[bottom_adjacent_index],
            faces_mask[bottom_adjacent_index],
            bottom_adjacent_index,
            top=False,
            end=False,
            spaces=self.cube_size,
            break_line=True,
            adjacent=False,
        )

        return result

    def display_extended_net(self, faces: list[str],
                             faces_mask: list[str]) -> str:
        """
        Display cube as an extended net layout.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.

        Returns:
            Formatted string showing cube in extended net layout.

        """
        b_face_idx = FACE_INDEXES['B']
        n = self.cube_size
        top_row = list(range(n))
        left_col = [i * n for i in range(n)]
        right_col = [i * n + (n - 1) for i in range(n)]
        bottom_row = list(range(n * (n - 1), n * n))

        # Top section with U face
        result = self.display_top_down_adjacent_facelets(
            faces[b_face_idx],
            faces_mask[b_face_idx],
            b_face_idx,
            top=True,
            end=False,
            spaces=self.cube_size + 2,
            break_line=True,
            adjacent=True,
        )

        top_l_indexes = top_row
        top_r_indexes = top_row[::-1]
        for row in range(self.cube_size):
            result += self.display_row_with_sides(
                faces, faces_mask, 'U',
                top_l_indexes, top_r_indexes,
                row, self.cube_size + 1,
                adjacent=True,
            )

        # Upper horizontal strip
        result += self.display_spaces(1)
        result += self.display_face_indexes(
            faces, faces_mask,
            'U', left_col,
            adjacent=True,
        )
        result += self.display_spaces(self.cube_size + 2)
        result += self.display_face_indexes(
            faces, faces_mask,
            'U', right_col[::-1] + top_row[::-1],
            adjacent=True,
        )
        result += '\n'

        # Central section with L F R B faces
        mid_b_indexes = right_col
        mid_l_indexes = left_col

        for row in range(self.cube_size):
            result += self.display_facelet_by_face(
                faces, faces_mask,
                'B', mid_b_indexes[row],
                adjacent=True,
            )

            result += self.display_face_row(
                faces, faces_mask, 'L', row,
            )
            result += self.display_spaces(1)
            result += self.display_face_row(
                faces, faces_mask, 'F', row,
            )
            result += self.display_spaces(1)
            result += self.display_face_row(
                faces, faces_mask, 'R', row,
            )
            result += self.display_face_row(
                faces, faces_mask, 'B', row,
            )

            result += self.display_facelet_by_face(
                faces, faces_mask,
                'L', mid_l_indexes[row],
                adjacent=True,
            )
            result += '\n'

        # Lower horizontal strip
        result += self.display_spaces(1)
        result += self.display_face_indexes(
            faces, faces_mask,
            'D', left_col[::-1],
            adjacent=True,
        )
        result += self.display_spaces(self.cube_size + 2)
        result += self.display_face_indexes(
            faces, faces_mask,
            'D', right_col + bottom_row[::-1],
            adjacent=True,
        )
        result += '\n'

        # Bottom section with D face
        bottom_l_indexes = bottom_row[::-1]
        bottom_r_indexes = bottom_row
        for row in range(self.cube_size):
            result += self.display_row_with_sides(
                faces, faces_mask, 'D',
                bottom_l_indexes, bottom_r_indexes,
                row, self.cube_size + 1,
                adjacent=True,
            )

        result += self.display_top_down_adjacent_facelets(
            faces[b_face_idx],
            faces_mask[b_face_idx],
            b_face_idx,
            top=False,
            end=True,
            spaces=self.cube_size + 2,
            break_line=True,
            adjacent=True,
        )

        return result

    def display_linear(self, faces: list[str],
                       faces_mask: list[str]) -> str:
        """
        Display facelets in a linear arrangement.

        Args:
            faces: List of face strings for all faces.
            faces_mask: List of mask strings for all faces.

        Returns:
            Formatted string showing facelets in linear rows.

        """
        result = ''

        for row in range(self.cube_size):
            result += ' '.join(
                self.display_face_row(faces, faces_mask, face, row)
                for face in FACE_ORDER
            )
            result += '\n'

        return result

    def position_based_effect(self, facelet_colors: str,
                              facelet_index: int) -> str:
        """
        Apply position-based visual effects to facelet colors.

        Args:
            facelet_colors: ANSI color code string to modify.
            facelet_index: Position index determining the effect to apply.

        Returns:
            Modified ANSI color code string with position-based effect applied.

        """
        matches = ANSI_TO_RGB.search(facelet_colors)

        if matches:
            groups = matches.groups()
            background_rgb = (int(groups[0]), int(groups[1]), int(groups[2]))
            foreground_rgb = (int(groups[3]), int(groups[4]), int(groups[5]))
        else:
            return facelet_colors

        assert self.effect is not None  # noqa: S101

        new_background_rgb, new_foreground_rgb = self.effect(
            background_rgb, foreground_rgb, facelet_index,
            self.cube_size,
        )

        return (
            f'\x1b[48;2;{ ";".join(str(c) for c in new_background_rgb) }m'
            f'\x1b[38;2;{ ";".join(str(c) for c in new_foreground_rgb) }m'
        )

    def letter_style_ansi(self, facelet_index: int,
                          face_color: str) -> tuple[str, str]:
        """
        Resolve ANSI letter style codes for a facelet position.

        Args:
            facelet_index: Global facelet index, or None if unknown.
            face_color: Current ANSI face color to restore after style reset.

        Returns:
            Tuple of (style_start, style_end) ANSI sequences.

        """
        piece_types = self.cube.get_facelet_piece_types(facelet_index)

        for piece_type in piece_types:
            style_ansi = self.style[piece_type]
            if style_ansi:
                return style_ansi, f'\x1b[0m{ face_color }'

        return '', ''
