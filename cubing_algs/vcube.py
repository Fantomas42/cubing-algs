"""Virtual cube implementation for simulating moves and tracking state."""
from functools import cached_property

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import FaceletPieceType
from cubing_algs.annotations import Mask
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.display.vcube import VCubeDisplay
from cubing_algs.exceptions import InvalidCubeSizeError
from cubing_algs.exceptions import InvalidFaceIndexError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.exceptions import InvalidOrientationError
from cubing_algs.exceptions import NotSupportedCubeSizeError
from cubing_algs.extensions import rotate_2x2x2
from cubing_algs.extensions import rotate_3x3x3
from cubing_algs.extensions import rotate_dynamic
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.integrity import VCubeIntegrityChecker
from cubing_algs.move import Move
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3
from cubing_algs.solved_state import get_solved_facelets
from cubing_algs.solver import facelets_to_facelets_algorithm


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

    face_number: int = FACE_NUMBER

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

        Raises:
            InvalidCubeSizeError: If size <= 0

        """
        self.size = size
        self.face_size = size * size

        if size <= 0:
            msg = f'Cube size must be positive, got {size}'
            raise InvalidCubeSizeError(msg)

        if initial:
            self._state = initial
            if check:
                self.check_integrity()
        elif size == 3:
            self._state = SOLVED_FACELETS_3x3x3
        else:
            self._state = get_solved_facelets(size)

        self.history: list[str] = history or []

    @property
    def state(self) -> str:
        """Get the current state of the cube as a facelet string."""
        return self._state

    @cached_property
    def has_fixed_centers(self) -> bool:
        """Check if the cube has fixed centers."""
        return bool(self.size % 2)

    @cached_property
    def center_index(self) -> int:
        """
        Return the center index for a face.

        For odd-sized cubes (3x3x3, 5x5x5, etc.), returns the index of the
        physical center facelet. For 2x2x2, returns 0 (top-left position).
        For other even-sized cubes (4x4x4, 6x6x6, etc.), returns a virtual
        center position calculated as face_size + 1, alias the top-left
        piece of a virtual center.

        Returns:
            The index of the center position within a face.

        """
        if self.has_fixed_centers:
            return self.face_size // 2
        if self.size == 2:
            return 0
        return self.size + 1

    @cached_property
    def facelet_piece_types(self) -> dict[int, list[FaceletPieceType]]:
        """
        Get the piece types for every facelet index on the cube.

        Each value is a list ordered from most specific to least specific,
        e.g. ['midge', 'edge'] or ['fixed_center', 'center'].

        Returns:
            Dictionary mapping facelet index to piece type list.

        """
        size = self.size
        middle = size // 2
        is_odd = self.has_fixed_centers
        result: dict[int, list[FaceletPieceType]] = {}

        for i in range(self.face_size):
            row, col = divmod(i, size)

            on_row_border = row == 0 or row == size - 1
            on_col_border = col == 0 or col == size - 1

            if on_row_border and on_col_border:
                result[i] = ['corner']
            elif on_row_border or on_col_border:
                if is_odd and middle in {row, col}:
                    result[i] = ['midge', 'edge']
                else:
                    result[i] = ['wing', 'edge']
            elif is_odd and row == middle and col == middle:
                result[i] = ['fixed_center', 'center']
            elif is_odd and middle in {row, col}:
                result[i] = ['t_center', 'center']
            elif min(row, size - 1 - row) == min(col, size - 1 - col):
                result[i] = ['x_center', 'center']
            else:
                result[i] = ['oblique_center', 'center']

        return result

    def get_facelet_piece_types(
            self, facelet_index: int,
    ) -> list[FaceletPieceType]:
        """
        Get the piece types for a specific facelet index.

        Args:
            facelet_index: Global facelet index (0-based).

        Returns:
            List of piece types from most specific to family.

        """
        return self.facelet_piece_types[facelet_index % self.face_size]

    @property
    def orientation(self) -> str:
        """
        Get the cube's orientation as a two-character string.

        Uses the top face center and front face center
        to determine the current orientation of the cube in space.

        For odd-sized cubes, uses the physical center facelet.
        For even-sized cubes, uses a representative position to
        determine orientation.

        It might not work well with an unchecked state.

        Returns:
            A two-character string representing the orientation
            (e.g., 'UF' for white top, green front).

        """
        top_center_index = self.center_index
        front_center_index = 2 * self.face_size + top_center_index

        return self._state[top_center_index] + self._state[front_center_index]

    @property
    def face_center_colors(self) -> tuple[str, ...]:
        """
        Get the center facelet colors for all faces.

        For odd-sized cubes, returns the physical center facelet colors.
        For even-sized cubes, returns representative facelet colors at
        the calculated center position.

        Returns:
            A tuple of center colors for all six faces in order
            (U, R, F, D, L, B).

        """
        center_index = self.center_index

        return tuple(
            self._state[(i * self.face_size) + center_index]
            for i in range(self.face_number)
        )

    @property
    def is_solved(self) -> bool:
        """
        Check if the cube is in a solved state.

        Returns:
            True if the cube is solved.

        """
        return all(face * self.face_size in self._state for face in FACE_ORDER)

    @property
    def cubies(self) -> tuple[
            list[int], list[int], list[int], list[int], list[int],
    ]:
        """
        Convert the cube state to cubie representation.

        Returns:
            A tuple of (corner_permutation, corner_orientation,
            edge_permutation, edge_orientation, center_orientation).

        Raises:
            NotSupportedCubeSizeError: If cube.size != 3

        """
        if self.size == 3:
            return facelets_to_cubies(self._state)

        msg = f'cubies are not available on cube with size {self.size}'
        raise NotSupportedCubeSizeError(msg)

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
            return self._state == other_cube._state  # noqa: SLF001

        oriented_copy = other_cube.oriented_copy(self.orientation)

        return self._state == oriented_copy._state  # noqa: SLF001

    def rotate(self, moves: Algorithm | Move | str, *,
               history: bool = True) -> str:
        """
        Apply a sequence of moves to the cube.

        Args:
            moves: The moves to apply to the cube.
            history: If True, record moves in the cube's history.

        Returns:
            The new state of the cube after applying the moves.

        Raises:
            InvalidMoveError: If a move is invalid.

        """
        moves_str = str(moves)

        if not moves_str:
            return self._state

        try:
            if self.size == 2:
                self._state = rotate_2x2x2.rotate_moves(self._state, moves_str)
            elif self.size == 3:
                self._state = rotate_3x3x3.rotate_moves(self._state, moves_str)
            else:
                self._state = rotate_dynamic.rotate_moves(
                    self._state, moves_str, size=self.size,
                )
        except ValueError as e:
            raise InvalidMoveError(str(e)) from e
        else:
            if history:
                self.history.extend(moves_str.split(' '))
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
            self._state,
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

        Raises:
            InvalidOrientationError: If a orientation key is not valid.

        """
        top_face, front_face = self.check_face_orientations(faces)

        orientation_key = str(self.get_face_index(top_face))

        if front_face:
            orientation_key += str(self.get_face_index(front_face))

        try:
            return OFFSET_ORIENTATION_MAP[orientation_key]
        except KeyError as e:
            raise InvalidOrientationError(str(e)) from e

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

        try:
            moves = self.compute_orientation_moves(faces)
        except (InvalidFaceIndexError, InvalidOrientationError):
            # Can only happen with scrambled non fixed center cube.
            # So it's not necessary to find a better orientation.
            moves = ''

        if moves:
            cube.rotate(moves, history=full)

        return cube

    def display(self, mode: str = '', orientation: str = '',  # noqa: PLR0913 PLR0917
                mask: Mask = '', palette: str = '',
                effect: str = '', facelet: str = '',
                style: str = '') -> str:
        """
        Generate a visual representation of the cube.

        Args:
            mode: Display mode for the visualization.
            orientation: Desired orientation for display.
            mask: Mask to apply to the display.
            palette: Color palette to use.
            effect: Visual effect to apply.
            facelet: Facelet mode for display.
            style: Letter style preset to apply.

        Returns:
            A string containing the visual representation of the cube.

        """
        return VCubeDisplay(self, palette, effect, facelet, style).display(
            mode, orientation, mask,
        )

    def show(self, mode: str = '', orientation: str = '',  # noqa: PLR0913 PLR0917
             mask: Mask = '', palette: str = '',
             effect: str = '', facelet: str = '',
             style: str = '') -> None:
        """Print a visual representation of the cube."""
        print(  # noqa: T201
            self.display(
                mode, orientation, mask,
                palette, effect, facelet,
                style,
            ),
            end='',
        )

    def image(self, *, size: int = 200,  # noqa: PLR0913
              view: str = '3d', mask: Mask = '',
              rotation: str = 'y45x-34',
              distance: float = 10.0,
              cube_color: str = '#111111',
              palette_name: str = 'default') -> str:
        """
        Render the cube as an SVG image.

        Args:
            size: Image dimension in pixels.
            view: Rendering mode. ``'3d'`` for perspective view,
                ``'top'`` for flat top-face with adjacent strips.
            mask: Mask to apply on the cube.
            rotation: Axis-angle rotation string (3d view only).
            distance: Camera distance for perspective projection
                (3d view only).
            cube_color: Hex color for cube body between stickers.
            palette_name: Color palette name for sticker colors.

        Returns:
            SVG string of the cube.

        """
        from cubing_algs.display.image import render_cube  # noqa: PLC0415

        return render_cube(
            self, size=size, view=view, mask=mask,
            rotation=rotation, distance=distance,
            cube_color=cube_color, palette_name=palette_name,
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

    def get_face_index(self, face: str) -> int:
        """
        Get the index of a face by its center color.

        Args:
            face: The center color of the face to find.

        Returns:
            The index (0-5) of the face with that center color.

        Raises:
            InvalidFaceIndexError: If a face is not found.

        """
        try:
            return self.face_center_colors.index(face)
        except ValueError as e:
            raise InvalidFaceIndexError(str(e)) from e

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

    def to_algorithm(self, other: 'VCube') -> Algorithm:
        """
        Build Algorithm to pass from a cube state to another.

        Args:
            other: Another VCube instance.

        Returns:
            An algorithm to apply.

        Raises:
            NotSupportedCubeSizeError: If cube.size != 3 or other.size != 3

        """
        if self.size != 3 or other.size != 3:
            msg = f'to_algorithm is not available on cube with size {self.size}'
            raise NotSupportedCubeSizeError(msg)

        self_uf = self.oriented_copy('UF', full=False)
        other_uf = other.oriented_copy('UF', full=False)

        algorithm = facelets_to_facelets_algorithm(
            self_uf.state,
            other_uf.state,
        )

        orientation = other_uf.compute_orientation_moves(other.orientation)

        if orientation:
            algorithm += orientation

        return algorithm

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
