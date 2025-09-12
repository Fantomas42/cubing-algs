from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import INITIAL_STATE
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.display import VCubeDisplay
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.extensions import rotate  # type: ignore[attr-defined]
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.integrity import VCubeIntegrityChecker


class VCube(VCubeIntegrityChecker):
    """
    Virtual 3x3 cube for tracking moves on facelets.

    Represents a Rubik's cube state using a 54-character string
    where each character represents a facelet color.
    """
    size = 3
    face_number = 6
    face_size = size * size

    def __init__(self, initial: str | None = None, *,
                 check: bool = True,
                 history: list[str] | None = None):
        """
        Initialize a virtual cube with optional initial state and history.
        """
        if initial:
            self._state = initial
            if check:
                self.check_integrity()
        else:
            self._state = INITIAL_STATE

        self.history: list[str] = history or []

    @property
    def state(self) -> str:
        """
        Get the current state of the cube as a facelet string.
        """
        return self._state

    @staticmethod
    def from_cubies(cp: list[int], co: list[int],  # noqa: PLR0913 PLR0917
                    ep: list[int], eo: list[int],
                    so: list[int],
                    scheme: str | None = None) -> 'VCube':
        """
        Create a VCube from cubie representation.
        """
        return VCube(
            cubies_to_facelets(cp, co, ep, eo, so, scheme),
            check=not bool(scheme),
        )

    @property
    def to_cubies(self) -> tuple[
            list[int], list[int], list[int], list[int], list[int],
    ]:
        """
        Convert the cube state to cubie representation.
        """
        return facelets_to_cubies(self._state)

    @property
    def is_solved(self) -> bool:
        """
        Check if the cube is in a solved state.
        """
        return all(face * self.face_size in self.state for face in FACE_ORDER)

    def rotate(self, moves: str | Algorithm, *, history: bool = True) -> str:
        """
        Apply a sequence of moves to the cube.
        """
        if isinstance(moves, Algorithm):
            for m in moves:
                self.rotate_move(str(m), history=history)
        else:
            for m in moves.split(' '):
                self.rotate_move(m, history=history)
        return self._state

    def rotate_move(self, move: str, *, history: bool = True) -> str:
        """
        Apply a single move to the cube.
        """
        try:
            self._state = rotate.rotate_move(self._state, move)
        except ValueError as e:
            raise InvalidMoveError(str(e)) from e
        else:
            if history:
                self.history.append(move)
            return self._state

    def copy(self, *, full: bool = False) -> 'VCube':
        """
        Create a copy of the cube with optional history preservation.
        """
        history = None
        if full:
            history = list(self.history)

        return VCube(
            self.state,
            check=False,
            history=history,
        )

    def compute_orientation_moves(self, faces: str) -> str:
        """
        Calculate the moves needed to orient the cube to specific faces.
        """
        top_face, front_face = self.check_face_orientations(faces)

        orientation_key = str(self.get_face_index(top_face))

        if front_face:
            orientation_key += str(self.get_face_index(front_face))

        return OFFSET_ORIENTATION_MAP[orientation_key]

    def oriented_copy(self, faces: str, *, full: bool = False) -> 'VCube':
        """
        Create a copy of the cube oriented to specific faces.
        """
        cube = self.copy(full=full)

        moves = self.compute_orientation_moves(faces)

        if moves:
            cube.rotate(moves, history=full)

        return cube

    def display(self, mode: str = '', orientation: str = '',
                mask: str = '') -> str:
        """
        Generate a visual representation of the cube.
        """
        return VCubeDisplay(self).display(mode, orientation, mask)

    def show(self, mode: str = '', orientation: str = '',
             mask: str = '') -> None:
        """
        Print a visual representation of the cube.
        """
        print(self.display(mode, orientation, mask), end='')

    def get_face(self, face: str) -> str:
        """
        Get the facelets of a specific face by face letter.
        """
        index = FACE_INDEXES[face]
        return self._state[index * self.face_size: (index + 1) * self.face_size]

    def get_face_center_indexes(self) -> list[str]:
        """
        Get the center facelet colors for all faces.
        """
        face_centers = []

        for i in range(6):
            face_centers.append(self.state[(i * self.face_size) + 4])

        return face_centers

    def get_face_index(self, face: str) -> int:
        """
        Get the index of a face by its center color.
        """
        return self.get_face_center_indexes().index(face)

    def get_face_by_center(self, face: str) -> str:
        """
        Get the facelets of a face by its center color.
        """
        index = self.get_face_index(face)

        return self._state[index * self.face_size: (index + 1) * self.face_size]

    def __str__(self) -> str:
        """
        Return the facelets of the cube
        """
        faces = []
        for face in FACE_ORDER:
            faces.append(f'{ face }: { self.get_face(face)}')

        return '\n'.join(faces)

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the VCube.
        """
        return f"VCube('{ self._state }')"
