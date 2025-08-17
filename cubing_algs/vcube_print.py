import os
from typing import TYPE_CHECKING

from cubing_algs.constants import FACE_ORDER

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube  # pragma: no cover

DEFAULT_COLORS = [
    'white', 'red', 'green',
    'yellow', 'orange', 'blue',
]

TERM_COLORS = {
    'reset': '\x1b[0;0m',
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

    def format_color(self, facelet: str) -> str:
        if USE_COLORS:
            return (
                f'{ TERM_COLORS[self.face_colors[facelet]]}'
                f' { facelet } '
                f'{ TERM_COLORS["reset"] }'
            )
        return f' { facelet } '

    def print_top_down_face(self, face: str) -> str:
        result = ''

        for index, facelet in enumerate(face):
            if index % self.cube_size == 0:
                result += (' ' * (self.facelet_size * self.cube_size))

            result += self.format_color(facelet)

            if index % self.cube_size == self.cube_size - 1:
                result += '\n'

        return result

    def print_cube(self) -> str:
        cube = self.cube

        original_cube_state = cube.state
        original_cube_history = list(cube.history)

        if self.orientation:
            cube.rotate(self.orientation)

        cube_state = cube.state

        faces = [
            cube_state[i * self.face_size: (i + 1) * self.face_size]
            for i in range(6)
        ]

        middle = [faces[4], faces[2], faces[1], faces[5]]

        # Top
        result = self.print_top_down_face(faces[0])

        # Middle
        for i in range(self.cube_size):
            for face in middle:
                for j in range(self.cube_size):
                    result += self.format_color(
                        face[i * self.cube_size + j],
                    )
            result += '\n'

        # Bottom
        result += self.print_top_down_face(faces[3])

        if self.orientation:
            cube._state = original_cube_state  # noqa: SLF001
            cube.history = original_cube_history

        return result
