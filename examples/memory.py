"""Demonstrate comprehensive algorithm memorability analysis."""
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


def gradient_color(value: float, low: float, high: float) -> str:
    """
    Return a color based on where value falls between low and high thresholds.

    Returns:
        Green if good (easy), red if bad (hard), yellow if in between.

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


def show_memory(algorithm: str) -> None:
    """Display comprehensive memorability analysis for an algorithm."""
    print()
    header(f'Algorithm: {algorithm}', FG_MAGENTA)

    algo = Algorithm.parse_moves(algorithm)
    mem = algo.memory

    section('OVERVIEW', FG_CYAN)
    stat('Move count', mem.move_count, color=FG_WHITE)
    stat(
        'Memory score',
        f'{mem.memory_score:.2f}',
        color=gradient_color(mem.memory_score, 0.4, 0.7),
    )
    stat('Memory rating', mem.memory_rating, color=FG_CYAN)

    section('SUB-SCORES (0 = hard, 1 = easy)', FG_BLUE)
    stat(
        'Length',
        f'{mem.length_score:.2f}',
        color=gradient_color(mem.length_score, 0.4, 0.7),
    )
    stat(
        'Chunking',
        f'{mem.chunk_score:.2f}',
        color=gradient_color(mem.chunk_score, 0.4, 0.7),
    )
    stat(
        'Structure',
        f'{mem.structure_score:.2f}',
        color=gradient_color(mem.structure_score, 0.4, 0.7),
    )
    stat(
        'Repetition',
        f'{mem.repetition_score:.2f}',
        color=gradient_color(mem.repetition_score, 0.4, 0.7),
    )
    stat(
        'Face familiarity',
        f'{mem.face_familiarity_score:.2f}',
        color=gradient_color(mem.face_familiarity_score, 0.4, 0.7),
    )
    stat(
        'Flow',
        f'{mem.flow_score:.2f}',
        color=gradient_color(mem.flow_score, 0.4, 0.7),
    )
    stat(
        'Move familiarity',
        f'{mem.move_familiarity_score:.2f}',
        color=gradient_color(mem.move_familiarity_score, 0.4, 0.7),
    )

    section('RAW DATA', FG_GREEN)
    stat('Effective chunks', mem.effective_chunks, color=FG_YELLOW)
    stat('Distinct triggers', mem.distinct_triggers, color=FG_YELLOW)
    stat(
        'Trigger coverage',
        f'{mem.trigger_coverage_percent:.0%}',
        color=FG_CYAN,
    )
    stat('Distinct faces', mem.distinct_faces, color=FG_YELLOW)
    stat('Has structure', yesno(value=mem.has_structure))
    stat('Repeated patterns', mem.repeated_patterns, color=FG_YELLOW)
    stat(
        'Unfamiliar moves',
        f'{mem.unfamiliar_move_percent:.0%}',
        color=gradient_color(1 - mem.unfamiliar_move_percent, 0.4, 0.7),
    )

    print()


def compare_memory(algorithms: dict[str, str]) -> None:
    """Compare memorability of multiple algorithms side by side."""
    print()
    header('MEMORABILITY COMPARISON', FG_BLUE)

    results = {}
    for name, alg_str in algorithms.items():
        algo = Algorithm.parse_moves(alg_str)
        results[name] = algo.memory

    names = list(results.keys())
    col_width = max(14, max(len(n) for n in names) + 2)

    header_label = colorize(f'  {"Metric":<26}', FG_GREY + BOLD)
    header_names = ''.join(
        colorize(f'{n:>{col_width}}', FG_CYAN + BOLD) for n in names
    )
    print(f'{header_label}{header_names}')
    print(colorize('  ' + '-' * (26 + col_width * len(names)), FG_GREY))

    rows: list[tuple[str, str, str]] = [
        ('Moves', 'move_count', ''),
        ('Score', 'memory_score', '.2f'),
        ('Rating', 'memory_rating', ''),
        ('Length', 'length_score', '.2f'),
        ('Chunking', 'chunk_score', '.2f'),
        ('Structure', 'structure_score', '.2f'),
        ('Repetition', 'repetition_score', '.2f'),
        ('Face familiarity', 'face_familiarity_score', '.2f'),
        ('Flow', 'flow_score', '.2f'),
        ('Familiarity', 'move_familiarity_score', '.2f'),
        ('Chunks', 'effective_chunks', ''),
        ('Triggers', 'distinct_triggers', ''),
    ]
    for label, attr, fmt in rows:
        line = colorize(f'  {label:<26}', FG_GREY)
        for name in names:
            val = getattr(results[name], attr)
            formatted = f'{val:{fmt}}' if fmt else str(val)
            line += colorize(f'{formatted:>{col_width}}', FG_WHITE + BOLD)
        print(line)

    print()


# --- Individual Algorithm Analysis ---

# Simple trigger - trivial to memorize
show_memory("R U R' U'")

# Sune - well-known OLL algorithm
show_memory("R U R' U R U2 R'")

# T-Perm - longer PLL with triggers
show_memory("R U R' U' R' F R2 U' R' U' R U R' F'")

# Algorithm with back and slice moves - harder to memorize
show_memory("B' M' U' M B")

# Long algorithm with many faces
show_memory("R U R' U' R' F R2 U' R' U' R U R' F' R U R' U R U2 R'")


# --- Side-by-Side Comparisons ---

# OLL algorithms - varying difficulty
compare_memory({
    'Sexy': "R U R' U'",
    'Sune': "R U R' U R U2 R'",
    'OLL-33': "R U R' U' R' F R F'",
    'OLL-21': "F R U R' U' R U R' U' R U R' U' F'",
})

# PLL algorithms
compare_memory({
    'T-Perm': "R U R' U' R' F R2 U' R' U' R U R' F'",
    'Jb-Perm': "R U R' F' R U R' U' R' F R2 U' R'",
    'Y-Perm': "F R U' R' U' R U R' F' R U R' U' R' F R F'",
})

# Familiar vs unfamiliar faces
compare_memory({
    'RU only': "R U R' U R U2 R'",
    'RUF': "R U R' U' R' F R F'",
    'With B': "B' R' U' R U B",
    'With D': "R U R' U' D R2 U' R U' R' U R' U R2 D'",
})
