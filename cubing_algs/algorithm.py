from collections import UserList
from collections.abc import Callable

from cubing_algs.metrics import compute_metrics
from cubing_algs.move import Move


class Algorithm(UserList[Move]):
    """
    Represents a sequence of Rubik's cube moves.

    This class encapsulates a series of moves to be applied to a Rubik's cube,
    providing methods to manipulate and analyze the algorithm.
    """

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
        return compute_metrics(self)

    def transform(
            self,
            *processes: Callable[[list[Move]], list[Move]],
    ) -> 'Algorithm':
        """
        Apply a series of transformation functions to the algorithm's moves.

        This method enables chaining multiple transformations together, such as
        simplification, optimization, or conversion between notations.
        """
        new_moves = self.copy()

        for process in processes:
            new_moves = process(new_moves)

        if new_moves == self:
            return self

        return Algorithm(new_moves)
