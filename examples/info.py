"""Display a text resume of an algorithm based on its to_dict() data."""
import argparse
import json
from typing import Any

from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.parsing import parse_moves

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

FACE_COLORS: dict[str, str] = {
    'U': FG_WHITE,
    'R': FG_RED,
    'F': FG_GREEN,
    'D': FG_YELLOW,
    'L': FG_ORANGE,
    'B': FG_BLUE,
}

WIDTH = 70
COVERAGE_THRESHOLD = 0.8


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


def stat_raw(label: str, value: str) -> None:
    """Print a label with an already-colored value, unchanged."""
    label_part = colorize(f'  {label:<26}', FG_GREY)
    print(f'{label_part} {value}')


def gradient_color(value: float, low: float, high: float) -> str:
    """
    Return a color based on where value falls between low and high thresholds.

    Returns:
        Green if good, red if bad, yellow if in between.

    """
    if value >= high:
        return FG_GREEN
    if value <= low:
        return FG_RED
    return FG_YELLOW


def yesno(*, value: bool) -> str:
    """
    Format a boolean as a colored Yes/No.

    Returns:
        Green 'Yes' when value is truthy, otherwise red 'No'.

    """
    return colorize('Yes', FG_GREEN + BOLD) if value else colorize('No', FG_RED)


def print_overview(data: dict[str, Any], size: int) -> None:
    """Print the algorithm overview block."""
    header(f'Algorithm: {data["moves"]}', FG_MAGENTA)
    stat('Cube size', f'{size}x{size}x{size}', color=FG_WHITE)

    section('OVERVIEW', FG_CYAN)
    stat('Cycles', data['cycles'], color=FG_YELLOW)
    stat('Minimum cube size', data['min_cube_size'], color=FG_YELLOW)
    stat('Standard notation', yesno(value=data['is_standard']))
    stat('SiGN notation', yesno(value=data['is_sign']))
    stat('Has rotations', yesno(value=data['has_rotations']))
    stat(
        'Has internal rotations',
        yesno(value=data['has_internal_rotations']),
    )
    stat('Has pauses', yesno(value=data['has_pauses']))
    stat('Has times', yesno(value=data['has_times']))


def print_metrics(metrics: dict[str, Any]) -> None:
    """Print move metrics."""
    section('METRICS', FG_BLUE)
    stat('HTM (half turn)', metrics['htm'], color=FG_YELLOW)
    stat('QTM (quarter turn)', metrics['qtm'], color=FG_YELLOW)
    stat('STM (slice turn)', metrics['stm'], color=FG_YELLOW)
    stat('ETM (execution)', metrics['etm'], color=FG_YELLOW)
    stat('QSTM', metrics['qstm'], color=FG_YELLOW)
    stat('RTM (rotations)', metrics['rtm'], color=FG_YELLOW)
    stat('Outer moves', metrics['outer_moves'], color=FG_CYAN)
    stat('Inner moves', metrics['inner_moves'], color=FG_CYAN)
    stat('Rotations', metrics['rotations'], color=FG_CYAN)
    stat('Pauses', metrics['pauses'], color=FG_CYAN)
    stat('Generators', ', '.join(metrics['generators']), color=FG_WHITE)


def print_ergonomics(ergo: dict[str, Any]) -> None:
    """Print ergonomics information."""
    section('ERGONOMICS', FG_GREEN)
    stat('Rating', ergo['ergonomic_rating'], color=FG_CYAN)
    stat('Difficulty', ergo['difficulty_classification'], color=FG_YELLOW)
    stat(
        'Ergonomic score',
        f'{ergo["ergonomic_score"]:.3f}',
        color=gradient_color(ergo['ergonomic_score'], 0.4, 0.7),
    )
    stat(
        'Flow score',
        f'{ergo["flow_score"]:.3f}',
        color=gradient_color(ergo['flow_score'], 0.4, 0.7),
    )
    stat(
        'Estimated TPS',
        f'{ergo["estimated_tps"]:.2f}',
        color=gradient_color(ergo['estimated_tps'], 5, 8),
    )
    stat(
        'Execution time',
        f'{ergo["estimated_execution_time"]:.2f}s',
        color=FG_CYAN,
    )
    stat(
        'Hand usage (R/L/both)',
        f'{ergo["right_hand_moves"]} / '
        f'{ergo["left_hand_moves"]} / '
        f'{ergo["both_hand_moves"]}',
        color=FG_WHITE,
    )
    stat(
        'Hand balance ratio',
        f'{ergo["hand_balance_ratio"]:.2f}',
        color=gradient_color(ergo['hand_balance_ratio'], 0.4, 0.8),
    )
    stat(
        'Regrips',
        ergo['regrip_count'],
        color=FG_GREEN if ergo['regrip_count'] == 0 else FG_RED,
    )
    stat(
        'Awkward moves',
        ergo['awkward_moves'],
        color=FG_GREEN if ergo['awkward_moves'] == 0 else FG_YELLOW,
    )
    stat(
        'Triggers',
        f'{ergo["trigger_count"]} (coverage {ergo["trigger_coverage"]})',
        color=FG_MAGENTA,
    )
    if ergo.get('detected_patterns'):
        stat(
            'Detected patterns',
            ', '.join(ergo['detected_patterns']),
            color=FG_WHITE,
        )
    if ergo.get('suggestions'):
        print(colorize('\n  Suggestions:', FG_YELLOW))
        for suggestion in ergo['suggestions']:
            bullet = colorize('•', FG_YELLOW)
            print(f'    {bullet} {colorize(suggestion, FG_WHITE)}')


def print_structure(struct: dict[str, Any]) -> None:
    """Print structural analysis."""
    section('STRUCTURE', FG_MAGENTA)
    stat('Compressed', struct['compressed'], color=FG_WHITE)
    stat('Efficiency rating', struct['efficiency_rating'], color=FG_CYAN)
    stat('Total structures', struct['total_structures'], color=FG_MAGENTA)
    stat('Conjugates', struct['conjugate_count'], color=FG_YELLOW)
    stat('Commutators', struct['commutator_count'], color=FG_YELLOW)
    stat('Pure commutators', struct['pure_commutator_count'], color=FG_GREEN)
    stat('Max nesting depth', struct['max_nesting_depth'], color=FG_YELLOW)
    stat(
        'Compression ratio',
        f'{struct["compression_ratio"]:.2%}',
        color=FG_GREEN if struct['compression_ratio'] < 1.0 else FG_GREY,
    )
    coverage_color = (
        FG_GREEN
        if struct['coverage_ratio'] >= COVERAGE_THRESHOLD
        else FG_YELLOW
    )
    stat(
        'Coverage',
        f'{struct["coverage_ratio"]:.0%} '
        f'({struct["uncovered_moves"]} uncovered)',
        color=coverage_color,
    )
    stat(
        'Best structure score',
        f'{struct["best_structure_score"]:.2f}',
        color=FG_CYAN,
    )


def print_memory(mem: dict[str, Any]) -> None:
    """Print memorization difficulty."""
    section('MEMORY', FG_BLUE)
    stat('Rating', mem['memory_rating'], color=FG_CYAN)
    stat(
        'Score',
        f'{mem["memory_score"]:.3f}',
        color=gradient_color(mem['memory_score'], 0.4, 0.7),
    )
    stat('Move count', mem['move_count'], color=FG_YELLOW)
    stat('Effective chunks', mem['effective_chunks'], color=FG_YELLOW)
    stat('Distinct triggers', mem['distinct_triggers'], color=FG_YELLOW)
    stat(
        'Trigger coverage',
        f'{mem["trigger_coverage_percent"]:.0%}',
        color=FG_CYAN,
    )
    stat('Distinct faces', mem['distinct_faces'], color=FG_YELLOW)
    stat('Has structure', yesno(value=mem['has_structure']))
    stat('Repeated patterns', mem['repeated_patterns'], color=FG_YELLOW)
    stat(
        'Unfamiliar moves',
        f'{mem["unfamiliar_move_percent"]:.0%}',
        color=gradient_color(1 - mem['unfamiliar_move_percent'], 0.4, 0.7),
    )


def print_impacts(impacts: dict[str, Any]) -> None:
    """Print the impact on the cube."""
    section('IMPACTS', FG_RED)
    stat(
        'Facelets mobilized',
        f'{impacts["facelets_mobilized_count"]} '
        f'({impacts["facelets_scrambled_percent"]:.0%})',
        color=FG_YELLOW,
    )
    stat('Facelets fixed', impacts['facelets_fixed_count'], color=FG_GREEN)

    face_mobility = impacts['facelets_face_mobility']
    mobility_str = ', '.join(
        f'{face_colorize(face)}:{colorize(str(count), FG_YELLOW)}'
        for face, count in face_mobility.items()
    )
    stat_raw('Face mobility', mobility_str)

    piece_impact = impacts['facelets_piece_type_impact']
    piece_str = ', '.join(
        f'{name}:{colorize(str(count), FG_YELLOW)}'
        for name, count in piece_impact.items()
    )
    stat_raw('Piece type impact', piece_str)

    stat(
        'Corners moved',
        f'{impacts["cubies_corners_moved"]} '
        f'(twisted: {impacts["cubies_corners_twisted"]})',
        color=FG_YELLOW,
    )
    stat(
        'Edges moved',
        f'{impacts["cubies_edges_moved"]} '
        f'(flipped: {impacts["cubies_edges_flipped"]})',
        color=FG_YELLOW,
    )
    stat(
        'Complexity score',
        impacts['cubies_complexity_score'],
        color=FG_MAGENTA,
    )
    signature = impacts['cubies_parity_signature']['signature']
    stat_raw(
        'Parity signature',
        f'{colorize(signature, FG_CYAN + BOLD)} '
        f'(valid: {yesno(value=impacts["cubies_parity_valid"])})',
    )
    stat(
        'Suggested approach',
        impacts['cubies_suggested_approach'],
        color=FG_CYAN,
    )

    qtm = impacts['facelets_qtm_distance']
    stat(
        'QTM distance',
        f'mean {qtm["mean"]:.2f}, max {qtm["max"]}, sum {qtm["sum"]}',
        color=FG_WHITE,
    )
    manhattan = impacts['facelets_manhattan_distance']
    stat(
        'Manhattan distance',
        f'mean {manhattan["mean"]:.2f}, '
        f'max {manhattan["max"]}, '
        f'sum {manhattan["sum"]}',
        color=FG_WHITE,
    )

    if impacts.get('cubies_patterns'):
        section('DETECTED PATTERNS', FG_MAGENTA)
        for pattern in impacts['cubies_patterns']:
            bullet = colorize('•', FG_MAGENTA)
            print(f'  {bullet} {colorize(pattern, FG_WHITE + BOLD)}')


def resume(algorithm: str, size: int, *, as_json: bool = False) -> None:
    """Print a text resume of an algorithm, or its raw data as JSON."""
    algo = parse_moves(algorithm)
    data = algo.to_dict(size)

    if as_json:
        print(json.dumps(data, indent=2))
        return

    print()
    print_overview(data, size)
    print_metrics(data['metrics'])
    print_ergonomics(data['ergonomics'])
    print_structure(data['structure'])
    print_memory(data['memory'])
    print_impacts(data['impacts'])
    print()


def main() -> None:
    """Parse CLI arguments and display the algorithm resume."""
    parser = argparse.ArgumentParser(
        description='Display a text resume of a cube algorithm.',
        epilog="""examples:
  %(prog)s "R U R' U'"
  %(prog)s "R U R' U R U2 R'" -s 3
  %(prog)s "Rw U Rw'" -s 4""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'algorithm',
        help='Algorithm to analyze (e.g. "R U R\'")',
    )
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=DEFAULT_CUBE_SIZE,
        help=f'Cube size (default: {DEFAULT_CUBE_SIZE})',
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output the raw resume data as JSON instead of text',
    )
    args = parser.parse_args()

    resume(args.algorithm, args.size, as_json=args.json)


if __name__ == '__main__':
    main()
