import os
import re
from typing import TYPE_CHECKING

from cubing_algs.constants import F2L_ADJACENT_FACES
from cubing_algs.constants import F2L_FACE_ORIENTATIONS
from cubing_algs.constants import F2L_FACES
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.effects import load_effect
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.masks import CROSS_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import OLL_MASK
from cubing_algs.masks import PLL_MASK
from cubing_algs.palettes import build_ansi_color
from cubing_algs.palettes import load_palette

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube  # pragma: no cover

USE_COLORS = os.environ.get('TERM') == 'xterm-256color'

DEFAULT_EFFECT = os.getenv('CUBING_ALGS_EFFECT', '')
DEFAULT_PALETTE = os.getenv('CUBING_ALGS_PALETTE', 'default')

ANSI_TO_RGB = re.compile(
    r'\x1b\[48;2;(\d+);(\d+);(\d+)m\x1b\[38;2;(\d+);(\d+);(\d+)m',
)


class VCubeDisplay:
    """
    Handle visual representation and display formatting for virtual cubes.

    Provides methods to render cube states with different display modes,
    color palettes, and visual effects for terminal output.
    """
    facelet_size = 3

    def __init__(self, cube: 'VCube',
                 palette_name: str = '', effect_name: str = '') -> None:
        """Initialize display handler with cube instance and visual settings."""
        self.cube = cube
        self.cube_size: int = cube.size
        self.face_size: int = self.cube_size * self.cube_size
        self.face_number: int = cube.face_number

        self.effect_name = (effect_name or DEFAULT_EFFECT).lower()
        self.palette_name = (palette_name or DEFAULT_PALETTE).lower()

        self.palette = load_palette(self.palette_name)
        self.effect = load_effect(self.effect_name, self.palette_name)

    def compute_mask(self, cube: 'VCube', mask: str) -> str:
        """Convert mask string to facelets format for display filtering."""
        if not mask:
            return '1' * (self.face_number * self.face_size)

        return cubies_to_facelets(
            *facelets_to_cubies(cube.state),
            mask,
        )

    def compute_f2l_front_face(self) -> str:
        """Determine the optimal front face orientation for F2L display mode."""
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
        """Split cube state string into individual face strings."""
        return [
            state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(self.face_number)
        ]

    def display(self, mode: str = '', orientation: str = '',
                mask: str = '') -> str:
        """Generate formatted visual representation of the cube state."""
        mode_mask = ''
        display_method = self.display_cube
        default_orientation = ''

        # Only work for 3x3x3
        if mode == 'oll':
            mode_mask = OLL_MASK
            display_method = self.display_top_face
            default_orientation = 'D'
        elif mode == 'pll':
            mode_mask = PLL_MASK
            display_method = self.display_top_face
            default_orientation = 'D'
        elif mode == 'cross':
            mode_mask = CROSS_MASK
            default_orientation = 'FU'
        elif mode in {'f2l', 'af2l'}:
            mode_mask = F2L_MASK
            default_orientation = f'D{ self.compute_f2l_front_face() }'
        elif mode == 'extended':
            display_method = self.display_extended_net

        final_orientation = orientation or default_orientation
        if final_orientation:
            cube = self.cube.oriented_copy(final_orientation, full=True)
        else:
            cube = self.cube

        faces = self.split_faces(cube.state)
        masked_faces = self.split_faces(
            self.compute_mask(cube, mask or mode_mask),
        )

        return display_method(faces, masked_faces)

    def display_spaces(self, count):
        """Generate a string of spaces for display formatting."""
        return ' ' * (self.facelet_size * count)

    def display_facelet(self, facelet: str, mask: str = '',
                        facelet_index: int | None = None) -> str:
        """Format a single facelet with colors and effects for display."""
        if facelet not in FACE_ORDER:
            face_color = self.palette['masked']
        else:
            face_key = facelet
            if mask == '0':
                face_key += '_hidden'
            face_color = self.palette[face_key]

        if self.effect and facelet_index is not None:
            face_color = self.position_based_effect(
                face_color, facelet_index,
            )

        if USE_COLORS:
            return (
                f'{ face_color }'
                f' { facelet } '
                f'{ self.palette["reset"] }'
            )

        return f' { facelet } '

    def display_face_row(self, faces: list[str], faces_mask: list[str],
                         face_key: str, row: int) -> str:
        """Display a complete row of a face."""
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
                                face_key: str, index: int) -> str:
        """Display a specific facelet from a face using face key and index."""
        face_idx = FACE_INDEXES[face_key]

        return self.display_facelet(
            faces[face_idx][index],
            faces_mask[face_idx][index],
            (face_idx * self.face_size) + index,
        )

    def display_face_indexes(self, faces: list[str], faces_mask: list[str],
                             face_key: str, indexes: list[int]) -> str:
        """Display multiple facelets from a face using specified indexes."""
        return ''.join(
            self.display_facelet_by_face(
                faces, faces_mask,
                face_key, idx,
            )
            for idx in indexes
        )

    def display_row_with_sides(self, faces: list[str], faces_mask: list[str],  # noqa: PLR0913 PLR0917
                               center_face: str,
                               left_indexes: list[int],
                               right_indexes: list[int],
                               row: int,
                               leading_spaces: int = 0) -> str:
        """Display a row with center face and adjacent side facelets."""
        row_result = self.display_spaces(leading_spaces)
        row_result += self.display_facelet_by_face(
            faces, faces_mask,
            'L', left_indexes[row],
        )

        row_result += self.display_face_row(
            faces, faces_mask,
            center_face, row,
        )

        row_result += self.display_facelet_by_face(
            faces, faces_mask,
            'R', right_indexes[row],
        )
        row_result += '\n'

        return row_result

    def display_top_down_face(self, face: str, face_mask: str,
                              face_index: int) -> str:
        """Display a complete face in top-down view with proper spacing."""
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
                                           break_line: bool = True) -> str:
        """Display adjacent facelets in a linear arrangement."""
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
            )

        if break_line:
            result += '\n'

        return result

    def display_cube(self, faces: list[str], faces_mask: list[str]) -> str:
        """Display cube in standard unfolded net layout."""
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
        """Display only the top face with surrounding adjacent facelets."""
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
        )

        # Middle
        for line in range(self.cube_size):
            result += self.display_spaces(self.cube_size - 1)

            left_adjacent_index = FACE_INDEXES['L']
            result += self.display_facelet(
                faces[left_adjacent_index][line],
                faces_mask[left_adjacent_index][line],
                (left_adjacent_index * self.face_size) + line,
            )

            middle_index = FACE_INDEXES['U']
            for col_index in range(self.cube_size):
                index = (line * self.cube_size) + col_index
                result += self.display_facelet(
                    faces[middle_index][index],
                    faces_mask[middle_index][index],
                    (middle_index * self.face_size) + index,
                )

            right_adjacent_index = FACE_INDEXES['R']
            col_index = self.cube_size - 1 - line
            result += self.display_facelet(
                faces[right_adjacent_index][col_index],
                faces_mask[right_adjacent_index][col_index],
                (right_adjacent_index * self.face_size) + col_index,
            )

            result += '\n'

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
        )

        return result

    def display_extended_net(self, faces: list[str],
                             faces_mask: list[str]) -> str:
        """Display cube as an extended net layout."""
        b_face_idx = FACE_INDEXES['B']

        # Top section with U face
        result = self.display_top_down_adjacent_facelets(
            faces[b_face_idx],
            faces_mask[b_face_idx],
            b_face_idx,
            top=True,
            end=False,
            spaces=self.cube_size + 2,
            break_line=True,
        )

        top_l_indexes = [0, 1, 2]
        top_r_indexes = [2, 1, 0]
        for row in range(self.cube_size):
            result += self.display_row_with_sides(
                faces, faces_mask, 'U',
                top_l_indexes, top_r_indexes,
                row, self.cube_size + 1,
            )

        # Upper horizontal strip
        result += self.display_spaces(1)
        result += self.display_face_indexes(
            faces, faces_mask,
            'U', [0, 3, 6],
        )
        result += self.display_spaces(self.cube_size + 2)
        result += self.display_face_indexes(
            faces, faces_mask,
            'U', [8, 5, 2, 2, 1, 0],
        )
        result += '\n'

        # Central section with L F R B faces
        mid_b_indexes = [2, 5, 8]
        mid_l_indexes = [0, 3, 6]

        for row in range(self.cube_size):
            result += self.display_facelet_by_face(
                faces, faces_mask,
                'B', mid_b_indexes[row],
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
            )
            result += '\n'

        # Lower horizontal strip
        result += self.display_spaces(1)
        result += self.display_face_indexes(
            faces, faces_mask,
            'D', [6, 3, 0],
        )
        result += self.display_spaces(self.cube_size + 2)
        result += self.display_face_indexes(
            faces, faces_mask,
            'D', [2, 5, 8, 8, 7, 6],
        )
        result += '\n'

        # Bottom section with D face
        bottom_l_indexes = [8, 7, 6]
        bottom_r_indexes = [6, 7, 8]
        for row in range(self.cube_size):
            result += self.display_row_with_sides(
                faces, faces_mask, 'D',
                bottom_l_indexes, bottom_r_indexes,
                row, self.cube_size + 1,
            )

        result += self.display_top_down_adjacent_facelets(
            faces[b_face_idx],
            faces_mask[b_face_idx],
            b_face_idx,
            top=False,
            end=True,
            spaces=self.cube_size + 2,
            break_line=True,
        )

        return result

    def position_based_effect(self, facelet_colors: str,
                              facelet_index: int) -> str:
        """Apply position-based visual effects to facelet colors."""
        matches = ANSI_TO_RGB.search(facelet_colors)

        if matches:
            background_rgb = tuple(int(c) for c in matches.groups()[0:3])
            foreground_rgb = tuple(int(c) for c in matches.groups()[3:6])

        new_background_rgb = self.effect(
            background_rgb, facelet_index,
            self.cube_size,
        )

        return build_ansi_color(
            new_background_rgb,
            foreground_rgb,
        )
