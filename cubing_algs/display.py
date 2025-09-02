import os
from typing import TYPE_CHECKING

from cubing_algs.constants import F2L_MASK
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import FULL_MASK
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

USE_COLORS = os.environ.get('TERM') == 'xterm-256color'


class VCubeDisplay:
    facelet_size = 3

    def __init__(self,
                 cube: 'VCube',
                 orientation: str = ''):
        self.cube = cube
        self.cube_size = cube.size
        self.face_size = self.cube_size * self.cube_size

        self.orientation = orientation

        self.face_colors = dict(
            zip(FACE_ORDER, DEFAULT_COLORS, strict=True),
        )

    def compute_mask(self, mask: str) -> str:
        if not mask:
            return FULL_MASK

        cube = self.cube.__class__(mask, check=False)

        moves = ' '.join(self.cube.history)

        if moves:
            cube.rotate(moves)

        return cube.state

    def split_faces(self, state: str) -> list[str]:
        return [
            state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(6)
        ]

    def display(self, mode: str = ''):
        cube = self.cube

        original_cube_state = cube.state
        original_cube_history = list(cube.history)

        if self.orientation:
            cube.rotate(self.orientation)

        faces = self.split_faces(cube.state)

        if mode == 'oll':
            display = self.display_yellow_face(
                faces, self.split_faces(self.compute_mask(OLL_MASK)),
            )
        elif mode == 'pll':
            display = self.display_yellow_face(
                faces, self.split_faces(self.compute_mask(PLL_MASK)),
            )
        elif mode == 'f2l':
            display = self.display_cube(
                faces, self.split_faces(self.compute_mask(F2L_MASK)),
            )
        else:
            display = self.display_cube(
                faces, self.split_faces(self.compute_mask(None)),
            )

        if self.orientation:
            cube._state = original_cube_state  # noqa: SLF001
            cube.history = original_cube_history

        return display

    def display_facelet(self, facelet: str, mask: str = '') -> str:
        face_color = 'hide' if mask == '0' else self.face_colors[facelet]

        if USE_COLORS:
            return (
                f'{ TERM_COLORS[face_color]}'
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
                                           *, top=False) -> str:
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
            faces[4], faces[2],
            faces[1], faces[5],
        ]
        middle_mask = [
            faces_mask[4], faces_mask[2],
            faces_mask[1], faces_mask[5],
        ]

        # Top
        result = self.display_top_down_face(faces[0], faces_mask[0])

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
        result += self.display_top_down_face(faces[3], faces_mask[3])

        return result

    def display_yellow_face(self, faces: list[str],
                            faces_mask: list[str]) -> str:
        """
        Because OLL/PLL maybe not on Down face,
        it's better to look for the yellow face wich is more a standard.
        """
        result = ''

        centers = self.cube.get_face_center_indexes()
        yellow_index = centers.index('D')
        red_index = centers.index('R')
        green_index = centers.index('F')
        blue_index = centers.index('B')
        orange_index = centers.index('L')

        # Top
        result = self.display_top_down_adjacent_facelets(
            faces[blue_index],
            faces_mask[blue_index],
            top=True,
        )

        # Middle
        for line in range(3):
            result += self.display_facelet(
                faces[red_index][line],
                faces_mask[red_index][line],
            )

            for i in range(3):
                result += self.display_facelet(
                    faces[yellow_index][line * 3 + i],
                    faces_mask[yellow_index][line * 3 + i],
                )

            result += self.display_facelet(
                faces[orange_index][2 - line],
                faces_mask[orange_index][2 - line],
            )

            result += '\n'

        # Bottom
        result += self.display_top_down_adjacent_facelets(
            faces[green_index],
            faces_mask[green_index],
            top=False,
        )

        return result
