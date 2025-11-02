"""
Metrics and analysis tools for Rubik's cube algorithms.

This module provides functions to calculate various metrics for evaluating
and comparing Rubik's cube algorithms. These metrics are different systems
for counting moves in an algorithm, each with its own rules and applications.

Supported Metrics
-----------------

**HTM (Half Turn Metric) / OBTM (Outer Block Turn Metric)**
    Any turn of any face, by any angle, counts as 1 turn. Slice moves count as
    2 turns since centers are assumed to be fixed. Rotations don't count.
    This is the official WCA metric (OBTM).

    - God's Number: 20 moves
    - Example: R U2 F M2 = 1+1+1+2 = 5 HTM

**QTM (Quarter Turn Metric)**
    Any 90-degree turn counts as 1 turn; 180-degree turns count as 2 turns.
    Slice moves count as 2 per quarter turn. Rotations don't count.

    - God's Number: 26 moves
    - Example: R U2 F M2 = 1+2+1+4 = 8 QTM

**STM (Slice Turn Metric)**
    Any turn of any layer, by any angle, counts as 1 turn. Unlike HTM, slice
    moves count as only 1 turn. Popular with Roux method users.

    - God's Number: 18-20 moves (unproven)
    - Example: R U2 F M2 = 1+1+1+1 = 4 STM

**QSTM (Quarter Slice Turn Metric)**
    90-degree turns of any layer count as 1 turn; 180-degree turns count as 2.
    Slice moves count the same as outer moves.

    - God's Number: ~23-26 moves (estimated)
    - Example: R U2 F M2 = 1+2+1+2 = 6 QSTM

**ETM (Execution Turn Metric)**
    Any perceived movement counts as a turn, including rotations. Designed for
    measuring actual moves executed during solving.

    - Example: R U2 F M2 x = 1+1+1+1+1 = 5 ETM

**RTM (Rotation Turn Metric)**
    Counts only rotations. Quarter rotations count as 1, half rotations as 2.
    Useful for analyzing regrips and cube reorientations.

    - Example: x y2 z = 1+2+1 = 4 RTM

**BTM (Block Turn Metric)**
    Any group of contiguous slices moving the same way counts as 1 move.
    Designed for big cubes (4x4x4, 5x5x5, etc.) where multiple layers can move
    together. Identical to STM for counting purposes.

    - Example: R U2 F M2 = 1+1+1+1 = 4 BTM
    - Big cube example: 2R 3Rw U 2-3r = 1+1+1+1 = 4 BTM

**BQTM (Block Quarter Turn Metric)**
    Same as BTM but 90-degree turns count as 1, 180-degree turns count as 2.
    Quarter-turn variant of BTM for big cubes.

    - Example: R U2 F M2 = 1+2+1+2 = 6 BQTM

References
----------
- https://www.speedsolving.com/wiki/index.php?title=Metric
- https://www.speedsolving.com/wiki/index.php?title=God%27s_Number

"""
import operator
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.move import Move

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


class MetricsData(NamedTuple):
    """
    Container for algorithm metrics computation results.

    Attributes:
        pauses: Number of pause moves (.) in the algorithm.
        rotations: Number of cube rotations (x, y, z).
        outer_moves: Number of outer face moves (R, U, F, etc.) and wide
            moves (Rw, Uw, etc.).
        inner_moves: Number of inner slice moves (M, E, S).
        htm: Half Turn Metric score (also known as OBTM).
        qtm: Quarter Turn Metric score (also known as OBQTM).
        stm: Slice Turn Metric score (also known as BTM, RBTM).
        etm: Execution Turn Metric score (includes rotations).
        rtm: Rotation Turn Metric score (only rotations).
        qstm: Quarter Slice Turn Metric score (also known as BQTM).
        generators: List of face names sorted by usage frequency.

    Properties (aliases):
        obtm: Alias for htm (Outer Block Turn Metric).
        obqtm: Alias for qtm (Outer Block Quantum Turn Metric).
        rbtm: Alias for stm (Range Block Turn Metric).
        btm: Alias for stm (Block Turn Metric).
        bqtm: Alias for qstm (Block Quarter Turn Metric).

    """

    pauses: int
    rotations: int
    outer_moves: int
    inner_moves: int
    htm: int
    qtm: int
    stm: int
    etm: int
    rtm: int
    qstm: int
    generators: list[str]

    @property
    def obtm(self) -> int:
        """
        Outer Block Turn Metric (OBTM) - alias for HTM.

        OBTM is the official WCA metric and is identical to HTM.
        Inner block moves count as 2 turns, outer block moves as 1,
        rotations as 0.

        Returns:
            The HTM/OBTM score.

        """
        return self.htm

    @property
    def obqtm(self) -> int:
        """
        Outer Block Quantum Turn Metric (OBQTM) - alias for QTM.

        OBQTM uses quarter-turn counting for outer block moves.
        Inner block moves count as 2 turns per quantum, outer block
        moves count as 1 turn per quantum, rotations count as 0.

        Returns:
            The QTM/OBQTM score.

        """
        return self.qtm

    @property
    def rbtm(self) -> int:
        """
        Range Block Turn Metric (RBTM) - alias for STM.

        RBTM counts any layer turn as 1 move regardless of whether
        it's inner or outer. Identical counting rules to STM.

        Returns:
            The STM/RBTM score.

        """
        return self.stm

    @property
    def btm(self) -> int:
        """
        Block Turn Metric (BTM) - alias for STM.

        BTM is used for big cubes and counts any contiguous block of layers
        as a single move. It uses identical counting rules to STM and RBTM.

        Returns:
            The STM/BTM/RBTM score.

        """
        return self.stm

    @property
    def bqtm(self) -> int:
        """
        Block Quarter Turn Metric (BQTM) - alias for QSTM.

        BQTM is the quarter-turn variant of BTM for big cubes. It uses
        identical counting rules to QSTM.

        Returns:
            The QSTM/BQTM score.

        """
        return self.qstm


# Dictionary mapping metric names to scoring rules for different move types.
# Each entry maps to [base_count, quantum_multiplier]:
#   - base_count: added for each move regardless of angle
#   - quantum_multiplier: multiplied by move's quantum count
#     (1 for quarter, 2 for half)
#
# Examples for move R2 (half turn):
#   HTM: 1 + (2 * 0) = 1    (half turns count as 1)
#   QTM: 0 + (2 * 1) = 2    (half turns count as 2)
#   STM: 1 + (2 * 0) = 1    (all turns count as 1)
#
# Examples for slice move M2 (inner, half turn):
#   HTM: 2 + (2 * 0) = 2    (slice moves count double)
#   QTM: 0 + (2 * 2) = 4    (slice quarter = 2, slice half = 4)
#   STM: 1 + (2 * 0) = 1    (slice moves count as 1)
MOVE_COUNTS = {
    'htm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [2, 0]},
    'qtm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 2]},
    'stm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'etm': {'rotation': [1, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'rtm': {'rotation': [0, 1], 'outer': [0, 0], 'inner': [0, 0]},
    'qstm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 1]},
    'obtm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [2, 0]},
}


def amount(move: Move) -> int:
    """
    Determine the quantum factor for a move.

    Double moves (like U2) count as 2, while single moves count as 1.
    This is used for quarter-turn based metrics (QTM, QSTM, RTM).

    Args:
        move: The move to evaluate.

    Returns:
        2 for double moves (180°), 1 for single moves (90°).

    Examples:
        >>> amount(parse_moves("R")[0])   # Quarter turn
        1
        >>> amount(parse_moves("R2")[0])  # Half turn
        2
        >>> amount(parse_moves("R'")[0])  # Quarter turn (inverse)
        1

    """
    if move.is_double:
        return 2
    return 1


def move_score(mode: str, field: str,
               moves: list[Move]) -> int:
    """
    Calculate the score for a specific group of moves under a given metric.

    Uses the MOVE_COUNTS dictionary to determine how to score each move
    based on the metric mode and move type. The score is calculated as:
    base_count + (quantum_count * quantum_multiplier) for each move.

    Args:
        mode: The metric mode (htm, qtm, stm, etm, rtm, qstm, obtm).
        field: The move field type (rotation, outer, inner).
        moves: List of moves to score.

    Returns:
        The total score for the moves under the specified metric.

    Examples:
        For outer moves [R, U2] in HTM:
            R: 1 + (1 * 0) = 1
            U2: 1 + (2 * 0) = 1
            Total: 2

        For outer moves [R, U2] in QTM:
            R: 0 + (1 * 1) = 1
            U2: 0 + (2 * 1) = 2
            Total: 3

    """
    datas = MOVE_COUNTS[mode][field]

    return sum(
        datas[0] + (amount(move) * datas[1])
        for move in moves
    )


def compute_score(mode: str,
                  rotations: list[Move],
                  outer: list[Move],
                  inner: list[Move]) -> int:
    """
    Compute the total score for an algorithm under a specific metric.

    Combines scores from all move types (rotations, outer, and inner moves)
    according to the rules of the specified metric.

    Args:
        mode: The metric mode (htm, qtm, stm, etm, rtm, qstm, obtm).
        rotations: List of rotation moves (x, y, z).
        outer: List of outer face moves (R, U, F, Rw, etc.).
        inner: List of inner slice moves (M, E, S).

    Returns:
        The total score combining all move types.

    Examples:
        For algorithm "R U R' U'" (sexy move):
            - All metrics count it as 4 moves (no rotations, no slices)

        For algorithm "M2 U M2 U2":
            - HTM: 2+1+2+1 = 6 (slice moves count double)
            - QTM: 4+1+4+2 = 11 (M2 counts as 4, U2 counts as 2)
            - STM: 1+1+1+1 = 4 (all moves count as 1)

    """
    return (
        move_score(mode, 'rotation', rotations)
        + move_score(mode, 'outer', outer)
        + move_score(mode, 'inner', inner)
    )


def compute_generators(moves: 'Algorithm') -> list[str]:
    """
    Identify the most frequently used move faces in an algorithm.

    This function counts how many times each face is turned (ignoring
    direction and whether it's a single or double turn) and returns them in
    order of frequency. Rotations and pauses are excluded from this analysis.

    This is useful for understanding which faces an algorithm primarily
    affects, which can help with method classification (e.g., RU algorithms
    only use R and U).

    Args:
        moves: The algorithm to analyze.

    Returns:
        List of face names sorted by frequency (most frequent first).

    Examples:
        >>> compute_generators(parse_moves("R U R' U'"))
        ['R', 'U']

        >>> compute_generators(parse_moves("R U R U R U' R'"))
        ['R', 'U']  # R appears 4 times, U appears 3 times

        >>> compute_generators(parse_moves("M2 U M2 U2"))
        ['M', 'U']  # M appears 2 times, U appears 2 times

    """
    count: dict[str, int] = {}
    for move in moves:
        if move.is_rotation_move or move.is_pause:
            continue

        count.setdefault(move.raw_base_move, 0)
        count[move.raw_base_move] += 1

    return [
        k
        for k, v in sorted(
                count.items(),
                key=operator.itemgetter(1),
                reverse=True,
        )
    ]


def regroup_moves(
        moves: 'Algorithm',
) -> tuple[list[Move], list[Move], list[Move], list[Move]]:
    """
    Categorize moves into pause, rotation, outer, and inner move types.

    This separation is necessary for accurate metric calculations, as different
    move types are counted differently depending on the metric.

    Args:
        moves: The algorithm to categorize.

    Returns:
        Tuple of (pauses, rotations, outer_moves, inner_moves) lists.

    """
    pauses = []
    rotations = []
    outer_moves = []
    inner_moves = []

    for move in moves:
        if move.is_pause:
            pauses.append(move)
        elif move.is_outer_move:
            outer_moves.append(move)
        elif move.is_inner_move:
            inner_moves.append(move)
        else:
            rotations.append(move)

    return pauses, rotations, outer_moves, inner_moves


def compute_metrics(moves: 'Algorithm') -> MetricsData:
    """
    Calculate a comprehensive set of metrics for an algorithm.

    This is the main entry point for algorithm analysis. It computes:
    - Move counts by type (rotations, outer moves, inner moves, pauses)
    - All standard metrics with their various aliases
    - Generator analysis (most frequently used faces)

    Args:
        moves: The algorithm to analyze.

    Returns:
        MetricsData: Namedtuple containing all calculated metrics:
            - pauses: Number of pause moves (.)
            - rotations: Number of rotation moves (x, y, z)
            - outer_moves: Number of outer face moves (R, U, F, Rw, etc.)
            - inner_moves: Number of inner slice moves (M, E, S)
            - htm: Half Turn Metric score
            - qtm: Quarter Turn Metric score
            - stm: Slice Turn Metric score
            - etm: Execution Turn Metric score
            - rtm: Rotation Turn Metric score
            - qstm: Quarter Slice Turn Metric score
            - generators: List of most frequently used faces
            - obtm: Property alias for htm (Outer Block Turn Metric)
            - obqtm: Property alias for qtm (Outer Block Quantum Turn Metric)
            - rbtm: Property alias for stm (Range Block Turn Metric)
            - btm: Property alias for stm (Block Turn Metric)
            - bqtm: Property alias for qstm (Block Quarter Turn Metric)

    Examples:
        >>> algo = parse_moves("R U R' U'")
        >>> metrics = compute_metrics(algo)
        >>> metrics.htm
        4
        >>> metrics.generators
        ['R', 'U']

        >>> algo = parse_moves("M2 U M2 U2")
        >>> metrics = compute_metrics(algo)
        >>> metrics.htm  # M2 counts as 2
        6
        >>> metrics.stm  # M2 counts as 1
        4
        >>> metrics.btm  # M2 counts as 1 (same as STM)
        4
        >>> metrics.qtm  # M2 counts as 4, U2 counts as 2
        11
        >>> metrics.bqtm  # M2 counts as 2, U2 counts as 2 (same as QSTM)
        6

        >>> algo = parse_moves("x R U R' U' x'")
        >>> metrics = compute_metrics(algo)
        >>> metrics.htm  # Rotations don't count
        4
        >>> metrics.etm  # Rotations do count
        6
        >>> metrics.rtm  # Only rotations count
        2

    Note:
        The MetricsData.obtm property returns the same value as htm,
        as OBTM is an alias for HTM and represents the official WCA metric.

        BTM and STM produce identical counts for 3x3x3 cubes. The distinction
        becomes meaningful on big cubes where BTM treats any contiguous block
        of layers as a single move.

    """
    pauses, rotations, outer_moves, inner_moves = regroup_moves(moves)

    return MetricsData(
        pauses=len(pauses),
        rotations=len(rotations),
        outer_moves=len(outer_moves),
        inner_moves=len(inner_moves),
        htm=compute_score('htm', rotations, outer_moves, inner_moves),
        qtm=compute_score('qtm', rotations, outer_moves, inner_moves),
        stm=compute_score('stm', rotations, outer_moves, inner_moves),
        etm=compute_score('etm', rotations, outer_moves, inner_moves),
        rtm=compute_score('rtm', rotations, outer_moves, inner_moves),
        qstm=compute_score('qstm', rotations, outer_moves, inner_moves),
        generators=compute_generators(moves),
    )
