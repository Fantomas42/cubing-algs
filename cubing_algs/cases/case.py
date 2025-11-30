"""Case representation for cubing algorithms."""
from functools import cached_property
from typing import TypedDict

from cubing_algs.algorithm import Algorithm
from cubing_algs.parsing import parse_moves


class RecognitionFeature(TypedDict):
    """Recognition feature information."""

    name: str
    description: str


class RecognitionCase(TypedDict):
    """Individual recognition case information."""

    description: str
    feature: RecognitionFeature
    notes: str
    observation: str


class RecognitionData(TypedDict):
    """Recognition pattern data for identifying a case."""

    cases: list[RecognitionCase]
    moves: list[str]


class CaseData(TypedDict):
    """Complete case data structure from JSON."""

    name: str
    code: str
    description: str
    aliases: list[str]
    arrows: str
    symmetry: str
    family: str
    groups: list[str]
    status: str
    recognition: RecognitionData
    optimal_cycles: int
    optimal_htm: int
    optimal_stm: int
    probability: float
    probability_label: str
    main: str
    algorithms: list[str]


class Case:  # noqa: PLR0904
    """
    Represents a single cubing case with its algorithms and properties.

    A case represents a specific cube configuration that needs to be solved,
    such as an OLL or PLL case, with associated algorithms and metadata.
    """

    def __init__(self, method: str, step: str, data: CaseData) -> None:
        """
        Initialize a Case with method, step, and data.

        Args:
            method: The solving method (e.g., 'CFOP')
            step: The step within the method (e.g., 'OLL', 'PLL')
            data: Dictionary containing case properties and algorithms

        """
        self.method: str = method
        self.step: str = step
        self.data: CaseData = data

    @cached_property
    def name(self) -> str:
        """Case name identifier."""
        return self.data['name']

    @cached_property
    def code(self) -> str:
        """Case code or notation."""
        return self.data['code']

    @cached_property
    def family(self) -> str:
        """Family or category the case belongs to."""
        return self.data['family']

    @cached_property
    def groups(self) -> list[str]:
        """Groups or classifications for the case."""
        return self.data['groups']

    @cached_property
    def status(self) -> str:
        """Status of the case (e.g., active, deprecated)."""
        return self.data['status']

    @cached_property
    def description(self) -> str:
        """Human-readable description of the case."""
        return self.data.get('description', '')

    @cached_property
    def aliases(self) -> list[str]:
        """Alternative names for the case."""
        return self.data.get('aliases', [])

    @cached_property
    def arrows(self) -> str:
        """Arrow notation for visualizing piece movements."""
        return self.data.get('arrows', '')

    @cached_property
    def symmetry(self) -> str:
        """Symmetry properties of the case."""
        return self.data.get('symmetry', '')

    @cached_property
    def recognition(self) -> RecognitionData:
        """Recognition pattern for identifying the case."""
        return self.data.get('recognition', {})

    @cached_property
    def optimal_cycles(self) -> int:
        """Optimal number of cycles to solve the case."""
        return self.data['optimal_cycles']

    @cached_property
    def optimal_htm(self) -> int:
        """Optimal solution length in Half Turn Metric."""
        return self.data['optimal_htm']

    @cached_property
    def optimal_stm(self) -> int:
        """Optimal solution length in Slice Turn Metric."""
        return self.data['optimal_stm']

    @cached_property
    def probability(self) -> float:
        """Probability of encountering this case."""
        return self.data['probability']

    @cached_property
    def probability_label(self) -> str:
        """Human-readable label for the probability."""
        return self.data['probability_label']

    @cached_property
    def main_algorithm(self) -> Algorithm:
        """Primary algorithm for solving the case."""
        return parse_moves(self.data['main'])

    @cached_property
    def algorithms(self) -> list[Algorithm]:
        """All alternative algorithms for solving the case."""
        return [
            parse_moves(moves)
            for moves in self.data['algorithms']
        ]

    @cached_property
    def badmephisto(self) -> dict:
        """
        BadMephisto informations.

        http://badmephisto.com/
        """
        return self.data.get('badmephisto', {})

    @cached_property
    def logiqx(self) -> list:
        """
        Logiqx informations.

        https://logiqx.github.io/cubing-algs/html/
        """
        return self.data.get('logiqx', [])

    @cached_property
    def sarah_pll_skips(self) -> dict:
        """
        Sarah's cubing site informations.

        https://sarah.cubing.net/3x3x3/pll-skip-cases
        """
        return self.data.get('sarah', {})

    @cached_property
    def two_phase_algorithms(self) -> list[Algorithm]:
        """Algorithms computed by two-phase algorithm."""
        return [
            parse_moves(moves)
            for moves in self.data.get('two-phase', [])
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
