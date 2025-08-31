import os
from typing import TYPE_CHECKING

from cubing_algs.constants import F2L_MASK
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import FULL_MASK

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube  # pragma: no cover

DEFAULT_COLORS = [
    'white', 'red', 'green',
    'yellow', 'orange', 'blue',
]

TERM_COLORS = {
    'reset': '\x1b[0;0m',
    'hide': '\x1b[48;5;240m\x1b[38;5;252m',
    'green': '\x1b[48;5;40m\x1b[38;5;232m',
    'blue': '\x1b[48;5;21m\x1b[38;5;230m',
    'red': '\x1b[48;5;196m\x1b[38;5;232m',
    'orange': '\x1b[48;5;208m\x1b[38;5;232m',
    'yellow': '\x1b[48;5;226m\x1b[38;5;232m',
    'white': '\x1b[48;5;254m\x1b[38;5;232m',
}

USE_COLORS = os.environ.get('TERM') == 'xterm-256color'


class VCubePrinter:
    facelet_size = 3

    def __init__(self,
                 cube: 'VCube',
                 orientation: str = '',
                 colors: list[str] | None = None):
        self.cube = cube
        self.cube_size = cube.size
        self.face_size = self.cube_size * self.cube_size

        self.orientation = orientation
        self.colors = colors or DEFAULT_COLORS

        self.face_colors = dict(
            zip(FACE_ORDER, self.colors, strict=True),
        )

    def compute_mask(self, mask):
        if not mask:
            return FULL_MASK

        cube = self.cube.__class__(mask, check=False)

        moves = ' '.join(self.cube.history)

        if moves:
            cube.rotate(moves)

        return cube.state

    def display(self, mode: str = ''):
        if mode == 'oll':
            return self.display_face()
        if mode == 'pll':
            return self.display_face()
        if mode == 'f2l':
            return self.display_cube(F2L_MASK)

        return self.display_cube()

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

    def display_cube(self, mask: str = '') -> str:
        cube = self.cube

        original_cube_state = cube.state
        original_cube_history = list(cube.history)

        if self.orientation:
            cube.rotate(self.orientation)

        cube_state = cube.state
        cube_mask = self.compute_mask(mask)

        faces = [
            cube_state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(6)
        ]
        faces_mask = [
            cube_mask[i * self.face_size: (i + 1) * self.face_size]
            for i in range(6)
        ]

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

        if self.orientation:
            cube._state = original_cube_state  # noqa: SLF001
            cube.history = original_cube_history

        return result

    def display_face(self, mask: str = '') -> str:
        ...
