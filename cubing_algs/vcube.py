"""Virtual cube implementation for simulating moves and tracking state."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.display import VCubeDisplay
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.extensions import rotate
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.initial_state import get_initial_state
from cubing_algs.integrity import VCubeIntegrityChecker
from cubing_algs.move import Move
from cubing_algs.rotate_dynamic import rotate_move as rotate_dynamic
from cubing_algs.visual_cube import visual_cube_cube


class VCube(VCubeIntegrityChecker):  # noqa: PLR0904
    """
    Virtual cube for tracking moves on facelets.

    Represents a Rubik's cube state using a facelet string where each
    character represents a facelet color.

    Supports arbitrary cube sizes:
    - 2x2x2: 24-character string (6 faces * 4 facelets)
    - 3x3x3: 54-character string (6 faces * 9 facelets)
    - NxNxN: 6*N*N-character string
    """

    face_number: int = 6

    def __init__(self, initial: str | None = None, *,
                 size: int = 3,
                 check: bool = True,
                 history: list[str] | None = None) -> None:
        """
        Initialize a virtual cube with optional initial state and history.

        Args:
            initial: Optional initial state string. If None, uses solved state.
            size: Size of the cube. Default is 3.
              (2 for 2x2x2, 3 for 3x3x3, etc.).
            check: Whether to check cube integrity on initialization.
            history: Optional move history to restore.

        """
        self.size = size
        self.face_size = size * size

        if initial:
            self._state = initial
            if check:
                self.check_integrity()
        else:
            self._state = get_initial_state(size)

        self.history: list[str] = history or []

    @property
    def state(self) -> str:
        """Get the current state of the cube as a facelet string."""
        return self._state

    @property
    def has_fixed_centers(self) -> bool:
        """Check if the cube has fixed centers."""
        return bool(self.size % 2)

    @property
    def center_index(self) -> int:
        """
        Return the center index.

        Does not work for even cube size.
        """
        return self.face_size // 2

    @staticmethod
    def from_cubies(cp: list[int], co: list[int],  # noqa: PLR0913 PLR0917
                    ep: list[int], eo: list[int],
                    so: list[int],
                    scheme: str | None = None) -> 'VCube':
        """
        Create a VCube from cubie representation.

        Args:
            cp: Corner permutation array.
            co: Corner orientation array.
            ep: Edge permutation array.
            eo: Edge orientation array.
            so: Center orientation array.
            scheme: Optional color scheme to use.

        Returns:
            A new VCube with the specified cubie configuration.

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

        Returns:
            A tuple of (corner_permutation, corner_orientation,
            edge_permutation, edge_orientation, center_orientation).

        """
        return facelets_to_cubies(self._state)

    @property
    def is_solved(self) -> bool:
        """Check if the cube is in a solved state."""
        return all(face * self.face_size in self.state for face in FACE_ORDER)

    def is_equal(self, other_cube: 'VCube', *, strict: bool = True) -> bool:
        """
        Compare two cubes for equality with optional orientation flexibility.

        In strict mode, compares exact facelet states.
        In non-strict mode, reorients the other cube to match
        this cube's orientation before comparing.

        Args:
            other_cube: The cube to compare against.
            strict: If True, compare exact states; if False, allow
                orientation differences.

        Returns:
            True if the cubes are equal according to the comparison mode.

        """
        if strict:
            return self.state == other_cube.state

        oriented_copy = other_cube.oriented_copy(self.orientation)

        return self.state == oriented_copy.state

    @property
    def orientation(self) -> str:
        """
        Get the cube's orientation as a two-character string.

        Uses the top face center and front face center
        to determine the current orientation of the cube in space.

        It might not work well with an unchecked state.

        Raises:
            NotImplementedError: If the cube size is not handled

        """
        if not self.has_fixed_centers:
            msg = 'Cannot compute orientation for cube even size.'
            raise NotImplementedError(msg)

        top_center_index = self.center_index
        front_center_index = 2 * self.face_size + top_center_index

        return self._state[top_center_index] + self._state[front_center_index]

    def rotate(self, moves: Algorithm | Move | str, *,
               history: bool = True) -> str:
        """
        Apply a sequence of moves to the cube.

        Args:
            moves: The moves to apply to the cube.
            history: If True, record moves in the cube's history.

        Returns:
            The new state of the cube after applying the moves.

        """
        moves_str = str(moves)

        if not moves_str:
            return self._state

        for move in moves_str.split(' '):
            self.rotate_move(move, history=history)

        return self._state

    def rotate_move(self, move: str, *, history: bool = True) -> str:
        """
        Apply a single move to the cube.

        Args:
            move: The move string to apply.
            history: If True, record the move in the cube's history.

        Returns:
            The new state of the cube after applying the move.

        Raises:
            InvalidMoveError: If the move is invalid.

        """
        try:
            # Use C extension for 3x3x3, Python for other sizes
            if self.size == 3:
                self._state = rotate.rotate_move(self._state, move)
            else:
                self._state = rotate_dynamic(self._state, move, size=self.size)
        except ValueError as e:
            raise InvalidMoveError(str(e)) from e
        else:
            if history:
                self.history.append(move)
            return self._state

    def copy(self, *, full: bool = False) -> 'VCube':
        """
        Create a copy of the cube with optional history preservation.

        Args:
            full: If True, copy the move history as well.

        Returns:
            A new VCube instance with the same state.

        """
        history = None
        if full:
            history = list(self.history)

        return VCube(
            self.state,
            size=self.size,
            check=False,
            history=history,
        )

    def compute_orientation_moves(self, faces: str) -> str:
        """
        Calculate the moves needed to orient the cube to specific faces.

        Args:
            faces: A string specifying the desired face orientation
                (e.g., 'UF').

        Returns:
            A string of moves needed to achieve the desired orientation.

        """
        top_face, front_face = self.check_face_orientations(faces)

        orientation_key = str(self.get_face_index(top_face))

        if front_face:
            orientation_key += str(self.get_face_index(front_face))

        return OFFSET_ORIENTATION_MAP[orientation_key]

    def oriented_copy(self, faces: str, *, full: bool = False) -> 'VCube':
        """
        Create a copy of the cube oriented to specific faces.

        Args:
            faces: The desired face orientation (e.g., 'UF').
            full: If True, copy the move history as well.

        Returns:
            A new VCube instance oriented to the specified faces.

        """
        cube = self.copy(full=full)

        moves = self.compute_orientation_moves(faces)

        if moves:
            cube.rotate(moves, history=full)

        return cube

    def display(self, mode: str = '', orientation: str = '',  # noqa: PLR0913 PLR0917
                mask: str = '', palette: str = '',
                effect: str = '', facelet: str = '') -> str:
        """
        Generate a visual representation of the cube.

        Args:
            mode: Display mode for the visualization.
            orientation: Desired orientation for display.
            mask: Mask to apply to the display.
            palette: Color palette to use.
            effect: Visual effect to apply.
            facelet: Facelet mode for display.

        Returns:
            A string containing the visual representation of the cube.

        """
        return VCubeDisplay(self, palette, effect, facelet).display(
            mode, orientation, mask,
        )

    def show(self, mode: str = '', orientation: str = '',  # noqa: PLR0913 PLR0917
             mask: str = '', palette: str = '',
             effect: str = '', facelet: str = '') -> None:
        """Print a visual representation of the cube."""
        print(  # noqa: T201
            self.display(
                mode, orientation, mask,
                palette, effect, facelet,
            ),
            end='',
        )

    def get_face(self, face: str) -> str:
        """
        Get the facelets of a specific face by face letter.

        Args:
            face: The face letter (e.g., 'U', 'F', 'R').

        Returns:
            A string of 9 characters representing the facelets on that face.

        """
        index = FACE_INDEXES[face]
        return self._state[index * self.face_size: (index + 1) * self.face_size]

    def get_face_center_indexes(self) -> list[str]:
        """
        Get the center facelet colors for all faces.

        Returns:
            A list of center colors for all six faces in order.

        Raises:
            NotImplementedError: If the cube size is not handled

        """
        if not self.has_fixed_centers:
            msg = 'Cannot compute center indexes for cube even size.'
            raise NotImplementedError(msg)

        center_index = self.center_index

        return [self.state[(i * self.face_size) + center_index] for i in range(6)]

    def get_face_index(self, face: str) -> int:
        """
        Get the index of a face by its center color.

        Args:
            face: The center color of the face to find.

        Returns:
            The index (0-5) of the face with that center color.

        """
        return self.get_face_center_indexes().index(face)

    def get_face_by_center(self, face: str) -> str:
        """
        Get the facelets of a face by its center color.

        Args:
            face: The center color to search for.

        Returns:
            A string of 9 characters representing the facelets on that face.

        """
        index = self.get_face_index(face)

        return self._state[index * self.face_size: (index + 1) * self.face_size]

    @property
    def visual_cube_url(self) -> str:
        """Get a VisualCube URL for this cube state."""
        return visual_cube_cube(self)

    def __str__(self) -> str:
        """
        Return the facelets of the cube.

        Returns:
            A multi-line string showing each face and its facelets.

        """
        faces = [f'{ face }: { self.get_face(face)}' for face in FACE_ORDER]

        return '\n'.join(faces)

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the VCube.

        Returns:
            A Python expression that can recreate this VCube object.

        """
        return f"VCube('{ self._state }')"
