"""Case representation for cubing algorithms."""
from functools import cached_property
from typing import NotRequired
from typing import TypedDict
from typing import cast

from cubing_algs.algorithm import Algorithm
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves


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


class BadmephistoData(TypedDict):
    """BadMephisto algorithm information."""

    algos: list[str]
    comment: str
    difficulty: int
    uid: str


class LogiqxVariation(TypedDict):
    """Logiqx algorithm variation."""

    algo: str
    description: str
    tags: list[str]


class LogiqxAlgorithm(TypedDict):
    """Logiqx algorithm information."""

    algo: str
    description: str
    variations: NotRequired[list[LogiqxVariation]]


class CaseData(TypedDict):
    """Complete case data structure from JSON."""

    name: str
    code: str
    description: NotRequired[str]
    aliases: NotRequired[list[str]]
    arrows: NotRequired[str]
    symmetry: NotRequired[str]
    family: NotRequired[str]
    groups: NotRequired[list[str]]
    status: NotRequired[str]
    recognition: NotRequired[RecognitionData]
    optimal_cycles: NotRequired[int]
    optimal_htm: NotRequired[int]
    optimal_stm: NotRequired[int]
    probability: NotRequired[float]
    probability_label: NotRequired[str]
    main: NotRequired[str]
    algorithms: NotRequired[list[str]]
    badmephisto: NotRequired[BadmephistoData]
    logiqx: NotRequired[list[LogiqxAlgorithm]]
    sarah: NotRequired[dict[str, str]]


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
        return self.data.get('family', '')

    @cached_property
    def groups(self) -> list[str]:
        """Groups or classifications for the case."""
        return self.data.get('groups', [])

    @cached_property
    def status(self) -> str:
        """Status of the case (e.g., active, deprecated)."""
        return self.data.get('status', '')

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
    def recognition(self) -> RecognitionData | None:
        """Recognition pattern for identifying the case."""
        return self.data.get('recognition')

    @cached_property
    def optimal_cycles(self) -> int:
        """Optimal number of cycles to solve the case."""
        return self.data.get('optimal_cycles', 0)

    @cached_property
    def optimal_htm(self) -> int:
        """Optimal solution length in Half Turn Metric."""
        return self.data.get('optimal_htm', 0)

    @cached_property
    def optimal_stm(self) -> int:
        """Optimal solution length in Slice Turn Metric."""
        return self.data.get('optimal_stm', 0)

    @cached_property
    def probability(self) -> float:
        """Probability of encountering this case."""
        return self.data.get('probability', 0)

    @cached_property
    def probability_label(self) -> str:
        """Human-readable label for the probability."""
        return self.data.get('probability_label', '')

    @cached_property
    def main_algorithm(self) -> Algorithm:
        """Primary algorithm for solving the case."""
        return parse_moves(self.data.get('main', ''))

    @cached_property
    def algorithms(self) -> list[Algorithm]:
        """All alternative algorithms for solving the case."""
        return [
            parse_moves(moves)
            for moves in self.data.get('algorithms', [])
        ]

    @cached_property
    def setup_algorithms(self) -> list[Algorithm]:
        """Return setup algorithms."""
        return [
            algorithm.transform(mirror_moves)
            for algorithm in self.algorithms
        ]

    @cached_property
    def badmephisto(self) -> BadmephistoData | None:
        """
        BadMephisto informations.

        http://badmephisto.com/
        """
        return self.data.get('badmephisto')

    @cached_property
    def logiqx(self) -> list[LogiqxAlgorithm] | None:
        """
        Logiqx informations.

        https://logiqx.github.io/cubing-algs/html/
        """
        return self.data.get('logiqx')

    @cached_property
    def sarah_pll_skips(self) -> dict[str, str] | None:
        """
        Sarah's cubing site informations.

        https://sarah.cubing.net/3x3x3/pll-skip-cases
        """
        return self.data.get('sarah')

    @cached_property
    def two_phase_algorithms(self) -> list[Algorithm]:
        """Algorithms computed by two-phase algorithm."""
        two_phase_data = cast('list[str]', self.data.get('two-phase', []))
        return [
            parse_moves(moves)
            for moves in two_phase_data
        ]

    @cached_property
    def pretty_name(self) -> str:
        """Return pretty name for case."""
        name = self.name
        if self.aliases:
            name += f' ({ self.aliases[0] })'
        return name

    @cached_property
    def cubing_fache_url(self) -> str:
        """Return cubing.fache.fr URL."""
        if self.method == 'CFOP' and self.step in {'OLL', 'PLL', 'F2L', 'AF2L'}:
            return f'https://cubing.fache.fr/{ self.step }/{ self.code }.html'
        return ''

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
