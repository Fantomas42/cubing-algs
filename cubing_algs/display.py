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

ANSI_TO_RGB = re.compile(
    r'\x1b\[48;2;(\d+);(\d+);(\d+)m\x1b\[38;2;(\d+);(\d+);(\d+)m',
)


class VCubeDisplay:
    facelet_size = 3

    def __init__(self, cube: 'VCube',
                 palette_name: str = '', effect_name: str = ''):
        self.cube = cube
        self.cube_size = cube.size
        self.face_size = self.cube_size * self.cube_size
        self.face_number = cube.face_number

        self.palette = load_palette(palette_name)
        self.effect = load_effect(effect_name, palette_name)

    def compute_mask(self, cube: 'VCube', mask: str) -> str:
        if not mask:
            return '1' * (self.face_number * self.face_size)

        return cubies_to_facelets(
            *facelets_to_cubies(cube.state),
            mask,
        )

    def compute_f2l_front_face(self) -> str:
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
        return [
            state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(self.face_number)
        ]

    def display(self, mode: str = '', orientation: str = '',
                mask: str = '') -> str:
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

    def display_facelet(self, facelet: str, mask: str = '',
                        facelet_index: int | None = None) -> str:
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

    def display_top_down_face(self, face: str, face_mask: str,
                              face_index: int) -> str:
        result = ''

        for index, facelet in enumerate(face):
            if index % self.cube_size == 0:
                result += (' ' * (self.facelet_size * self.cube_size))

            result += self.display_facelet(
                facelet,
                face_mask[index],
                (face_index * self.face_size) + index,
            )

            if index % self.cube_size == self.cube_size - 1:
                result += '\n'

        return result

    def display_top_down_adjacent_facelets(self, face: str, face_mask: str,
                                           *, top: bool = False) -> str:
        result = ' ' * (self.facelet_size * self.cube_size)
        facelets = face[:3]
        facelets_mask = face_mask[:3]

        if top:
            facelets = facelets[::-1]
            facelets_mask = facelets_mask[::-1]

        for index, facelet in enumerate(facelets):
            result += self.display_facelet(
                facelet,
                facelets_mask[index],
            )

        result += '\n'

        return result

    def display_cube(self, faces: list[str], faces_mask: list[str]) -> str:
        middle_face_indexes = [
            FACE_INDEXES['L'],
            FACE_INDEXES['F'],
            FACE_INDEXES['R'],
            FACE_INDEXES['B'],
        ]
        middle_faces = [
            faces[index]
            for index in middle_face_indexes
        ]
        middle_masks = [
            faces_mask[index]
            for index in middle_face_indexes
        ]

        # Top
        top_face_index = FACE_INDEXES['U']
        result = self.display_top_down_face(
            faces[top_face_index],
            faces_mask[top_face_index],
            top_face_index,
        )

        # Middle
        for i in range(self.cube_size):
            for face, face_masked, middle_index in zip(
                    middle_faces, middle_masks, middle_face_indexes,
                    strict=True,
            ):
                for j in range(self.cube_size):
                    facelet_index = (i * self.cube_size) + j

                    result += self.display_facelet(
                        face[facelet_index],
                        face_masked[facelet_index],
                        (middle_index * self.face_size) + facelet_index,
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
        result = ''

        # Top
        result = self.display_top_down_adjacent_facelets(
            faces[FACE_INDEXES['B']],
            faces_mask[FACE_INDEXES['B']],
            top=True,
        )

        # Middle
        for line in range(3):
            result += ' ' * (self.facelet_size * (self.cube_size - 1))

            result += self.display_facelet(
                faces[FACE_INDEXES['L']][line],
                faces_mask[FACE_INDEXES['L']][line],
            )

            for i in range(3):
                result += self.display_facelet(
                    faces[FACE_INDEXES['U']][line * 3 + i],
                    faces_mask[FACE_INDEXES['U']][line * 3 + i],
                )

            result += self.display_facelet(
                faces[FACE_INDEXES['R']][2 - line],
                faces_mask[FACE_INDEXES['R']][2 - line],
            )

            result += '\n'

        # Bottom
        result += self.display_top_down_adjacent_facelets(
            faces[FACE_INDEXES['F']],
            faces_mask[FACE_INDEXES['F']],
            top=False,
        )

        return result

    def position_based_effect(self, facelet_colors, facelet_index) -> str:
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
