"""Virtual cube implementation for simulating moves and tracking state."""
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import CornerOrientation
from cubing_algs.annotations import CornerPermutation
from cubing_algs.annotations import CubeCubiesOriented
from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import CubeOrientation
from cubing_algs.annotations import EdgeOrientation
from cubing_algs.annotations import EdgePermutation
from cubing_algs.annotations import FaceFacelets
from cubing_algs.annotations import FaceletPieceType
from cubing_algs.annotations import SpatialOrientation
from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.constants import FACE_INDEXES
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OFFSET_ORIENTATION_MAP
from cubing_algs.display.image import ImageDisplay
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
from cubing_algs.transform.invert import invert_moves


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

    def __init__(
            self,
            initial: CubeFacelets | None = None,
            *,
            size: int = DEFAULT_CUBE_SIZE,
            check: bool = True,
            history: list[str] | None = None,
    ) -> None:
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
    def state(self) -> CubeFacelets:
        """Get the current state of the cube as a facelet string."""
        return self._state

    @property
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
            self,
            facelet_index: int,
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
    def orientation(self) -> CubeOrientation:
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
    def cubies(self) -> CubeCubiesOriented:
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
    def from_cubies(  # noqa: PLR0913 PLR0917
            cp: CornerPermutation,
            co: CornerOrientation,
            ep: EdgePermutation,
            eo: EdgeOrientation,
            so: SpatialOrientation,
            scheme: CubeFacelets | None = None,
    ) -> 'VCube':
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

    def is_equal(
            self,
            other_cube: 'VCube',
            *,
            strict: bool = True,
    ) -> bool:
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

    def rotate(
            self,
            moves: Algorithm | Move | str,
            *,
            history: bool = True,
    ) -> CubeFacelets:
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

    def undo(self, move_number: int = 1) -> CubeFacelets:
        """
        Undo moves from history.

        Args:
            move_number: Number of moves to undo. Default is 1.

        Returns:
            The new state of the cube after undoing the moves.

        """
        moves = Algorithm(Move(m) for m in self.history[-move_number:])
        del self.history[-move_number:]

        return self.rotate(invert_moves(moves), history=False)

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

    def compute_orientation_moves(self, faces: CubeOrientation) -> str:
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

    def oriented_copy(
            self,
            faces: CubeOrientation,
            *,
            full: bool = False,
    ) -> 'VCube':
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

    def display(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            effect: str = '',
            facelet: str = '',
            style: str = '',
    ) -> str:
        """
        Generate a visual representation of the cube.

        Args:
            mode: Display mode for layout/orientation/mask
                  (e.g., 'oll', 'pll', 'cross', 'f2l').
            layout: Display layout ('cube', 'top', 'linear', 'extended').
            orientation: Cube orientation string for reorienting the view.
            mask: Mask to filter which facelets are displayed.
            palette: Color palette to use.
            effect: Visual effect to apply.
            facelet: Facelet mode for display.
            style: Letter style preset to apply.

        Returns:
            A string containing the visual representation of the cube.

        """
        return VCubeDisplay(
            self,
            palette,
            effect,
            facelet,
            style,
        ).display(
            mode=mode,
            layout=layout,
            orientation=orientation,
            mask=mask,
        )

    def show(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            effect: str = '',
            facelet: str = '',
            style: str = '',
    ) -> None:
        """Print a visual representation of the cube."""
        print(  # noqa: T201
            self.display(
                mode=mode,
                layout=layout,
                orientation=orientation,
                mask=mask,
                palette=palette,
                effect=effect,
                facelet=facelet,
                style=style,
            ),
            end='',
        )

    def image(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
            arrows: str = '',
    ) -> str:
        """
        Render the cube as an SVG image.

        Args:
            mode: Display preset that sets layout, orientation, and mask
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            layout: Display layout; 'top' renders a flat 2D top-view,
                    otherwise a 3D perspective view is used.
            orientation: Cube orientation string for reorienting the view
                         before rendering.
            mask: Mask to filter which facelets are displayed.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string for the 3D view, composed of
                      axis-angle pairs (e.g., 'y45x-30').
            distance: Camera distance from the cube center for the 3D view.
            arrows: Comma-separated arrow definitions.

        Returns:
            SVG string of the cube.

        """
        return ImageDisplay(
            self,
            palette,
        ).render(
            mode=mode,
            layout=layout,
            orientation=orientation,
            mask=mask,
            image_size=image_size,
            rotation=rotation,
            distance=distance,
            arrows=arrows,
        )

    def render(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
    ) -> bytes:
        """
        Render the cube as a PNG image, on the GPU and without a window.

        The framing, the palette, the modes and the masks are the ones
        of ``image()``: the same cube comes out the same way in both
        backends, lit like a solid rather than drawn flat.

        Requires the ``opengl`` extra.

        Args:
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before rendering.
            mask: Mask to filter which facelets are displayed.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.

        Returns:
            The bytes of a PNG image, its background left transparent.

        """
        from cubing_algs.display.gl import Presentation  # noqa: PLC0415
        from cubing_algs.display.gl import render  # noqa: PLC0415
        from cubing_algs.display.gl.constants import (  # noqa: PLC0415
            RENDER_SIZE,
        )

        return render(
            self.oriented_copy(orientation, full=True)
            if orientation else self,
            Presentation(
                palette=palette,
                mode=mode,
                mask=mask,
                rotation=rotation,
                distance=distance,
                image_size=image_size or RENDER_SIZE,
            ),
        )

    def view(  # noqa: PLR0913
            self,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            window_size: tuple[int, int] | None = None,
            rotation: str = '',
            distance: float = 0.0,
            debug: bool = False,
            show_axes: bool = False,
    ) -> None:
        """
        Open a window showing the cube, and turn it around until it closes.

        The mouse orbits the cube, the wheel zooms, and the letters of
        the notation turn it one animated move at a time. The cube of
        the viewer is a copy: nothing done in the window reaches this
        one.

        Everything the window is not given here - a look of its own, an
        external orientation from a bluetooth sensor, the duration of a
        move - is reached by building a
        ``cubing_algs.display.gl.Viewer`` directly.

        Requires the ``opengl`` extra.

        Args:
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before showing it.
            mask: Mask to filter which facelets are displayed.
            palette: Color palette name for sticker colors.
            window_size: Width and height of the window, in pixels.
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.
            debug: Monitor the performance of the rendering, and
                show it in the title of the window. F3 turns it on
                and off once the window is open, F4 writes a full
                report, and F5 frees the frames from the vsync.
            show_axes: Show the three axes of the grid, X red, Y green
                and Z blue. F2 turns them on and off.

        """
        from cubing_algs.display.gl import Viewer  # noqa: PLC0415
        from cubing_algs.display.gl.constants import (  # noqa: PLC0415
            VIEWER_SIZE,
        )

        Viewer(
            self.oriented_copy(orientation, full=True)
            if orientation else self,
            palette=palette,
            mode=mode,
            mask=mask,
            rotation=rotation,
            distance=distance,
            window_size=window_size or VIEWER_SIZE,
            debug=debug,
            show_axes=show_axes,
        ).run()

    def animate(  # noqa: PLR0913
            self,
            moves: Iterable[Move | str] | Move | str,
            path: str | Path,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            mask: CubeDisplayMask = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
    ) -> list[Path]:
        """
        Play an algorithm on the cube and write it as an animation.

        The cube is left untouched: an animation starts from the state
        it is in and plays the moves on a copy of it.

        A GIF is written when Pillow is around; without it the frames
        are written as numbered PNG files instead.

        Requires the ``opengl`` extra.

        Args:
            moves: The algorithm to play.
            path: Where the animation is written.
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before playing the algorithm.
            mask: Mask to filter which facelets are displayed.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.

        Returns:
            The paths written to: the GIF alone, or one per frame.

        """
        from cubing_algs.display.gl import Presentation  # noqa: PLC0415
        from cubing_algs.display.gl import animate  # noqa: PLC0415
        from cubing_algs.display.gl.constants import (  # noqa: PLC0415
            RENDER_SIZE,
        )

        return animate(
            self.oriented_copy(orientation, full=True)
            if orientation else self,
            moves,
            path,
            Presentation(
                palette=palette,
                mode=mode,
                mask=mask,
                rotation=rotation,
                distance=distance,
                image_size=image_size or RENDER_SIZE,
            ),
        )

    def get_face(self, face: str) -> FaceFacelets:
        """
        Get the facelets of a specific face by face letter.

        Args:
            face: The face letter (e.g., 'U', 'F', 'R').

        Returns:
            A string of face_size characters representing the facelets
            on that face.

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

    def get_face_by_center(self, face: str) -> FaceFacelets:
        """
        Get the facelets of a face by its center color.

        Args:
            face: The center color to search for.

        Returns:
            A string of face_size characters representing the facelets
            on that face.

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
