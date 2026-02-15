"""Demonstrate comprehensive algorithm memory difficulty analysis."""
# ruff: noqa: T201
from typing import ClassVar

from cubing_algs.algorithm import Algorithm


def show_memory(algorithm: str) -> None:
    """Display comprehensive memory difficulty analysis for an algorithm."""
    print(f'{"=" * 70}')
    print(f'Algorithm: {algorithm}')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    mem = algo.memory

    # Overview
    print('\nOVERVIEW')
    print('-' * 70)
    print(f'  Memory score:            {mem.memory_score:.1f}/100')
    print(f'  Memory rating:           {mem.memory_rating}')
    print(f'  Move count:              {mem.move_count}')

    # Sub-scores
    print('\nSUB-SCORES (0 = easy, 100 = hard)')
    print('-' * 70)
    print(f'  Length:                 {mem.length_score:.1f}')
    print(f'  Chunking:               {mem.chunk_score:.1f}')
    print(f'  Structure:              {mem.structure_score:.1f}')
    print(f'  Repetition:             {mem.repetition_score:.1f}')
    print(f'  Face diversity:         {mem.face_diversity_score:.1f}')
    print(f'  Flow:                   {mem.flow_score:.1f}')
    print(f'  Move familiarity:       {mem.move_familiarity_score:.1f}')

    # Raw data
    print('\nRAW DATA')
    print('-' * 70)
    print(f'  Effective chunks:        {mem.effective_chunks}')
    print(f'  Distinct triggers:       {mem.distinct_triggers}')
    print(f'  Trigger coverage:        {mem.trigger_coverage_percent:.0%}')
    print(f'  Distinct faces:          {mem.distinct_faces}')
    print(f'  Has structure:           {mem.has_structure}')
    print(f'  Repeated patterns:       {mem.repeated_patterns}')
    print(f'  Unfamiliar moves:        {mem.unfamiliar_move_percent:.0%}')

    print()


class _CompareHelper:
    """Helper for side-by-side comparison display."""

    ROWS: ClassVar[list[tuple[str, str, str]]] = [
        ('Moves', 'move_count', ''),
        ('Score', 'memory_score', '.1f'),
        ('Rating', 'memory_rating', ''),
        ('Length', 'length_score', '.1f'),
        ('Chunking', 'chunk_score', '.1f'),
        ('Structure', 'structure_score', '.1f'),
        ('Repetition', 'repetition_score', '.1f'),
        ('Face diversity', 'face_diversity_score', '.1f'),
        ('Flow', 'flow_score', '.1f'),
        ('Familiarity', 'move_familiarity_score', '.1f'),
        ('Chunks', 'effective_chunks', ''),
        ('Triggers', 'distinct_triggers', ''),
    ]


def compare_memory(algorithms: dict[str, str]) -> None:
    """Compare memory difficulty of multiple algorithms side by side."""
    print(f'{"=" * 70}')
    print('MEMORY DIFFICULTY COMPARISON')
    print('=' * 70)

    results = {}
    for name, alg_str in algorithms.items():
        algo = Algorithm.parse_moves(alg_str)
        results[name] = algo.memory

    # Header
    names = list(results.keys())
    col_width = max(14, max(len(n) for n in names) + 2)
    header = (
        f'  {"Metric":<26}'
        + ''.join(f'{n:>{col_width}}' for n in names)
    )
    print(header)
    print('  ' + '-' * (26 + col_width * len(names)))

    # Rows
    for label, attr, fmt in _CompareHelper.ROWS:
        line = f'  {label:<26}'
        for name in names:
            val = getattr(results[name], attr)
            if fmt:
                line += f'{val:>{col_width}{fmt}}'
            else:
                line += f'{val!s:>{col_width}}'
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
