import os
from typing import TYPE_CHECKING

from cubing_algs.constants import CROSS_MASK
from cubing_algs.constants import F2L_FACE_ORIENTATIONS
from cubing_algs.constants import F2L_FACES
from cubing_algs.constants import F2L_MASK
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OLL_MASK
from cubing_algs.constants import PLL_MASK

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube  # pragma: no cover

DEFAULT_COLORS = [
    'white', 'red', 'green',
    'yellow', 'orange', 'blue',
]

TERM_COLORS = {
    'reset': '\x1b[0;0m',
    'hide': '\x1b[48;5;238m\x1b[38;5;252m',
    'green': '\x1b[48;5;40m\x1b[38;5;232m',
    'blue': '\x1b[48;5;21m\x1b[38;5;230m',
    'red': '\x1b[48;5;196m\x1b[38;5;232m',
    'orange': '\x1b[48;5;208m\x1b[38;5;232m',
    'yellow': '\x1b[48;5;226m\x1b[38;5;232m',
    'white': '\x1b[48;5;254m\x1b[38;5;232m',
}

FACE_COLORS = dict(
    zip(FACE_ORDER, DEFAULT_COLORS, strict=True),
)

USE_COLORS = os.environ.get('TERM') == 'xterm-256color'


class VCubeDisplay:
    facelet_size = 3

    def __init__(self, cube: 'VCube'):
        self.cube = cube
        self.cube_size = cube.size
        self.face_size = self.cube_size * self.cube_size
        self.face_number = cube.face_number

    def compute_mask(self, cube: 'VCube', mask: str) -> str:
        if not mask:
            return '1' * (self.face_number * self.face_size)

        new_cube = cube.__class__(mask, check=False)

        moves = ' '.join(cube.history)

        if moves:
            new_cube.rotate(moves)

        return new_cube.state

    def split_faces(self, state: str) -> list[str]:
        return [
            state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(self.face_number)
        ]

    def display(self, mode: str = '', orientation: str = '') -> str:
        mask = ''
        display_method = self.display_cube
        default_orientation = ''

        # Only work for 3x3x3
        if mode == 'oll':
            mask = OLL_MASK
            display_method = self.display_top_face
            default_orientation = 'D'
        elif mode == 'pll':
            mask = PLL_MASK
            display_method = self.display_top_face
            default_orientation = 'D'
        elif mode == 'cross':
            mask = CROSS_MASK
            default_orientation = 'BU'
        elif mode == 'f2l':
            mask = F2L_MASK

            impacted_faces = ''
            for face in F2L_FACES:
                facelets = self.cube.get_face_by_center(face)
                exclusion_pattern = face * 6

                if (
                        not facelets.startswith(exclusion_pattern)
                        and not facelets.endswith(exclusion_pattern)
                ):
                    impacted_faces += face
            selected_front_face = F2L_FACE_ORIENTATIONS.get(
                impacted_faces, '',
            )

            default_orientation = f'D{ selected_front_face }'

        final_orientation = orientation or default_orientation
        if final_orientation:
            cube = self.cube.oriented_copy(final_orientation, full=True)
        else:
            cube = self.cube

        faces = self.split_faces(cube.state)
        masked_faces = self.split_faces(
            self.compute_mask(cube, mask),
        )

        return display_method(faces, masked_faces)

    @staticmethod
    def display_facelet(facelet: str, mask: str = '') -> str:
        face_color = 'hide' if mask == '0' else FACE_COLORS[facelet]

        if USE_COLORS:
            return (
                f'{ TERM_COLORS[face_color] }'
                f' { facelet } '
                f'{ TERM_COLORS["reset"] }'
            )
        return f' { facelet } '

    def display_top_down_face(self, face: str, face_mask: str) -> str:
        result = ''

        for index, facelet in enumerate(face):
            if index % self.cube_size == 0:
                result += (' ' * (self.facelet_size * self.cube_size))

            result += self.display_facelet(
                facelet,
                face_mask[index],
            )

            if index % self.cube_size == self.cube_size - 1:
                result += '\n'

        return result

    def display_top_down_adjacent_facelets(self, face: str, face_mask: str,
                                           *, top: bool = False) -> str:
        result = '   '
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
        middle = [
            faces[FACE_INDEXES['L']],
            faces[FACE_INDEXES['F']],
            faces[FACE_INDEXES['R']],
            faces[FACE_INDEXES['B']],
        ]
        middle_mask = [
            faces_mask[FACE_INDEXES['L']],
            faces_mask[FACE_INDEXES['F']],
            faces_mask[FACE_INDEXES['R']],
            faces_mask[FACE_INDEXES['B']],
        ]

        # Top
        result = self.display_top_down_face(
            faces[FACE_INDEXES['U']],
            faces_mask[FACE_INDEXES['U']],
        )

        # Middle
        for i in range(self.cube_size):
            for face, face_masked in zip(middle, middle_mask, strict=True):
                for j in range(self.cube_size):
                    result += self.display_facelet(
                        face[i * self.cube_size + j],
                        face_masked[i * self.cube_size + j],
                    )
            result += '\n'

        # Bottom
        result += self.display_top_down_face(
            faces[FACE_INDEXES['D']],
            faces_mask[FACE_INDEXES['D']],
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
