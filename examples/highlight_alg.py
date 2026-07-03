"""Display an algorithm with highlighted trigger patterns."""
# ruff: noqa: T201
import argparse
import re

from cubing_algs.algorithm import Algorithm
from cubing_algs.structure import Structure
from cubing_algs.structure import compute_structure
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerPattern

RESET = '\x1b[0m'
BOLD = '\x1b[1m'
DIM = '\x1b[2m'

FG_GREY = '\x1b[38;5;244m'
FG_WHITE = '\x1b[38;5;255m'

OP_COMMA = '\x1b[38;5;111m'   # light blue  — commutator separator
OP_COLON = '\x1b[38;5;210m'   # light salmon — conjugate separator
BRACKET_COLORS = [
    '\x1b[38;5;226m',  # depth 0 — bright yellow
    '\x1b[38;5;213m',  # depth 1 — light magenta
    '\x1b[38;5;123m',  # depth 2 — light cyan
    '\x1b[38;5;155m',  # depth 3 — light green
]

_TRIGGER_PALETTE = [
    '\x1b[38;5;196m',  # bright red
    '\x1b[38;5;208m',  # orange
    '\x1b[38;5;226m',  # bright yellow
    '\x1b[38;5;118m',  # bright green
    '\x1b[38;5;51m',   # cyan
    '\x1b[38;5;39m',   # dodger blue
    '\x1b[38;5;129m',  # violet
    '\x1b[38;5;201m',  # hot pink
    '\x1b[38;5;214m',  # amber
    '\x1b[38;5;154m',  # yellow-green
    '\x1b[38;5;45m',   # sky blue
    '\x1b[38;5;165m',  # orchid
    '\x1b[38;5;82m',   # chartreuse
    '\x1b[38;5;207m',  # pink
    '\x1b[38;5;93m',   # blue-violet
    '\x1b[38;5;48m',   # spring green
]
TRIGGER_COLORS: dict[str, str] = {
    p.name: _TRIGGER_PALETTE[i % len(_TRIGGER_PALETTE)]
    for i, p in enumerate(TRIGGER_PATTERNS)
}


def parse_move_strings(moves_str: str) -> list[str]:
    """
    Return individual move strings parsed from a move sequence.

    Returns:
        List of move strings.

    """
    return [str(m) for m in Algorithm.parse_moves(moves_str)]


def build_pattern_variants() -> list[tuple[TriggerPattern, list[str]]]:
    """
    Return all (pattern, move-list) pairs including variations, longest first.

    Returns:
        Sorted list of (pattern, moves) pairs.

    """
    entries: list[tuple[TriggerPattern, list[str]]] = []
    for pattern in TRIGGER_PATTERNS:
        entries.append((pattern, parse_move_strings(pattern.moves)))
        entries.extend(
            (pattern, parse_move_strings(variation.moves))
            for variation in pattern.variations
        )
    entries.sort(key=lambda x: len(x[1]), reverse=True)
    return entries


def find_matches(
    moves: list[str],
    pattern_variants: list[tuple[TriggerPattern, list[str]]],
) -> dict[int, tuple[int, TriggerPattern]]:
    """
    Find non-overlapping trigger matches using greedy longest-first matching.

    Returns:
        Mapping from start index to (exclusive end index, pattern).

    """
    n = len(moves)
    matched: dict[int, tuple[int, TriggerPattern]] = {}
    i = 0
    while i < n:
        for pattern, pmoves in pattern_variants:
            plen = len(pmoves)
            if i + plen <= n and moves[i : i + plen] == pmoves:
                matched[i] = (i + plen, pattern)
                i += plen
                break
        else:
            i += 1
    return matched


def trigger_color(pattern: TriggerPattern) -> str:
    """
    Return the ANSI color for a trigger pattern.

    Returns:
        ANSI escape code string.

    """
    return TRIGGER_COLORS.get(pattern.name, _TRIGGER_PALETTE[0])


def render_algorithm(
    moves: list[str],
    matches: dict[int, tuple[int, TriggerPattern]],
) -> str:
    """
    Build a colorized string of the algorithm with triggers highlighted.

    Returns:
        ANSI-colored move sequence string.

    """
    parts: list[str] = []
    i = 0
    while i < len(moves):
        if i in matches:
            end, pattern = matches[i]
            color = trigger_color(pattern)
            segment = ' '.join(moves[i:end])
            parts.append(f'{color}{BOLD}{segment}{RESET}')
            i = end
        else:
            parts.append(f'{FG_WHITE}{moves[i]}{RESET}')
            i += 1
    return ' '.join(parts)


def render_legend(
    matches: dict[int, tuple[int, TriggerPattern]],
) -> None:
    """Print a legend of detected triggers with their categories."""
    seen: dict[str, TriggerPattern] = {}
    for _, (_, pattern) in sorted(matches.items()):
        if pattern.name not in seen:
            seen[pattern.name] = pattern

    if not seen:
        return

    print(f'\n{FG_GREY}Triggers:{RESET}')
    for name, pattern in seen.items():
        color = trigger_color(pattern)
        label = f'{color}{BOLD}{name}{RESET}'
        category = f'{FG_GREY}[{pattern.category}]{RESET}'
        moves_display = f'{DIM}{pattern.moves}{RESET}'
        print(f'  {label} {category}  {moves_display}')


# Matches individual punctuation characters or move tokens (e.g. R, U2, Rw')
_STRUCTURE_TOKEN_RE = re.compile(r"[\[\],:]|[A-Za-z][A-Za-z0-9]*'*")
_PUNCT = frozenset('[],:')


def _color_punct(tok: str, depth: int) -> tuple[str, int]:
    """
    Return (colored_string, new_depth) for a punctuation token.

    Returns:
        Tuple of colored string and updated nesting depth.

    """
    bracket_color = BRACKET_COLORS[depth % len(BRACKET_COLORS)]
    if tok == '[':
        return f'{bracket_color}{tok}{RESET}', depth + 1
    if tok == ']':
        new_depth = depth - 1
        color = BRACKET_COLORS[new_depth % len(BRACKET_COLORS)]
        return f'{color}{tok}{RESET}', new_depth
    if tok == ',':
        return f'{OP_COMMA}{tok}{RESET}', depth
    return f'{OP_COLON}{tok}{RESET}', depth  # ':'


def render_structure_notation(
    compressed: str,
    pattern_variants: list[tuple[TriggerPattern, list[str]]],
) -> str:
    """
    Return the compressed structure notation with trigger sequences colorized.

    Brackets are colored by nesting depth; `,` is light blue (commutator)
    and `:` is light salmon (conjugate); move tokens are checked against
    trigger patterns and colored when they match.

    Returns:
        ANSI-colored compressed notation string.

    """
    toks = _STRUCTURE_TOKEN_RE.findall(compressed)

    # Build (raw_tokens, colored_str) segments
    segments: list[tuple[list[str], str]] = []
    depth = 0
    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok in _PUNCT:
            colored, depth = _color_punct(tok, depth)
            segments.append(([tok], colored))
            i += 1
            continue

        matched = False
        for pattern, pmoves in pattern_variants:
            plen = len(pmoves)
            if toks[i:i + plen] == pmoves:
                color = trigger_color(pattern)
                segment = ' '.join(pmoves)
                segments.append((pmoves, f'{color}{BOLD}{segment}{RESET}'))
                i += plen
                matched = True
                break

        if not matched:
            segments.append(([tok], f'{FG_WHITE}{tok}{RESET}'))
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


def render_structure_line(
    structures: list[Structure],
) -> str:
    """
    Return a one-line summary of the detected top-level structures.

    Returns:
        Human-readable classification string.

    """
    if not structures:
        return f'{FG_GREY}none{RESET}'
    parts: list[str] = []
    for s in structures:
        cls = s.classification or s.type
        color = '\x1b[38;5;203m' if s.type == 'commutator' else '\x1b[38;5;75m'
        parts.append(f'{color}{BOLD}{cls}{RESET}')
    return f'{FG_GREY},{RESET} '.join(parts)


def show_highlighted(algorithm_str: str) -> None:
    """Parse and display an algorithm with trigger patterns highlighted."""
    algo = Algorithm.parse_moves(algorithm_str)
    moves = [str(m) for m in algo]

    pattern_variants = build_pattern_variants()
    matches = find_matches(moves, pattern_variants)

    rendered = render_algorithm(moves, matches)
    trigger_count = len(matches)
    covered = sum(end - start for start, (end, _) in matches.items())

    structure_data = compute_structure(algo)
    rendered_structure = render_structure_notation(
        structure_data.compressed, pattern_variants,
    )
    structure_summary = render_structure_line(structure_data.structures)

    print(f'{FG_GREY}Algorithm:{RESET} {FG_WHITE}{BOLD}{algorithm_str}{RESET}')
    print(f'{FG_GREY}Moves:    {RESET} {len(moves)}')
    print(f'{FG_GREY}Triggers: {RESET} {trigger_count}')
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
            "  python highlight_alg.py \"R U R' U' R' F R2 ...\""
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
