"""Case representation for cubing algorithms."""
from functools import cached_property

from cubing_algs.parsing import parse_moves


class Case:
    """
    Represents a single cubing case with its algorithms and properties.

    A case represents a specific cube configuration that needs to be solved,
    such as an OLL or PLL case, with associated algorithms and metadata.
    """

    def __init__(self, method: str, step: str, data: dict) -> None:
        """
        Initialize a Case with method, step, and data.

        Args:
            method: The solving method (e.g., 'CFOP')
            step: The step within the method (e.g., 'OLL', 'PLL')
            data: Dictionary containing case properties and algorithms

        """
        self.method = method
        self.step = step

        self.data = data

    @cached_property
    def name(self) -> str:
        """Case name identifier."""
        return self.data['name']

    @cached_property
    def code(self) -> str:
        """Case code or notation."""
        return self.data['code']

    @cached_property
    def description(self) -> str:
        """Human-readable description of the case."""
        return self.data['description']

    @cached_property
    def aliases(self) -> str:
        """Alternative names for the case."""
        return self.data['aliases']

    @cached_property
    def arrows(self) -> str:
        """Arrow notation for visualizing piece movements."""
        return self.data['arrows']

    @cached_property
    def symmetry(self) -> str:
        """Symmetry properties of the case."""
        return self.data['symmetry']

    @cached_property
    def family(self) -> str:
        """Family or category the case belongs to."""
        return self.data['family']

    @cached_property
    def groups(self) -> str:
        """Groups or classifications for the case."""
        return self.data['groups']

    @cached_property
    def status(self) -> str:
        """Status of the case (e.g., active, deprecated)."""
        return self.data['status']

    @cached_property
    def recognition(self) -> str:
        """Recognition pattern for identifying the case."""
        return self.data['recognition']

    @cached_property
    def optimal_cycles(self) -> str:
        """Optimal number of cycles to solve the case."""
        return self.data['optimal_cycles']

    @cached_property
    def optimal_htm(self) -> str:
        """Optimal solution length in Half Turn Metric."""
        return self.data['optimal_htm']

    @cached_property
    def optimal_stm(self) -> str:
        """Optimal solution length in Slice Turn Metric."""
        return self.data['optimal_stm']

    @cached_property
    def probability(self) -> str:
        """Probability of encountering this case."""
        return self.data['probability']

    @cached_property
    def probability_label(self) -> str:
        """Human-readable label for the probability."""
        return self.data['probability_label']

    @cached_property
    def main_algorithm(self) -> str:
        """Primary algorithm for solving the case."""
        return parse_moves(self.data['main'])

    @cached_property
    def algorithms(self) -> str:
        """All alternative algorithms for solving the case."""
        return [
            parse_moves(moves)
            for moves in self.data['algorithms']
        ]

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the case.

        Returns:
            String representation with case name

        """
        return f'Case { self.name }'

    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the case.

        Returns:
            String representation with method, step, and case name

        """
        return (
            f"Case('{ self.method }', '{ self.step }', "
            f"{{'name': '{ self.name }'}})"
        )
