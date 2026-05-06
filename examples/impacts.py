"""Demonstrate comprehensive algorithm impact analysis."""
# ruff: noqa: T201
import sys
from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm
from cubing_algs.triggers import TRIGGER_PATTERNS

if TYPE_CHECKING:
    from cubing_algs.impacts import CycleAnalysis
    from cubing_algs.impacts import ImpactData


RESET = '\x1b[0m'
BOLD = '\x1b[1m'
DIM = '\x1b[2m'
ITALIC = '\x1b[3m'

FG_RED = '\x1b[38;5;203m'
FG_GREEN = '\x1b[38;5;77m'
FG_YELLOW = '\x1b[38;5;221m'
FG_BLUE = '\x1b[38;5;75m'
FG_MAGENTA = '\x1b[38;5;177m'
FG_CYAN = '\x1b[38;5;80m'
FG_ORANGE = '\x1b[38;5;215m'
FG_GREY = '\x1b[38;5;244m'
FG_WHITE = '\x1b[38;5;255m'

FACE_COLORS: dict[str, str] = {
    'U': FG_WHITE,
    'R': FG_RED,
    'F': FG_GREEN,
    'D': FG_YELLOW,
    'L': FG_ORANGE,
    'B': FG_BLUE,
}

WIDTH = 70


def colorize(text: str, color: str) -> str:
    """
    Wrap text with ANSI color codes.

    Returns:
        The text surrounded by the given color escape and a reset.

    """
    return f'{color}{text}{RESET}'


def face_colorize(face: str) -> str:
    """
    Colorize a face letter using its canonical cube color.

    Returns:
        The face letter wrapped in its canonical ANSI color.

    """
    color = FACE_COLORS.get(face, FG_WHITE)
    return colorize(face, color + BOLD)


def header(title: str, color: str) -> None:
    """Print a section header with a colored rule."""
    rule = colorize('=' * WIDTH, color)
    print(rule)
    print(colorize(f'  { title }', color + BOLD))
    print(rule)


def section(title: str, color: str) -> None:
    """Print a subsection title with a thin rule."""
    print()
    print(colorize(f'▸ { title }', color + BOLD))
    print(colorize('-' * WIDTH, FG_GREY))


def stat(label: str, value: object, *, color: str = FG_CYAN) -> None:
    """Print a label/value pair with aligned columns."""
    label_part = colorize(f'  {label:<24}', FG_GREY)
    value_part = colorize(str(value), color + BOLD)
    print(f'{label_part} {value_part}')


def check_mark(*, flag: bool) -> str:
    """
    Return a colored ✓ / ✗ depending on the flag.

    Returns:
        Green ✓ when flag is True, red ✗ otherwise.

    """
    if flag:
        return colorize('✓', FG_GREEN + BOLD)
    return colorize('✗', FG_RED + BOLD)


def colorize_mask(mask: str) -> str:
    """
    Highlight '1' bits in a transformation mask.

    Returns:
        The mask with active bits in green and idle bits in grey.

    """
    out: list[str] = []
    for ch in mask:
        if ch == '1':
            out.append(colorize(ch, FG_GREEN + BOLD))
        else:
            out.append(colorize(ch, FG_GREY))
    return ''.join(out)


def colorize_state(state: str) -> str:
    """
    Colorize each facelet in a state string by its face color.

    Returns:
        The state string with each facelet painted with its face color.

    """
    return ''.join(face_colorize(ch) for ch in state)


def print_cycle_info(
    label: str,
    cycles: list[list[int]],
    analysis: 'CycleAnalysis | None',
) -> None:
    """Print cycle details for corners or edges."""
    stat(f'{label} cycles', cycles, color=FG_MAGENTA)
    if analysis is None or analysis.cycle_count == 0:
        return
    stat('  Cycle count', analysis.cycle_count)
    stat('  Cycle lengths', analysis.cycle_lengths)
    if analysis.two_cycles > 0:
        stat('  2-cycles (swaps)', analysis.two_cycles, color=FG_YELLOW)
    if analysis.three_cycles > 0:
        stat('  3-cycles', analysis.three_cycles, color=FG_YELLOW)


def print_distance_metrics(impacts: 'ImpactData') -> None:
    """Print Manhattan and QTM distance metrics."""
    manhattan = impacts.facelets_manhattan_distance
    if manhattan is not None:
        print(colorize('\n  Manhattan distance metrics:', FG_BLUE))
        stat('  Mean displacement', f'{manhattan.mean:.2f}')
        stat('  Max displacement', manhattan.max)
        stat('  Total displacement', manhattan.sum)
    qtm = impacts.facelets_qtm_distance
    if qtm is not None:
        print(colorize('\n  QTM distance metrics:', FG_BLUE))
        stat('  Mean displacement', f'{qtm.mean:.2f}')
        stat('  Max displacement', qtm.max)
        stat('  Total displacement', qtm.sum)


def print_face_analysis(impacts: 'ImpactData') -> None:
    """Print face mobility, face-to-face matrix, and symmetry info."""
    print()
    stat('State', colorize_state(impacts.facelets_state), color=FG_WHITE)
    stat(
        'Transformation mask',
        colorize_mask(impacts.facelets_transformation_mask),
        color=FG_WHITE,
    )

    print(colorize('\n  Face mobility:', FG_BLUE))
    for face, count in impacts.facelets_face_mobility.items():
        label = f'  {face_colorize(face)} face'
        padding = ' ' * (24 - 8)
        bar = '█' * count + colorize('░' * (9 - count), FG_GREY)
        count_color = FG_GREEN if count else FG_GREY
        value = f'{bar} { colorize(f"{count}/9", count_color + BOLD) }'
        print(f'  {label}{padding} {value}')

    print(colorize('\n  Face-to-face matrix:', FG_BLUE))
    for from_face, targets in impacts.facelets_face_to_face_matrix.items():
        flows = ', '.join(
            f'{face_colorize(to_face)}:{colorize(str(count), FG_YELLOW)}'
            for to_face, count in targets.items()
            if count > 0
        )
        if flows:
            arrow = colorize('→', FG_GREY)
            print(f'    {face_colorize(from_face)} {arrow} {flows}')

    print(colorize('\n  Symmetry:', FG_BLUE))
    for axis, is_symmetric in impacts.facelets_symmetry.items():
        stat(f'  {axis}', check_mark(flag=is_symmetric), color=FG_WHITE)

    permutations = impacts.facelets_permutations
    if permutations:
        count = len(permutations)
        stat(
            '\n  Facelet permutations',
            f'{count} facelets moved',
            color=FG_MAGENTA,
        )


def print_facelet_analysis(impacts: 'ImpactData') -> None:
    """Print facelet-based spatial impact analysis."""
    section('FACELET ANALYSIS (Visual/Spatial Impact)', FG_CYAN)
    stat('Fixed facelets', f'{impacts.facelets_fixed_count}/54', color=FG_GREEN)
    stat(
        'Mobilized facelets',
        f'{impacts.facelets_mobilized_count}/54',
        color=FG_YELLOW,
    )
    stat(
        'Scrambled percent',
        f'{impacts.facelets_scrambled_percent:.1%}',
        color=FG_MAGENTA,
    )

    print_distance_metrics(impacts)
    print_face_analysis(impacts)

    piece_types = impacts.facelets_piece_type_impact
    print(colorize('\n  Piece type impact:', FG_BLUE))
    for piece_type, count in sorted(piece_types.items()):
        stat(f'  {piece_type}', count, color=FG_YELLOW)


def print_parity_info(impacts: 'ImpactData') -> None:
    """Print parity values and signature details."""
    print(colorize('\n  Parity:', FG_BLUE))
    corner_parity = impacts.cubies_corner_parity
    corner_label = 'even' if corner_parity == 0 else 'odd'
    corner_color = FG_GREEN if corner_parity == 0 else FG_YELLOW
    stat(
        '  Corner parity',
        f'{corner_parity} ({corner_label})',
        color=corner_color,
    )
    edge_parity = impacts.cubies_edge_parity
    edge_label = 'even' if edge_parity == 0 else 'odd'
    edge_color = FG_GREEN if edge_parity == 0 else FG_YELLOW
    stat('  Edge parity', f'{edge_parity} ({edge_label})', color=edge_color)
    stat('  Parity valid', check_mark(flag=bool(impacts.cubies_parity_valid)))

    signature = impacts.cubies_parity_signature
    if signature is None:
        return
    print(colorize('\n  Parity signature:', FG_BLUE))
    stat('  Signature', signature.signature, color=FG_MAGENTA)
    stat('  Valid', check_mark(flag=signature.is_valid))
    if signature.implications:
        print(colorize('    Implications:', FG_GREY))
        for implication in signature.implications:
            bullet = colorize('•', FG_MAGENTA)
            print(f'      {bullet} {colorize(implication, FG_WHITE)}')


def print_cubie_analysis(impacts: 'ImpactData') -> None:
    """Print cubie-based piece-level impact analysis."""
    section('CUBIE ANALYSIS (Piece-Level Impact)', FG_MAGENTA)
    stat('Corners moved', f'{impacts.cubies_corners_moved}/8', color=FG_YELLOW)
    stat(
        'Corners twisted',
        f'{impacts.cubies_corners_twisted}/8',
        color=FG_YELLOW,
    )
    stat('Edges moved', f'{impacts.cubies_edges_moved}/12', color=FG_YELLOW)
    stat('Edges flipped', f'{impacts.cubies_edges_flipped}/12', color=FG_YELLOW)

    print(colorize('\n  Raw cubie arrays:', FG_BLUE))
    stat(
        '  Corner permutation',
        impacts.cubies_corner_permutation,
        color=FG_WHITE,
    )
    stat(
        '  Corner orientation',
        impacts.cubies_corner_orientation,
        color=FG_WHITE,
    )
    stat('  Edge permutation', impacts.cubies_edge_permutation, color=FG_WHITE)
    stat('  Edge orientation', impacts.cubies_edge_orientation, color=FG_WHITE)

    print_parity_info(impacts)

    if impacts.cubies_corner_cycles:
        print()
        print_cycle_info(
            'Corner cycles',
            impacts.cubies_corner_cycles,
            impacts.cubies_corner_cycle_analysis,
        )

    if impacts.cubies_edge_cycles:
        print()
        print_cycle_info(
            'Edge cycles',
            impacts.cubies_edge_cycles,
            impacts.cubies_edge_cycle_analysis,
        )

    print()
    stat(
        'Complexity score',
        impacts.cubies_complexity_score,
        color=FG_MAGENTA,
    )
    stat(
        'Suggested approach',
        impacts.cubies_suggested_approach,
        color=FG_CYAN,
    )

    patterns = impacts.cubies_patterns
    if patterns is not None:
        print(colorize('\n  Pattern classification:', FG_BLUE))
        categories: list[tuple[str, list[str]]] = [
            ('State', patterns.state),
            ('Orientation', patterns.orientation),
            ('Permutation', patterns.permutation),
            ('First layer', patterns.first_layer),
            ('Last layer', patterns.last_layer),
            ('Scramble', patterns.scramble),
            ('Cycle', patterns.cycle),
        ]
        for category, labels in categories:
            if not labels:
                continue
            print(f'    {colorize(category, FG_CYAN + BOLD)}')
            for pattern in labels:
                bullet = colorize('•', FG_MAGENTA)
                print(f'      {bullet} {colorize(pattern, FG_WHITE + BOLD)}')


def show_impact(algorithm: str) -> None:
    """Display comprehensive impact analysis for an algorithm."""
    print()
    header(f'Algorithm: { algorithm }', FG_MAGENTA)

    algo = Algorithm.parse_moves(algorithm)
    impacts = algo.impacts()

    print_facelet_analysis(impacts)
    print_cubie_analysis(impacts)

    section('CUBE VISUALIZATION', FG_GREEN)
    algo.show()


if '--triggers' in sys.argv[1:]:
    for trigger in TRIGGER_PATTERNS:
        show_impact(trigger.moves)
elif sys.argv[1:]:
    for arg in sys.argv[1:]:
        show_impact(arg)
else:
    # Default examples demonstrating different types of algorithms
    show_impact('R')
    show_impact("R'")
    show_impact("R U R' U'")
    show_impact("R U R' U R U2 R'")  # Sune
    show_impact("R U R' F' R U R' U' R' F R2 U' R'")  # T-Perm
