from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import INITIAL_STATE
from cubing_algs.display import VCubeDisplay
from cubing_algs.extensions import rotate  # type: ignore[attr-defined]
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.integrity import VCubeIntegrityChecker
from cubing_algs.move import InvalidMoveError


class VCube(VCubeIntegrityChecker):
    """
    Virtual 3x3 cube for tracking moves on facelets
    """
    size = 3
    face_number = 6
    face_size = size * size

    def __init__(self, initial: str | None = None, *, check: bool = True):
        if initial:
            self._state = initial
            if check:
                self.check_integrity()
        else:
            self._state = INITIAL_STATE

        self.history: list[str] = []

    @property
    def state(self) -> str:
        return self._state

    @staticmethod
    def from_cubies(cp: list[int], co: list[int],
                    ep: list[int], eo: list[int],
                    so: list[int]) -> 'VCube':
        return VCube(cubies_to_facelets(cp, co, ep, eo, so))

    @property
    def to_cubies(self) -> tuple[
            list[int], list[int], list[int], list[int], list[int],
    ]:
        return facelets_to_cubies(self._state)

    @property
    def is_solved(self) -> bool:
        return all(face * self.face_size in self.state for face in FACE_ORDER)

    def rotate(self, moves: str | Algorithm) -> str:
        if isinstance(moves, Algorithm):
            for m in moves:
                self.rotate_move(str(m))
        else:
            for m in moves.split(' '):
                self.rotate_move(m)
        return self._state

    def rotate_move(self, move: str) -> str:
        try:
            self._state = rotate.rotate_move(self._state, move)
        except ValueError as e:
            raise InvalidMoveError(str(e)) from e
        else:
            self.history.append(move)
            return self._state

    def display(self, orientation: str = '',
                mode: str = '') -> str:
        return VCubeDisplay(self, orientation).display(mode)

    def show(self, orientation: str = '',
             mode: str = '') -> None:
        print(self.display(orientation, mode), end='')

    def get_face(self, face: str):
        index = FACE_ORDER.index(face)
        return self._state[index * self.face_size: (index + 1) * self.face_size]

    def get_face_center_indexes(self) -> list[str]:
        face_centers = []

        for i in range(6):
            face_centers.append(self.state[(i * self.face_size) + 4])

        return face_centers

    def get_face_index(self, face: str) -> int:
        return self.get_face_center_indexes().index(face)

    def get_face_by_center(self, face: str):
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
