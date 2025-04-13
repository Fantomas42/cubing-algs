from collections.abc import Callable
from functools import cached_property
from typing import Any

from cubing_algs.metrics import compute_metrics
from cubing_algs.move import Move


class Algorithm:
    """
    Represents a sequence of Rubik's cube moves.

    This class encapsulates a series of moves to be applied to a Rubik's cube,
    providing methods to manipulate and analyze the algorithm.
    """

    def __init__(self, moves: list[Move]):
        """
        Initialize an Algorithm with a list of Move objects.
        """
        self.moves = moves

    def append(self, move: Move) -> None:
        self.moves.append(move)

    def extend(self, moves: list[Move]) -> None:  # | Algorithm
        if isinstance(moves, Algorithm):
            self.moves.extend(moves.moves)
        else:
            self.moves.extend(moves)

    def insert(self, i: int, move: Move) -> None:
        self.moves.insert(i, move)

    def remove(self, move: Move) -> None:
        self.moves.remove(move)

    def pop(self, *arg):
        return self.moves.pop(*arg)

    def copy(self):
        return Algorithm(self.moves.copy())

    def __iter__(self):
        yield from self.moves

    def __getitem__(self, index):
        return self.moves[index]

    def __setitem__(self, index, value):
        self.moves[index] = value

    def __delitem__(self, index):
        del self.moves[index]

    def __len__(self) -> int:
        """
        Return the number of moves in the algorithm.
        """
        return len(self.moves)

    def __str__(self) -> str:
        """
        Convert the algorithm to a human-readable string.
        """
        return ' '.join([str(m) for m in self.moves])

    def __repr__(self) -> str:
        """
        Return a string representation that can be used
        to recreate the algorithm.
        """
        return f'Algorithm("{ "".join([str(m) for m in self.moves]) }")'

    def __eq__(self, other: Any) -> bool:
        """
        Compare this algorithm with another for equality.

        Two algorithms are equal if they have identical move sequences.
        """
        return isinstance(other, Algorithm) and other.moves == self.moves

    def __hash__(self) -> int:
        """
        Calculate a hash value for this algorithm.

        This allows Algorithm objects to be used as dictionary keys.
        """
        return hash(self.__str__())

    @property
    def metrics(self) -> dict[str, int | list[str]]:
        """
        Calculate various metrics for this algorithm.

        Uses the compute_metrics function to analyze the algorithm's efficiency,
        move types, and other characteristics.
        """
        return compute_metrics(self.moves)

    def transform(
            self,
            *processes: Callable[[list[Move]], list[Move]],
    ) -> 'Algorithm':
        """
        Apply a series of transformation functions to the algorithm's moves.

        This method enables chaining multiple transformations together, such as
        simplification, optimization, or conversion between notations.
        """
        new_moves = self.moves.copy()

        for process in processes:
            new_moves = process(new_moves)

        if new_moves == self.moves:
            return self

        return Algorithm(new_moves)
