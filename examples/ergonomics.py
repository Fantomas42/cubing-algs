"""Demonstrate comprehensive algorithm ergonomics analysis."""
# ruff: noqa: T201
import sys

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import HandDominance
from cubing_algs.ergonomics import compute_ergonomics

RESET = '\x1b[0m'
BOLD = '\x1b[1m'

FG_RED = '\x1b[38;5;203m'
FG_GREEN = '\x1b[38;5;77m'
FG_YELLOW = '\x1b[38;5;221m'
FG_BLUE = '\x1b[38;5;75m'
FG_MAGENTA = '\x1b[38;5;177m'
FG_CYAN = '\x1b[38;5;80m'
FG_ORANGE = '\x1b[38;5;215m'
FG_GREY = '\x1b[38;5;244m'
FG_WHITE = '\x1b[38;5;255m'

WIDTH = 70


def colorize(text: str, color: str) -> str:
    """
    Wrap text with ANSI color codes.

    Returns:
        The text surrounded by the given color escape and a reset.

    """
    return f'{color}{text}{RESET}'


def header(title: str, color: str) -> None:
    """Print a section header with a colored rule."""
    rule = colorize('=' * WIDTH, color)
    print(rule)
    print(colorize(f'  {title}', color + BOLD))
    print(rule)


def section(title: str, color: str) -> None:
    """Print a subsection title with a thin rule."""
    print()
    print(colorize(f'▸ {title}', color + BOLD))
    print(colorize('-' * WIDTH, FG_GREY))


def stat(label: str, value: object, *, color: str = FG_CYAN) -> None:
    """Print a label/value pair with aligned columns."""
    label_part = colorize(f'  {label:<26}', FG_GREY)
    value_part = colorize(str(value), color + BOLD)
    print(f'{label_part} {value_part}')


def gradient_color(
    value: float,
    low: float,
    high: float,
    *,
    invert: bool = False,
) -> str:
    """
    Return a color based on where value falls between low and high thresholds.

    Returns:
        Green if good, red if bad, yellow if in between.

    """
    is_good = value >= high
    is_bad = value <= low
    if invert:
        is_good, is_bad = is_bad, is_good
    if is_good:
        return FG_GREEN
    if is_bad:
        return FG_RED
    return FG_YELLOW


def show_ergonomics(algorithm: str) -> None:
    """Display comprehensive ergonomics analysis for an algorithm."""
    print()
    header(f'Algorithm: {algorithm}', FG_MAGENTA)

    algo = Algorithm.parse_moves(algorithm)
    ergo = algo.ergonomics

    section('OVERVIEW', FG_CYAN)
    stat('Total moves', ergo.total_moves, color=FG_WHITE)
    stat(
        'Comfort score',
        f'{ergo.ergonomic_score * 100:.1f}/100',
        color=gradient_color(ergo.ergonomic_score * 100, 40, 70),
    )
    stat('Ergonomic rating', ergo.ergonomic_rating, color=FG_CYAN)
    stat('Difficulty', ergo.difficulty_classification, color=FG_YELLOW)
    stat('Ergonomic score', f'{ergo.ergonomic_score:.2f}', color=FG_MAGENTA)

    section('EXECUTION METRICS', FG_BLUE)
    stat(
        'Estimated time',
        f'{ergo.estimated_execution_time:.2f}s',
        color=FG_CYAN,
    )
    stat(
        'Estimated TPS',
        f'{ergo.estimated_tps:.1f}',
        color=gradient_color(ergo.estimated_tps, 5, 8),
    )
    stat(
        'Flow score',
        f'{ergo.flow_score:.2f}',
        color=gradient_color(ergo.flow_score, 0.4, 0.7),
    )
    stat(
        'Fingertrick difficulty',
        f'{ergo.fingertrick_difficulty:.2f}',
        color=FG_YELLOW,
    )

    section('HAND BALANCE', FG_GREEN)
    stat('Right hand moves', ergo.right_hand_moves, color=FG_CYAN)
    stat('Left hand moves', ergo.left_hand_moves, color=FG_CYAN)
    stat('Both hands moves', ergo.both_hand_moves, color=FG_CYAN)
    stat(
        'Balance ratio',
        f'{ergo.hand_balance_ratio:.2f} (0.5 = perfect)',
        color=gradient_color(
            abs(ergo.hand_balance_ratio - 0.5),
            0.3,
            0.1,
            invert=True,
        ),
    )

    section('FINGER DISTRIBUTION', FG_ORANGE)
    stat('Thumb moves', ergo.thumb_moves, color=FG_YELLOW)
    stat('Index finger moves', ergo.index_finger_moves, color=FG_YELLOW)
    stat('Middle finger moves', ergo.middle_finger_moves, color=FG_YELLOW)
    stat('Ring finger moves', ergo.ring_finger_moves, color=FG_YELLOW)

    section('DIFFICULTY FACTORS', FG_RED)
    stat(
        'Regrips required',
        ergo.regrip_count,
        color=FG_GREEN if ergo.regrip_count == 0 else FG_RED,
    )
    stat(
        'Awkward moves',
        ergo.awkward_moves,
        color=FG_GREEN if ergo.awkward_moves == 0 else FG_YELLOW,
    )

    section('TRIGGER PATTERNS', FG_MAGENTA)
    stat('Triggers detected', ergo.trigger_count, color=FG_MAGENTA)
    stat('Trigger coverage', f'{ergo.trigger_coverage} moves', color=FG_CYAN)
    if ergo.detected_patterns:
        for pattern in ergo.detected_patterns:
            bullet = colorize('•', FG_MAGENTA)
            print(f'    {bullet} {colorize(pattern, FG_WHITE + BOLD)}')

    if ergo.suggestions:
        section('SUGGESTIONS', FG_YELLOW)
        for suggestion in ergo.suggestions:
            bullet = colorize('•', FG_YELLOW)
            print(f'    {bullet} {colorize(suggestion, FG_WHITE)}')

    print()


def compare_algorithms(algorithms: dict[str, str]) -> None:
    """Compare ergonomics of multiple algorithms side by side."""
    print()
    header('ALGORITHM COMPARISON', FG_BLUE)

    results = {}
    for name, alg_str in algorithms.items():
        algo = Algorithm.parse_moves(alg_str)
        results[name] = algo.ergonomics

    names = list(results.keys())
    col_width = max(14, max(len(n) for n in names) + 2)

    header_label = colorize(f'  {"Metric":<26}', FG_GREY + BOLD)
    header_names = ''.join(
        colorize(f'{n:>{col_width}}', FG_CYAN + BOLD) for n in names
    )
    print(f'{header_label}{header_names}')
    print(colorize('  ' + '-' * (26 + col_width * len(names)), FG_GREY))

    rows: list[tuple[str, str, str]] = [
        ('Moves', 'total_moves', ''),
        ('Rating', 'ergonomic_rating', ''),
        ('Difficulty', 'difficulty_classification', ''),
        ('TPS', 'estimated_tps', '.1f'),
        ('Flow', 'flow_score', '.2f'),
        ('Regrips', 'regrip_count', ''),
        ('Triggers', 'trigger_count', ''),
        ('Time (s)', 'estimated_execution_time', '.2f'),
    ]

    for label, attr, fmt in rows:
        line = colorize(f'  {label:<26}', FG_GREY)
        values = [getattr(results[name], attr) for name in names]
        for val in values:
            formatted = f'{val:{fmt}}' if fmt else str(val)
            line += colorize(f'{formatted:>{col_width}}', FG_WHITE + BOLD)
        print(line)

    print()


def show_hand_dominance_comparison(algorithm: str) -> None:
    """Show how hand dominance affects ergonomic scores."""
    print()
    header(f'HAND DOMINANCE ANALYSIS: {algorithm}', FG_GREEN)

    algo = Algorithm.parse_moves(algorithm)

    for dominance in HandDominance:
        ergo = compute_ergonomics(algo, dominance)
        print()
        print(colorize(f'  ▸ {dominance.value.upper()} HANDED', FG_CYAN + BOLD))
        stat(
            '  Ergonomic score',
            f'{ergo.ergonomic_score:.2f}',
            color=FG_MAGENTA,
        )
        stat(
            '  Comfort score',
            f'{ergo.ergonomic_score * 100:.1f}/100',
            color=gradient_color(ergo.ergonomic_score * 100, 40, 70),
        )
        stat(
            '  Estimated TPS',
            f'{ergo.estimated_tps:.1f}',
            color=gradient_color(ergo.estimated_tps, 5, 8),
        )
        stat('  Difficulty', ergo.difficulty_classification, color=FG_YELLOW)

    print()


algos = sys.argv[1:]

if algos:
    for algo in algos:
        show_ergonomics(algo)

    if len(algos) > 1:
        compare_algorithms(
            {
                f'Algo #{ i }': algo
                for i, algo in enumerate(algos)
            },
        )
    for algo in algos:
        show_hand_dominance_comparison(algo)
else:
    # Individual algorithm analysis
    show_ergonomics("R U R' U'")
    show_ergonomics("R U R' U R U2 R'")
    show_ergonomics("R U R' U' R' F R2 U' R' U' R U R' F'")
    show_ergonomics("B' M' U' M B")
    show_ergonomics("y R U R' U' R U R' U' R U R' y'")

    # Side-by-side comparisons
    compare_algorithms({
        'Sexy': "R U R' U'",
        'Sune': "R U R' U R U2 R'",
        'T-Perm': "R U R' U' R' F R2 U' R' U' R U R' F'",
        'Jb-Perm': "R U R' U' R' F R2 U' R' U' R U R' F'",
    })

    compare_algorithms({
        'OLL-21': "F R U R' U' R U R' U' R U R' U' F'",
        'OLL-33': "R U R' U' R' F R F'",
        'OLL-45': "F R U R' U' F'",
    })

    # Hand dominance comparisons
    show_hand_dominance_comparison("R U R' U' R' F R F'")
    show_hand_dominance_comparison("L U L' U' L' F L F'")
