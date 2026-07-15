"""Display an algorithm with highlighted trigger patterns."""
import argparse
import re

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import MOVE_SPLIT
from cubing_algs.ergonomics import find_trigger_patterns
from cubing_algs.parsing import parse_moves
from cubing_algs.structure import Structure
from cubing_algs.structure import compute_structure
from cubing_algs.transform.pause import unpause_moves
from cubing_algs.transform.sign import unsign_moves
from cubing_algs.triggers import TriggerMatch

RESET = '\x1b[0m'
BOLD = '\x1b[1m'
DIM = '\x1b[2m'

FG_GREY = '\x1b[38;5;244m'
FG_WHITE = '\x1b[38;5;255m'

OP_COMMA = '\x1b[38;5;111m'   # light blue  — commutator separator
OP_COLON = '\x1b[38;5;210m'   # light salmon — conjugate separator

STRUCTURE_COLORS = {
    'commutator': '\x1b[38;5;203m',  # salmon red
    'conjugate': '\x1b[38;5;75m',    # steel blue
}

BRACKET_COLORS = [
    '\x1b[38;5;226m',  # depth 0 — bright yellow
    '\x1b[38;5;213m',  # depth 1 — light magenta
    '\x1b[38;5;123m',  # depth 2 — light cyan
    '\x1b[38;5;155m',  # depth 3 — light green
]

# One stable color per trigger category, so that adding a pattern to
# TRIGGER_PATTERNS never shifts the colors of the existing ones.
CATEGORY_COLORS = {
    'basic': '\x1b[38;5;118m',     # bright green
    'compound': '\x1b[38;5;39m',   # dodger blue
    'OLL': '\x1b[38;5;208m',       # orange
    'advanced': '\x1b[38;5;201m',  # hot pink
    'setup': '\x1b[38;5;226m',     # bright yellow
    'wide': '\x1b[38;5;51m',       # cyan
}
CATEGORY_FALLBACK = '\x1b[38;5;196m'  # bright red

# Move tokens as tokenized by the library, plus the punctuation used by
# the compressed structure notation.
STRUCTURE_TOKEN_RE = re.compile(r'[\[\],:]|' + MOVE_SPLIT.pattern)
PUNCTUATION = frozenset('[],:')


def normalize(algorithm_str: str) -> Algorithm:
    """
    Return the parsed algorithm in the notation used for trigger matching.

    Pauses are dropped and SiGN moves are converted to standard notation,
    so that move indices line up with those of find_trigger_patterns.

    Returns:
        Normalized algorithm.

    """
    return parse_moves(algorithm_str).transform(unpause_moves, unsign_moves)


def match_triggers(moves: list[str]) -> dict[int, TriggerMatch]:
    """
    Detect triggers in a sequence of normalized move strings.

    Returns:
        Mapping from start index to the trigger match starting there.

    """
    if not moves:
        return {}

    matches = find_trigger_patterns(parse_moves(' '.join(moves)))
    return {match.start_index: match for match in matches}


def match_token_runs(tokens: list[str]) -> dict[int, TriggerMatch]:
    """
    Detect triggers in each run of move tokens separated by punctuation.

    Triggers never span a bracket or a separator, so each run is matched
    on its own and its results are shifted back to token indices.

    Returns:
        Mapping from start token index to the trigger match starting there.

    """
    matches: dict[int, TriggerMatch] = {}
    run: list[str] = []
    run_start = 0

    for index, token in enumerate([*tokens, ',']):
        if token in PUNCTUATION:
            matches.update({
                run_start + start: match
                for start, match in match_triggers(run).items()
            })
            run = []
            run_start = index + 1
        else:
            run.append(token)

    return matches


def trigger_color(match: TriggerMatch) -> str:
    """
    Return the ANSI color of a matched trigger, keyed by its category.

    Returns:
        ANSI escape code string.

    """
    return CATEGORY_COLORS.get(match.pattern.category, CATEGORY_FALLBACK)


def render_moves(
    moves: list[str],
    matches: dict[int, TriggerMatch],
) -> str:
    """
    Build a colorized string of the algorithm with triggers highlighted.

    Returns:
        ANSI-colored move sequence string.

    """
    parts: list[str] = []
    i = 0
    while i < len(moves):
        match = matches.get(i)
        if match:
            segment = ' '.join(moves[i : i + match.length])
            parts.append(f'{trigger_color(match)}{BOLD}{segment}{RESET}')
            i += match.length
        else:
            parts.append(f'{FG_WHITE}{moves[i]}{RESET}')
            i += 1
    return ' '.join(parts)


def render_legend(matches: dict[int, TriggerMatch]) -> None:
    """Print a legend of detected triggers with their categories."""
    seen: dict[tuple[str, str], TriggerMatch] = {}
    for _, match in sorted(matches.items()):
        kind = match.variation.kind.value if match.variation else ''
        seen.setdefault((match.pattern.name, kind), match)

    if not seen:
        return

    print(f'\n{FG_GREY}Triggers:{RESET}')
    for (name, kind), match in seen.items():
        pattern = match.pattern
        label = f'{trigger_color(match)}{BOLD}{name}{RESET}'
        category = f'{FG_GREY}[{pattern.category}]{RESET}'
        moves_display = f'{DIM}{match.matched_moves}{RESET}'
        variation = f' {FG_GREY}({kind}){RESET}' if kind else ''
        print(f'  {label} {category}  {moves_display}{variation}')


def color_punctuation(punct: str, depth: int) -> tuple[str, int]:
    """
    Return (colored_string, new_depth) for a punctuation token.

    Returns:
        Tuple of colored string and updated nesting depth.

    """
    bracket_color = BRACKET_COLORS[depth % len(BRACKET_COLORS)]
    if punct == '[':
        return f'{bracket_color}{punct}{RESET}', depth + 1
    if punct == ']':
        new_depth = depth - 1
        color = BRACKET_COLORS[new_depth % len(BRACKET_COLORS)]
        return f'{color}{punct}{RESET}', new_depth
    if punct == ',':
        return f'{OP_COMMA}{punct}{RESET}', depth
    return f'{OP_COLON}{punct}{RESET}', depth  # ':'


def render_structure_notation(compressed: str) -> str:
    """
    Return the compressed structure notation with trigger sequences colorized.

    Brackets are colored by nesting depth; `,` is light blue (commutator)
    and `:` is light salmon (conjugate); move tokens are colored by the
    category of the trigger they belong to.

    Returns:
        ANSI-colored compressed notation string.

    """
    tokens = [
        token.group(0)
        for token in STRUCTURE_TOKEN_RE.finditer(compressed)
    ]
    matches = match_token_runs(tokens)

    # Build (raw_tokens, colored_str) segments
    segments: list[tuple[list[str], str]] = []
    depth = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in PUNCTUATION:
            colored, depth = color_punctuation(token, depth)
            segments.append(([token], colored))
            i += 1
            continue

        match = matches.get(i)
        if match:
            matched = tokens[i : i + match.length]
            segment = ' '.join(matched)
            segments.append(
                (matched, f'{trigger_color(match)}{BOLD}{segment}{RESET}'),
            )
            i += match.length
        else:
            segments.append(([token], f'{FG_WHITE}{token}{RESET}'))
            i += 1

    # Reconstruct spacing: no space after `[`, no space before `]`/`,`/`:`
    result: list[str] = []
    for idx, (raw, colored) in enumerate(segments):
        if idx == 0:
            result.append(colored)
            continue
        prev_last = segments[idx - 1][0][-1]
        curr_first = raw[0]
        if prev_last == '[' or curr_first in {']', ',', ':'}:
            result.append(colored)
        else:
            result.append(' ' + colored)

    return ''.join(result)


def render_structure_line(structures: list[Structure]) -> str:
    """
    Return a one-line summary of the detected top-level structures.

    Returns:
        Human-readable classification string.

    """
    if not structures:
        return f'{FG_GREY}none{RESET}'
    parts: list[str] = []
    for structure in structures:
        classification = structure.classification or structure.type
        color = STRUCTURE_COLORS.get(structure.type, FG_WHITE)
        parts.append(f'{color}{BOLD}{classification}{RESET}')
    return f'{FG_GREY},{RESET} '.join(parts)


def show_highlighted(algorithm_str: str) -> None:
    """Parse and display an algorithm with trigger patterns highlighted."""
    algo = normalize(algorithm_str)
    moves = [str(move) for move in algo]

    matches = match_triggers(moves)
    covered = sum(match.length for match in matches.values())

    structure_data = compute_structure(algo)
    rendered = render_moves(moves, matches)
    rendered_structure = render_structure_notation(structure_data.compressed)
    structure_summary = render_structure_line(structure_data.structures)

    print(f'{FG_GREY}Algorithm:{RESET} {FG_WHITE}{BOLD}{algorithm_str}{RESET}')
    print(f'{FG_GREY}Moves:    {RESET} {len(moves)}')
    print(f'{FG_GREY}Triggers: {RESET} {len(matches)}')
    print(f'{FG_GREY}Coverage: {RESET} {covered}/{len(moves)} moves')
    print(f'{FG_GREY}Structure:{RESET} {structure_summary}')
    print()
    print(f'  {rendered}')
    print(f'  {rendered_structure}')

    render_legend(matches)
    print()


def main() -> None:
    """Parse arguments and display algorithms with trigger highlighting."""
    parser = argparse.ArgumentParser(
        description=(
            'Display algorithms with highlighted '
            'trigger patterns and structure.'
        ),
        epilog=(
            'Examples:\n'
            "  python highlight_alg.py \"R U R' U'\"\n"
            "  python highlight_alg.py \"R U R' U' R' F R F'\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'algorithms',
        nargs='*',
        metavar='ALG',
        help='Algorithm(s) to display. Uses built-in examples if none given.',
    )
    args = parser.parse_args()

    algorithms = args.algorithms or [
        # Simple
        "R U R'",
        "R U R' U'",
        "R U2 R'",
        "F R U R' U' F'",
        # Medium
        "R' U' R U' R' U2 R",
        "R U R' U R U2 R'",
        "R U R' U' R' F R F'",
        # Long — PLL and OLL
        "R U R' U' R' F R2 U' R' U' R U R' F'",
        "R U R' F' R U R' U' R' F R2 U' R'",
        "R2 U R U R' U' R' U' R' U R'",
        "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        "R' U2 R U2 R' F R U R' U' R' F' R2",
        "F R U R' U' R U R' U' R U R' U' F'",
        'M2 U M2 U2 M2 U M2',
    ]

    for alg in algorithms:
        show_highlighted(alg)


if __name__ == '__main__':
    main()
