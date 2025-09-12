from collections import UserList
from collections.abc import Callable
from collections.abc import Iterable
from functools import cached_property

from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.metrics import compute_metrics
from cubing_algs.move import Move


class Algorithm(UserList[Move]):
    """
    Represents a sequence of Rubik's cube moves.

    This class encapsulates a series of moves to be applied to a Rubik's cube,
    providing methods to manipulate and analyze the algorithm.
    """

    def __init__(self, initlist: Iterable[Move] | None = None):
        super().__init__()

        if initlist is not None:
            self.data.extend(initlist)

    @staticmethod
    def parse_moves(items: str | list[str]) -> 'Algorithm':
        """
        Parse a string or list of strings into an Algorithm object.
        """
        from cubing_algs.parsing import parse_moves  # noqa: PLC0415

        return parse_moves(items, secure=False)

    @staticmethod
    def parse_move(item: str) -> Move:
        """
        Parse a single move string into a Move object.
        """
        move = Move(item)
        if not move.is_valid:
            msg = f'{ item } is an invalid move'
            raise InvalidMoveError(msg)

        return move

    def append(self, item) -> None:
        """
        Add a move to the end of the algorithm.
        """
        self.data.append(self.parse_move(item))

    def insert(self, i, item) -> None:
        """
        Insert a move at a specific position in the algorithm.
        """
        self.data.insert(i, self.parse_move(item))

    def extend(self, other) -> None:
        """
        Extend the algorithm with moves from another sequence.
        """
        if isinstance(other, Algorithm):
            self.data.extend(other)
        else:
            self.data.extend(self.parse_moves(other))

    def __iadd__(self, other) -> 'Algorithm':
        """
        In-place addition operator (+=) for algorithms.
        """
        self.extend(other)
        return self

    def __radd__(self, other) -> 'Algorithm':
        """
        Right addition operator for algorithms.
        """
        result = self.parse_moves(other)
        result += self
        return result

    def __add__(self, other) -> 'Algorithm':
        """
        Addition operator (+) for algorithms.
        """
        if isinstance(other, Algorithm):
            result = self.copy()
            result.extend(other)
            return result

        result = self.copy()
        result.extend(self.parse_moves(other))
        return result

    def __setitem__(self, i, item) -> None:
        """
        Set a move at a specific index in the algorithm.
        """
        if isinstance(item, Move):
            self.data[i] = item
        else:
            self.data[i] = self.parse_moves(item)

    def __str__(self) -> str:
        """
        Convert the algorithm to a human-readable string.
        """
        return ' '.join([str(m) for m in self])

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the algorithm.
        """
        return f'Algorithm("{ "".join([str(m) for m in self]) }")'

    @property
    def metrics(self) -> dict[str, int | list[str]]:
        """
        Calculate various metrics for this algorithm.

        Uses the compute_metrics function to analyze the algorithm's efficiency,
        move types, and other characteristics.
        """
        return compute_metrics(self)

    def transform(
            self,
            *processes: Callable[[list[Move]], list[Move]],
            to_fixpoint: bool = False,
    ) -> 'Algorithm':
        """
        Apply a series of transformation functions to the algorithm's moves.

        This method enables chaining multiple transformations together, such as
        simplification, optimization, or conversion between notations.
        """
        new_moves = self.copy()
        mod_moves = self.copy()

        max_iterations = 1
        if to_fixpoint:
            max_iterations = MAX_ITERATIONS

        for _ in range(max_iterations):
            for process in processes:
                mod_moves = process(mod_moves)

            if new_moves == mod_moves:
                break
            new_moves = mod_moves

        return Algorithm(mod_moves)

    @cached_property
    def min_cube_size(self) -> int:
        """
        Compute the minimum cube size required to apply the algorithm.

        This allows validation of the algorithm against a cube.
        """
        min_cube = 2

        for m in self:
            if m.is_layered or m.is_inner_move:
                cube = 3

                max_layers = max(m.layers)
                if max_layers > 1:
                    cube = (max_layers + 1) * 2

                min_cube = max(cube, min_cube)

        return min_cube

    @cached_property
    def is_standard(self) -> bool:
        """
        Check if algorithm is in standard notations
        """
        return not self.is_sign

    @cached_property
    def is_sign(self) -> bool:
        """
        Check if algorithm contains SiGN notations
        """
        return any(m.is_sign_move for m in self)

    @cached_property
    def has_rotations(self) -> bool:
        """
        Check if algorithm contains rotations
        """
        return any(m.is_wide_move or m.is_rotation_move for m in self)

    @cached_property
    def has_internal_rotations(self) -> bool:
        """
        Check if algorithm contains internal rotations
        inducted by the moves.
        """
        return any(m.is_wide_move for m in self)
