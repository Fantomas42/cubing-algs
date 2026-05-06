"""Demonstrate comprehensive algorithm structure analysis."""
# ruff: noqa: T201
from cubing_algs.algorithm import Algorithm

RESET = '\x1b[0m'
BOLD = '\x1b[1m'

FG_RED = '\x1b[38;5;203m'
FG_GREEN = '\x1b[38;5;77m'
FG_YELLOW = '\x1b[38;5;221m'
FG_BLUE = '\x1b[38;5;75m'
FG_MAGENTA = '\x1b[38;5;177m'
FG_CYAN = '\x1b[38;5;80m'
FG_GREY = '\x1b[38;5;244m'
FG_WHITE = '\x1b[38;5;255m'

WIDTH = 70
COVERAGE_THRESHOLD = 0.8
SCORE_HIGH = 0.7
SCORE_MID = 0.4


def colorize(text: str, color: str) -> str:
    """
    Wrap text with ANSI color codes.

    Returns:
        The text surrounded by the given color escape and a reset.

    """
    return f'{color}{text}{RESET}'


def header(title: str) -> None:
    """Print a section header with a colored rule."""
    rule = colorize('=' * WIDTH, FG_CYAN)
    print()
    print(rule)
    print(colorize(f'  {title}', FG_CYAN + BOLD))
    print(rule)


def section(title: str) -> None:
    """Print a subsection title with a thin rule."""
    print()
    print(colorize(f'▸ {title}', FG_BLUE + BOLD))
    print(colorize('-' * WIDTH, FG_GREY))


def stat(label: str, value: object, *, color: str = FG_CYAN) -> None:
    """Print a label/value pair with aligned columns."""
    label_part = colorize(f'  {label:<24}', FG_GREY)
    value_part = colorize(str(value), color + BOLD)
    print(f'{label_part} {value_part}')


def show_structure(algorithm: str) -> None:  # noqa: PLR0915
    """Display comprehensive structure analysis for an algorithm."""
    header(f'Algorithm: {algorithm}')

    algo = Algorithm.parse_moves(algorithm)
    struct = algo.structure

    section('BASIC INFORMATION')
    stat('Original', struct.original, color=FG_WHITE)
    stat('Compressed', struct.compressed, color=FG_WHITE)
    stat('Move count', f'{struct.original_length} moves', color=FG_YELLOW)

    section('STRUCTURE DETECTION')
    stat('Total structures', struct.total_structures, color=FG_MAGENTA)
    stat('Conjugates', struct.conjugate_count)
    stat('Commutators', struct.commutator_count)
    stat('Max nesting depth', struct.max_nesting_depth)
    stat('Nested structures', struct.nested_structure_count)

    section('COMPRESSION ANALYSIS')
    stat('Original length', f'{len(struct.original)} chars', color=FG_YELLOW)
    stat(
        'Compressed length',
        f'{struct.compressed_notation_char_length} chars',
        color=FG_YELLOW,
    )
    ratio_color = FG_GREEN if struct.compression_ratio < 1.0 else FG_GREY
    stat(
        'Compression ratio',
        f'{struct.compression_ratio:.1%}',
        color=ratio_color,
    )

    section('QUALITY METRICS')
    stat(
        'Average score',
        f'{struct.average_structure_score:.2f}',
        color=FG_CYAN,
    )
    stat('Best score', f'{struct.best_structure_score:.2f}', color=FG_GREEN)

    if struct.total_structures > 0:
        section('SETUP AND ACTION ANALYSIS')
        stat(
            'Setup lengths',
            f'{struct.shortest_setup_length}-{struct.longest_setup_length} '
            f'(avg: {struct.average_setup_length:.1f})',
            color=FG_CYAN,
        )
        stat(
            'Action lengths',
            f'{struct.shortest_action_length}-{struct.longest_action_length} '
            f'(avg: {struct.average_action_length:.1f})',
            color=FG_CYAN,
        )

    section('COVERAGE ANALYSIS')
    coverage_color = (
        FG_GREEN if struct.coverage_ratio >= COVERAGE_THRESHOLD else FG_YELLOW
    )
    stat('Coverage', f'{struct.coverage_ratio:.1%}', color=coverage_color)
    uncovered_color = FG_GREY if struct.uncovered_moves == 0 else FG_RED
    stat('Uncovered moves', struct.uncovered_moves, color=uncovered_color)

    section('CLASSIFICATION STATISTICS')
    stat('Pure commutators', struct.pure_commutator_count, color=FG_GREEN)
    stat('A9 commutators', struct.a9_commutator_count, color=FG_CYAN)
    stat('Nested conjugates', struct.nested_conjugate_count, color=FG_MAGENTA)
    stat('Simple conjugates', struct.simple_conjugate_count, color=FG_CYAN)
    stat(
        'With cancellations',
        struct.structures_with_cancellations,
        color=FG_YELLOW,
    )
    stat(
        'Avg moves/structure',
        f'{struct.average_move_count:.1f}',
        color=FG_CYAN,
    )
    stat('Efficiency rating', struct.efficiency_rating, color=FG_MAGENTA)

    if struct.structures:
        section('DETAILED STRUCTURES')
        for idx, s in enumerate(struct.structures, 1):
            type_str = colorize(s.type.capitalize(), FG_BLUE + BOLD)
            notation_str = colorize(str(s), FG_WHITE + BOLD)

            class_tag = (
                colorize(f' [{s.classification}]', FG_CYAN)
                if s.classification
                else ''
            )
            pure_tag = (
                colorize(' (PURE)', FG_GREEN + BOLD) if s.is_pure else ''
            )
            cancel_tag = (
                colorize(' *cancels*', FG_YELLOW) if s.has_cancellations else ''
            )

            line = (
                f'  {colorize(str(idx), FG_GREY)}. '
                f'{type_str}: {notation_str}'
                f'{class_tag}{pure_tag}{cancel_tag}'
            )
            print(line)
            score_color = (
                FG_GREEN
                if s.score >= SCORE_HIGH
                else FG_YELLOW
                if s.score >= SCORE_MID
                else FG_RED
            )
            print(
                f'     {colorize("Score:", FG_GREY)} '
                f'{colorize(f"{s.score:.2f}", score_color + BOLD)}'
                f'  {colorize("Moves:", FG_GREY)} '
                f'{colorize(str(s.move_count), FG_CYAN + BOLD)}',
            )
            print(
                f'     {colorize("Setup:", FG_GREY)} '
                f'{colorize(str(s.setup), FG_WHITE)}'
                f' {colorize(f"({len(s.setup)} moves)", FG_GREY)}',
            )
            print(
                f'     {colorize("Action:", FG_GREY)} '
                f'{colorize(str(s.action), FG_WHITE)}'
                f' {colorize(f"({len(s.action)} moves)", FG_GREY)}',
            )
            print(
                f'     {colorize("Position:", FG_GREY)} '
                f'{colorize(f"{s.start}-{s.end}", FG_CYAN)}',
            )
    else:
        print()
        print(colorize('  No structures found.', FG_GREY))

    print()


# Examples demonstrating different types of algorithms
# Simple move - no structure
show_structure('R')
# Simple commutator
show_structure("R U R' U'")
# Sune - simple algorithm
show_structure("R U R' U R U2 R'")
# Sexy move with setup
show_structure("F R U R' U' F'")
# T-Perm - complex structure
show_structure("R U R' F' R U R' U' R' F R2 U' R'")
# Jb-Perm
show_structure("R U R' U' R' F R2 U' R' U' R U R' F'")
