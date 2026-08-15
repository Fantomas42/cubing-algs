"""
Core Algorithm class for representing and manipulating
sequences of cube moves.
"""
from collections import UserList
from collections.abc import Callable
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Self
from typing import SupportsIndex

from cubing_algs.annotations import CubeMask
from cubing_algs.annotations import CubeOrientation
from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.cycles import compute_cycles
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.ergonomics import HandDominance
from cubing_algs.ergonomics import compute_ergonomics
from cubing_algs.exceptions import InvalidCubeSizeError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.impacts import ImpactData
from cubing_algs.impacts import compute_impacts
from cubing_algs.memory import MemoryData
from cubing_algs.memory import compute_memory
from cubing_algs.metrics import MetricsData
from cubing_algs.metrics import compute_metrics
from cubing_algs.move import Move
from cubing_algs.structure import StructureData
from cubing_algs.structure import compute_structure

if TYPE_CHECKING:
    from cubing_algs.vcube import VCube


class Algorithm(UserList[Move]):  # noqa: PLR0904
    """
    Represents a sequence of Rubik's cube moves.

    This class encapsulates a series of moves to be applied to a Rubik's cube,
    providing methods to manipulate and analyze the algorithm.
    """

    def __init__(self, initlist: Iterable[Move] | None = None) -> None:
        """Initialize an Algorithm with an optional sequence of Move objects."""
        super().__init__()

        if initlist is not None:
            self.data.extend(initlist)

    @staticmethod
    def parse_moves(
            moves: Iterable[Move | str] | Move | str,
            *,
            trust_input: bool = False,
    ) -> 'Algorithm':
        """
        Parse a string or list of strings into an Algorithm object.

        Args:
            moves: A string or iterable of Move objects or strings
                representing moves.
            trust_input: If True, trust the input and skip cleaning
                and validation steps.

        Returns:
            An Algorithm object containing the parsed moves.

        """
        from cubing_algs.parsing import parse_moves  # noqa: PLC0415

        return parse_moves(moves, trust_input=trust_input)

    @staticmethod
    def parse_move(item: Move | str) -> Move:
        """
        Parse a single move string into a Move object.

        Args:
            item: A Move object or string representing a single move.

        Returns:
            A validated Move object.

        Raises:
            InvalidMoveError: If the move is not valid.

        """
        move = item if isinstance(item, Move) else Move(item)

        if not move.is_valid:
            msg = f'{ item } is an invalid move'
            raise InvalidMoveError(msg)

        return move

    def append(self, item: Move | str) -> None:
        """Add a move to the end of the algorithm."""
        self.data.append(self.parse_move(item))

    def insert(self, i: int, item: Move | str) -> None:
        """Insert a move at a specific position in the algorithm."""
        self.data.insert(i, self.parse_move(item))

    def extend(self, other: Iterable[Move | str] | Move | str) -> None:
        """Extend the algorithm with moves from another sequence."""
        if isinstance(other, Algorithm):
            self.data.extend(other)
        else:
            self.data.extend(self.parse_moves(other))

    def __iadd__(self, other: Iterable[Move | str] | Move | str) -> Self:
        """
        In-place addition operator (+=) for algorithms.

        Args:
            other: A string, Move, or iterable of moves to add to this
                algorithm.

        Returns:
            This algorithm object after modification.

        """
        self.extend(other)
        return self

    def __radd__(self, other: Iterable[Move | str] | str) -> 'Algorithm':
        """
        Right addition operator for algorithms.

        Args:
            other: A string, or iterable of moves to add before this
                algorithm.

        Returns:
            A new Algorithm with other followed by this algorithm.

        """
        result = self.parse_moves(other)
        result += self
        return result

    def __add__(self, other: Iterable[Move | str] | Move | str) -> 'Algorithm':
        """
        Addition operator (+) for algorithms.

        Args:
            other: A string, Move, or iterable of moves to add to this
                algorithm.

        Returns:
            A new Algorithm combining this algorithm with other.

        """
        if isinstance(other, Algorithm):
            result = self.copy()
            result.extend(other)
            return result

        result = self.copy()
        result.extend(self.parse_moves(other))
        return result

    def __setitem__(
            self,
            i: SupportsIndex | slice,
            item: Move | str | Iterable[Move | str],
    ) -> None:
        """
        Set a move at a specific index in the algorithm.

        Raises:
            InvalidMoveError: If a single-index assignment is given a value
                that is not a Move or move string.

        """
        if isinstance(i, slice):
            self.data[i] = self.parse_moves(item)
        elif isinstance(item, Move | str):
            self.data[i] = self.parse_move(item)
        else:
            msg = f'{ item } is an invalid move'
            raise InvalidMoveError(msg)

    def __str__(self) -> str:
        """
        Convert the algorithm to a human-readable string.

        Returns:
            A space-separated string of all moves in the algorithm.

        """
        return ' '.join(str(m) for m in self)

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the algorithm.

        Returns:
            A Python expression that can recreate this Algorithm object.

        """
        return f'Algorithm("{ " ".join(str(m) for m in self) }")'

    def transform(
            self,
            *processes: Callable[['Algorithm'], 'Algorithm'],
            to_fixpoint: bool = False,
    ) -> 'Algorithm':
        """
        Apply a series of transformation functions to the algorithm's moves.

        This method enables chaining multiple transformations together, such as
        simplification, optimization, or conversion between notations.

        Args:
            *processes: One or more transformation functions to apply.
            to_fixpoint: If True, repeat transformations until no changes occur.

        Returns:
            A new Algorithm with all transformations applied.

        """
        mod_moves = self.copy()

        if not to_fixpoint:
            for process in processes:
                mod_moves = process(mod_moves)
            return mod_moves

        new_moves = self.copy()
        for _ in range(MAX_ITERATIONS):
            for process in processes:
                mod_moves = process(mod_moves)

            if new_moves == mod_moves:
                break
            new_moves = mod_moves

        return mod_moves

    def validate_cube_size(self, size: int) -> None:
        """
        Ensure the given cube size can accommodate this algorithm.

        Raises:
            InvalidCubeSizeError: If cube size is less than minimal cube size.

        """
        if size < self.min_cube_size:
            msg = (
                'Cube size is too small for this algorithm '
                f'({ size } < { self.min_cube_size })'
            )
            raise InvalidCubeSizeError(msg)

    def impacts(self, size: int = DEFAULT_CUBE_SIZE) -> ImpactData:
        """
        Analyze the spatial impact of this algorithm on a cube.

        Computes comprehensive metrics about how the algorithm affects
        individual facelets on the cube, including movement patterns,
        distances, and face-level statistics.

        Cubie-level analysis is only available for 3x3x3 cubes.

        Args:
            size: Size of the cube (default 3).

        Returns:
            An ImpactData object containing comprehensive impact metrics.

        Example:
            >>> alg = Algorithm.parse_moves("R U R' U'")
            >>> impacts = alg.impacts()
            >>> impacts.facelets_mobilized_count
            18  # 18 out of 54 facelets are affected
            >>> impacts.facelets_scrambled_percent
            0.33  # About 33% of the cube is scrambled

        """
        self.validate_cube_size(size)

        return compute_impacts(self, size=size)

    @property
    def cycles(self) -> int:
        """
        Get the number of times this algorithm must be applied
        to return a 3x3x3 cube to its solved state.

        This property calculates the "order" of the algorithm - how many times
        you need to execute the sequence of moves to bring a solved cube back
        to its original solved state.

        This is useful for understanding the periodic behavior of algorithms
        and their mathematical properties.

        Example:
            >>> alg = Algorithm.parse_moves("R U R' U'")
            >>> alg.cycles
            6  # Meaning applying this 6 times returns to solved

        """
        return compute_cycles(self)

    @property
    def metrics(self) -> MetricsData:
        """
        Calculate comprehensive metrics for analyzing algorithm efficiency
        and characteristics.

        Computes various standardized metrics including different move counting
        systems (HTM, QTM, STM, ETM, RTM, QSTM), move type categorization,
        and generator analysis to identify the most frequently used faces.

        This is essential for comparing algorithm efficiency, analyzing solve
        methods, and understanding algorithmic complexity across different
        metric systems used in speedcubing competitions.

        Example:
            >>> alg = Algorithm.parse_moves("R U R' U' R' F R F'")
            >>> metrics = alg.metrics
            >>> metrics.htm
            8  # Half Turn Metric: 8 moves
            >>> metrics.qtm
            8  # Quarter Turn Metric: 8 quarter turns
            >>> metrics.generators
            ['R', 'U', 'F']  # Most used faces in order

        """
        return compute_metrics(self)

    @property
    def ergonomics(self) -> ErgonomicsData:
        """
        Analyze the ergonomic properties and execution comfort
        of this algorithm.

        Computes comprehensive ergonomic metrics including hand balance,
        fingertrick comfort, regrip requirements, flow analysis, and
        overall execution comfort. This analysis considers speedcubing
        conventions for finger assignments and identifies awkward transitions.

        This is valuable for evaluating algorithm suitability for speedsolving,
        comparing alternative algorithms for the same case, and understanding
        the physical demands of different move sequences.

        Example:
            >>> alg = Algorithm.parse_moves("R U R' U' R' F R F'")
            >>> ergo = alg.ergonomics
            >>> ergo.ergonomic_score
            0.93  # Overall score from 0.0 to 1.0
            >>> ergo.ergonomic_rating
            'Excellent'  # Qualitative assessment
            >>> ergo.hand_balance_ratio
            0.5  # Hand balance (1.0 is perfect)

        """
        return self.compute_ergonomics()

    def compute_ergonomics(
            self,
            hand_dominance: HandDominance = HandDominance.RIGHT,
    ) -> ErgonomicsData:
        """
        Analyze the ergonomic properties for a given hand dominance.

        Same analysis as the `ergonomics` property, but lets the caller
        pick the hand dominance the metrics are computed for.

        Args:
            hand_dominance: The hand dominance preference.

        Returns:
            ErgonomicsData containing all calculated ergonomic metrics.

        Example:
            >>> alg = Algorithm.parse_moves("R U R' U'")
            >>> lefty = alg.compute_ergonomics(HandDominance.LEFT)
            >>> lefty.fingertrick_comfort
            0.89  # Easier for a left-handed cuber

        """
        return compute_ergonomics(self, hand_dominance)

    @property
    def structure(self) -> StructureData:
        """
        Analyze the structural composition of this algorithm.

        Computes comprehensive structural metrics including detection of
        conjugate and commutator patterns, nesting analysis, compression
        ratios, and coverage statistics.

        This analysis helps understand algorithm composition, identify
        patterns for memorization, and evaluate the mathematical structure
        of move sequences.

        Example:
            >>> alg = Algorithm.parse_moves("F R U R' U' F'")
            >>> struct = alg.structure
            >>> struct.compressed
            '[F: [R, U]]'
            >>> struct.total_structures
            2  # One conjugate, one commutator
            >>> struct.conjugate_count
            1
            >>> struct.commutator_count
            1

        """
        return compute_structure(self)

    @property
    def memory(self) -> MemoryData:
        """Analyze the memorisation difficulty of this algorithm."""
        return compute_memory(self)

    @property
    def min_cube_size(self) -> int:
        """
        Compute the minimum cube size required to execute this algorithm.

        Analyzes the moves to determine the smallest cube that can accommodate
        all the layered moves in the algorithm.
        """
        min_cube = 2

        for m in self:
            if m.is_layered or m.is_inner_move:
                cube = 3

                max_layers = max(m.layers)
                if max_layers > 1:
                    cube = max_layers + 2

                min_cube = max(cube, min_cube)

        return min_cube

    @property
    def is_standard(self) -> bool:
        """Check if algorithm is in standard notations."""
        return not self.is_sign

    @property
    def is_sign(self) -> bool:
        """Check if algorithm contains SiGN notations."""
        return any(m.is_sign_move for m in self)

    @property
    def has_rotations(self) -> bool:
        """Check if algorithm contains rotations."""
        return any(m.is_rotational_move for m in self)

    @property
    def has_internal_rotations(self) -> bool:
        """
        Check if algorithm contains internal rotations
        induced by wide or inner moves.
        """
        return any(
            m.is_wide_move or m.is_inner_move
            for m in self
        )

    @property
    def has_pauses(self) -> bool:
        """Check if algorithm contains pauses."""
        return any(m.is_pause for m in self)

    @property
    def has_times(self) -> bool:
        """Check if algorithm timed moves."""
        return any(m.is_timed for m in self)

    def get_cube_and_impact_mask(
            self,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            impact_mask: bool = True,
    ) -> tuple['VCube', CubeMask]:
        """
        Apply this algorithm to a fresh cube and return it with an impact mask.

        Strips pauses and timed moves, applies the cleaned algorithm to a new
        VCube, and optionally computes a mask string identifying which facelets
        were moved by the algorithm.

        Args:
            size: Size of the cube (default 3).
            impact_mask: If True, compute and return a mask string marking
                moved facelets. If False, the mask is an empty string.

        Returns:
            A tuple of (cube, mask) where cube is the VCube after the algorithm
            is applied, and mask is the CubeMask string of impacted facelets
            by the algorithm or '' when impact_mask is False.

        """
        from cubing_algs.masks import compute_algorithm_mask  # noqa: PLC0415
        from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415
        from cubing_algs.transform.timing import untime_moves  # noqa: PLC0415
        from cubing_algs.vcube import VCube  # noqa: PLC0415

        self.validate_cube_size(size)

        cleaned_algo = self.transform(
            unpause_moves,
            untime_moves,
        )

        cube = VCube(size=size)
        cube.rotate(cleaned_algo)

        moved_facelets_mask = ''

        if impact_mask:
            moved_facelets_mask, _ = compute_algorithm_mask(
                cleaned_algo, size,
            )

        return cube, moved_facelets_mask

    def show(  # noqa: PLR0913
            self,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            palette: str = '',
            effect: str = '',
            facelet: str = '',
            style: str = '',
            impact_mask: bool = True,
    ) -> 'VCube':
        """
        Visualize the algorithm's effect on a cube.

        Creates a VCube, applies this algorithm to it, and displays the result
        with a mask showing which facelets are affected by the algorithm.

        Args:
            size: Size of the cube.
            mode: Display mode for layout/orientation/mask
                  (e.g., 'oll', 'pll', 'cross', 'f2l').
            layout: Display layout ('cube', 'top', 'linear', 'extended').
            orientation: Cube orientation string for reorienting the view.
            palette: Color palette to use.
            effect: Visual effect to apply.
            facelet: Facelet mode for display.
            style: Letter style preset to apply.
            impact_mask: Show affected facelets with a mask.

        Returns:
            A VCube object with the algorithm applied.

        """
        cube, moved_facelets_mask = self.get_cube_and_impact_mask(
            size=size,
            impact_mask=impact_mask,
        )

        cube.show(
            mode=mode,
            layout=layout,
            orientation=orientation,
            mask=moved_facelets_mask,
            palette=palette,
            effect=effect,
            facelet=facelet,
            style=style,
        )

        return cube

    def image(  # noqa: PLR0913
            self,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            mode: str = '',
            layout: str = '',
            orientation: CubeOrientation = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0,
            impact_mask: bool = True,
    ) -> str:
        """
        Generate image of the algorithm's effect on a cube.

        Creates a VCube, applies this algorithm to it, and displays the result
        with a mask showing which facelets are affected by the algorithm.

        Args:
            size: Size of the cube (default 3).
            mode: Display preset that sets layout, orientation, and mask
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            layout: Display layout; 'top' renders a flat 2D top-view,
                    otherwise a 3D perspective view is used.
            orientation: Cube orientation string for reorienting the view
                         before rendering.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string for the 3D view, composed of
                      axis-angle pairs (e.g., 'y45x-30').
            distance: Camera distance from the cube center for the 3D view.
            impact_mask: If True, highlight facelets moved by the algorithm.

        Returns:
            SVG string of the cube.

        """
        cube, moved_facelets_mask = self.get_cube_and_impact_mask(
            size=size,
            impact_mask=impact_mask,
        )

        return cube.image(
            mode=mode,
            layout=layout,
            orientation=orientation,
            mask=moved_facelets_mask,
            palette=palette,
            image_size=image_size,
            rotation=rotation,
            distance=distance,
        )

    def render(  # noqa: PLR0913
            self,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
            impact_mask: bool = True,
    ) -> bytes:
        """
        Render the algorithm's effect on a cube as a PNG image.

        Creates a VCube, applies this algorithm to it, and renders the
        result on the GPU with a mask showing which facelets the
        algorithm affects. The picture is the one ``image()`` draws,
        lit as a solid rather than flat.

        Requires the ``opengl`` extra.

        Args:
            size: Size of the cube (default 3).
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before rendering.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.
            impact_mask: If True, highlight facelets moved by the algorithm.

        Returns:
            The bytes of a PNG image, its background left transparent.

        """
        cube, moved_facelets_mask = self.get_cube_and_impact_mask(
            size=size,
            impact_mask=impact_mask,
        )

        return cube.render(
            mode=mode,
            orientation=orientation,
            mask=moved_facelets_mask,
            palette=palette,
            image_size=image_size,
            rotation=rotation,
            distance=distance,
        )

    def view(  # noqa: PLR0913
            self,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            palette: str = '',
            window_size: tuple[int, int] | None = None,
            rotation: str = '',
            distance: float = 0.0,
            show_fps: bool = False,
            show_axes: bool = False,
            impact_mask: bool = True,
    ) -> 'VCube':
        """
        Open a window on the cube the algorithm leads to.

        Creates a VCube, applies this algorithm to it, and shows the
        result in an interactive window, masked as ``show()`` masks it.

        Requires the ``opengl`` extra.

        Args:
            size: Size of the cube (default 3).
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before showing it.
            palette: Color palette name for sticker colors.
            window_size: Width and height of the window, in pixels.
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.
            show_fps: Show the frame rate in the title of the window.
                F3 turns it on and off once the window is open.
            show_axes: Show the three axes of the grid, X red, Y green
                and Z blue. F2 turns them on and off.
            impact_mask: If True, highlight facelets moved by the algorithm.

        Returns:
            A VCube object with the algorithm applied.

        """
        cube, moved_facelets_mask = self.get_cube_and_impact_mask(
            size=size,
            impact_mask=impact_mask,
        )

        cube.view(
            mode=mode,
            orientation=orientation,
            mask=moved_facelets_mask,
            palette=palette,
            window_size=window_size,
            rotation=rotation,
            distance=distance,
            show_fps=show_fps,
            show_axes=show_axes,
        )

        return cube

    def animate(  # noqa: PLR0913
            self,
            path: str | Path,
            size: int = DEFAULT_CUBE_SIZE,
            *,
            mode: str = '',
            orientation: CubeOrientation = '',
            palette: str = '',
            image_size: int = 0,
            rotation: str = '',
            distance: float = 0.0,
            impact_mask: bool = False,
    ) -> list[Path]:
        """
        Write the algorithm playing on a solved cube as an animation.

        Unlike ``image()`` and ``render()``, which draw the state the
        algorithm leads to, this plays it: the cube starts solved and
        every move turns its layers in turn.

        The impact mask is off by default here, for the same reason:
        dimming everything the algorithm leaves alone tells a still
        picture apart, but hides most of a cube one is watching turn.

        Requires the ``opengl`` extra.

        Args:
            path: Where the animation is written.
            size: Size of the cube (default 3).
            mode: Display preset that sets the mask and the orientation
                  together (e.g., 'oll', 'pll', 'cross', 'f2l').
            orientation: Cube orientation string for reorienting the cube
                         before playing the algorithm.
            palette: Color palette name for sticker colors.
            image_size: Output image dimension in pixels (width and height).
            rotation: Camera rotation string, composed of axis-angle
                      pairs (e.g., 'y45x-34').
            distance: Camera distance from the cube center.
            impact_mask: If True, highlight facelets moved by the algorithm.

        Returns:
            The paths written to: the GIF alone, or one per frame.

        """
        from cubing_algs.vcube import VCube  # noqa: PLC0415

        self.validate_cube_size(size)

        moved_facelets_mask: CubeMask = ''

        if impact_mask:
            _cube, moved_facelets_mask = self.get_cube_and_impact_mask(
                size=size,
            )

        return VCube(size=size).animate(
            self,
            path,
            mode=mode,
            orientation=orientation,
            mask=moved_facelets_mask,
            palette=palette,
            image_size=image_size,
            rotation=rotation,
            distance=distance,
        )

    def to_dict(self, size: int = DEFAULT_CUBE_SIZE) -> dict[str, Any]:
        """
        Export algorithm data as a plain, JSON-serializable dict.

        Aggregates the move string, every analysis property, and the
        impacts computed for the given cube size. Nested data containers
        (NamedTuple) are recursively flattened to plain dicts.

        Args:
            size: Cube size used for impacts computation.

        Returns:
            A dict aggregating the algorithm moves and all its computed
            properties and analyses.

        """
        from cubing_algs.vcube import VCube  # noqa: PLC0415

        def flatten(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, VCube | Algorithm | Move):
                return obj.state if isinstance(obj, VCube) else str(obj)
            if hasattr(obj, '_asdict'):  # NamedTuple
                return {k: flatten(v) for k, v in obj._asdict().items()}
            if hasattr(obj, 'items'):  # mapping
                return {k: flatten(v) for k, v in obj.items()}
            if type(obj) in {list, tuple}:
                return [flatten(v) for v in obj]
            return obj

        return {
            'moves': str(self),
            'cycles': self.cycles,
            'min_cube_size': self.min_cube_size,
            'is_standard': self.is_standard,
            'is_sign': self.is_sign,
            'has_rotations': self.has_rotations,
            'has_internal_rotations': self.has_internal_rotations,
            'has_pauses': self.has_pauses,
            'has_times': self.has_times,
            'metrics': flatten(self.metrics),
            'ergonomics': flatten(self.ergonomics),
            'structure': flatten(self.structure),
            'memory': flatten(self.memory),
            'impacts': flatten(self.impacts(size)),
        }
