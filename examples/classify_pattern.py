"""Compare classify_pattern() results across multiple algorithms."""
# ruff: noqa: T201
import sys
from typing import NamedTuple

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import CORNER_NAMES
from cubing_algs.constants import EDGE_NAMES
from cubing_algs.impacts import PatternClassification
from cubing_algs.impacts import classify_pattern
from cubing_algs.transform.degrip import degrip_full_moves
from cubing_algs.transform.rotation import remove_ending_rotations
from cubing_algs.vcube import VCube

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

WIDTH = 72

CATEGORY_COLORS: dict[str, str] = {
    'state': FG_GREEN,
    'orientation': FG_CYAN,
    'permutation': FG_BLUE,
    'first_layer': FG_YELLOW,
    'last_layer': FG_MAGENTA,
    'scramble': FG_RED,
    'cycle': FG_WHITE,
}

# Corner twist glyphs: 0=solved, 1=clockwise, 2=counter-clockwise
CO_GLYPHS = {0: '✓', 1: '↻', 2: '↺'}
CO_COLORS = {0: FG_GREEN, 1: FG_YELLOW, 2: FG_YELLOW}


class PatternResult(NamedTuple):
    """Pattern classification with raw orientation arrays."""

    pattern: PatternClassification
    co: list[int]
    eo: list[int]


def colorize(text: str, color: str) -> str:
    """
    Wrap text with an ANSI color code and reset.

    Returns:
        ANSI-colored string.

    """
    return f'{color}{text}{RESET}'


def get_pattern(algorithm_str: str) -> PatternResult:
    """
    Parse and apply an algorithm, returning its pattern classification.

    Returns:
        PatternResult with classification and orientation arrays.

    """
    algo = Algorithm.parse_moves(algorithm_str)
    cleaned = algo.transform(degrip_full_moves, remove_ending_rotations)
    cube = VCube(size=3)
    cube.rotate(cleaned)
    cp, co, ep, eo, *_ = cube.cubies
    return PatternResult(classify_pattern(cp, co, ep, eo), co, eo)


def format_labels(labels: list[str], color: str) -> str:
    """
    Format a list of pattern labels with color, or a dash if empty.

    Returns:
        Comma-separated colored labels, or a grey dash when empty.

    """
    if not labels:
        return colorize('—', FG_GREY)
    return ', '.join(colorize(lbl, color + BOLD) for lbl in labels)


def format_eo_bar(eo: list[int]) -> str:
    """
    Build a compact edge-orientation bar.

    Each edge slot shows its name in green (oriented) or red+bold
    (flipped), followed by a bad-edge count summary.

    Returns:
        Formatted string with colored edge names and a count summary.

    """
    parts: list[str] = []
    bad = 0
    for i, val in enumerate(eo):
        name = EDGE_NAMES[i]
        if val == 0:
            parts.append(colorize(name, FG_GREEN))
        else:
            parts.append(colorize(name, FG_RED + BOLD))
            bad += 1

    # Insert visual gaps between the three edge groups (U, D, middle)
    groups = [' '.join(parts[:4]), ' '.join(parts[4:8]), ' '.join(parts[8:])]
    bar = colorize(' │ ', FG_GREY).join(groups)

    count_color = FG_GREEN if bad == 0 else FG_RED
    summary = colorize(f'{bad}/12 bad', count_color + BOLD)
    return f'{bar}  {summary}'


def format_co_bar(co: list[int]) -> str:
    """
    Build a compact corner-orientation bar.

    Each corner slot shows its name followed by a twist glyph:
    ✓ (solved), ↻ (clockwise), ↺ (counter-clockwise).

    Returns:
        Formatted string with colored corner names and a count summary.

    """
    parts: list[str] = []
    bad = 0
    for i, val in enumerate(co):
        name = CORNER_NAMES[i]
        glyph = CO_GLYPHS[val]
        color = CO_COLORS[val]
        parts.append(colorize(f'{name}{glyph}', color))
        if val != 0:
            bad += 1

    groups = [' '.join(parts[:4]), ' '.join(parts[4:])]
    bar = colorize(' │ ', FG_GREY).join(groups)

    count_color = FG_GREEN if bad == 0 else FG_YELLOW
    summary = colorize(f'{bad}/8 bad', count_color + BOLD)
    return f'{bar}  {summary}'


def print_comparison(algorithms: list[str]) -> None:
    """Print a side-by-side pattern classification for each algorithm."""
    results = [(alg, get_pattern(alg)) for alg in algorithms]

    rule = colorize('=' * WIDTH, FG_MAGENTA)
    print(rule)
    print(colorize('  Pattern Classification Comparison', FG_MAGENTA + BOLD))
    print(rule)

    categories: list[tuple[str, str]] = [
        ('state', 'State'),
        ('orientation', 'Orientation'),
        ('permutation', 'Permutation'),
        ('first_layer', 'First layer'),
        ('last_layer', 'Last layer'),
        ('scramble', 'Scramble'),
        ('cycle', 'Cycle'),
    ]

    for alg, result in results:
        print()
        print(colorize(f'  Algorithm: {alg}', FG_CYAN + BOLD))
        print(colorize('  ' + '-' * (WIDTH - 2), FG_GREY))

        eo_label = colorize(f'    {"EO":<14}', FG_GREY)
        print(f'{eo_label} {format_eo_bar(result.eo)}')

        co_label = colorize(f'    {"CO":<14}', FG_GREY)
        print(f'{co_label} {format_co_bar(result.co)}')

        print(colorize('  ' + '·' * (WIDTH - 2), FG_GREY))

        for field, label in categories:
            labels = getattr(result.pattern, field)
            color = CATEGORY_COLORS[field]
            label_part = colorize(f'    {label:<14}', FG_GREY)
            value_part = format_labels(labels, color)
            print(f'{label_part} {value_part}')


if sys.argv[1:]:
    print_comparison(sys.argv[1:])
else:
    print_comparison([
        'R',
        "R U R' U'",
        "R U R' U R U2 R'",                        # Sune
        "R U R' F' R U R' U' R' F R2 U' R'",      # T-Perm
        'M2 U M2 U2 M2 U M2',                      # Z-Perm
        "R U2 R' U' R U2 L' U R' U' L",            # Niklas (3-cycle)
        "R U R' U' R' F R2 U' R' U' R U R' F'",   # F-Perm
    ])
