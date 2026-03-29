"""Demonstrate comprehensive algorithm ergonomics analysis."""
# ruff: noqa: T201
from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import HandDominance
from cubing_algs.ergonomics import compute_ergonomics


def show_ergonomics(algorithm: str) -> None:
    """Display comprehensive ergonomics analysis for an algorithm."""
    print(f'{"=" * 70}')
    print(f'Algorithm: {algorithm}')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    ergo = algo.ergonomics

    # Overview
    print('\nOVERVIEW')
    print('-' * 70)
    print(f'  Total moves:             {ergo.total_moves}')
    print(f'  Comfort score:           {ergo.comfort_score:.1f}/100')
    print(f'  Ergonomic rating:        {ergo.ergonomic_rating}')
    print(f'  Difficulty:              {ergo.difficulty_classification}')
    print(f'  Ergonomic score:         {ergo.ergonomic_score:.2f}')

    # Execution Metrics
    print('\nEXECUTION METRICS')
    print('-' * 70)
    print(f'  Estimated time:          {ergo.estimated_execution_time:.2f}s')
    print(f'  Estimated TPS:           {ergo.estimated_tps:.1f}')
    print(f'  Flow score:              {ergo.flow_score:.2f}')
    print(f'  Fingertrick difficulty:  {ergo.fingertrick_difficulty:.2f}')

    # Hand Balance
    print('\nHAND BALANCE')
    print('-' * 70)
    print(f'  Right hand moves:        {ergo.right_hand_moves}')
    print(f'  Left hand moves:         {ergo.left_hand_moves}')
    print(f'  Both hands moves:        {ergo.both_hand_moves}')
    print(
        f'  Balance ratio:           '
        f'{ergo.hand_balance_ratio:.2f} (0.5 = perfect)',
    )

    # Finger Distribution
    print('\nFINGER DISTRIBUTION')
    print('-' * 70)
    print(f'  Thumb moves:             {ergo.thumb_moves}')
    print(f'  Index finger moves:      {ergo.index_finger_moves}')
    print(f'  Middle finger moves:     {ergo.middle_finger_moves}')
    print(f'  Ring finger moves:       {ergo.ring_finger_moves}')

    # Difficulty Factors
    print('\nDIFFICULTY FACTORS')
    print('-' * 70)
    print(f'  Regrips required:        {ergo.regrip_count}')
    print(f'  Awkward moves:           {ergo.awkward_moves}')
    print(f'  Flow breaks:             {ergo.flow_breaks}')

    # Trigger Patterns
    print('\nTRIGGER PATTERNS')
    print('-' * 70)
    print(f'  Triggers detected:       {ergo.trigger_count}')
    print(f'  Trigger coverage:        {ergo.trigger_coverage} moves')
    if ergo.detected_patterns:
        for pattern in ergo.detected_patterns:
            print(f'    - {pattern}')

    # Suggestions
    if ergo.suggestions:
        print('\nSUGGESTIONS')
        print('-' * 70)
        for suggestion in ergo.suggestions:
            print(f'  - {suggestion}')

    print()


def compare_algorithms(algorithms: dict[str, str]) -> None:
    """Compare ergonomics of multiple algorithms side by side."""
    print(f'{"=" * 70}')
    print('ALGORITHM COMPARISON')
    print('=' * 70)

    results = {}
    for name, alg_str in algorithms.items():
        algo = Algorithm.parse_moves(alg_str)
        results[name] = algo.ergonomics

    # Header
    names = list(results.keys())
    col_width = max(14, max(len(n) for n in names) + 2)
    header = f'  {"Metric":<26}' + ''.join(f'{n:>{col_width}}' for n in names)
    print(header)
    print('  ' + '-' * (26 + col_width * len(names)))

    # Rows
    rows = [
        ('Moves', 'total_moves', ''),
        ('Comfort', 'comfort_score', '.1f'),
        ('Rating', 'ergonomic_rating', ''),
        ('Difficulty', 'difficulty_classification', ''),
        ('TPS', 'estimated_tps', '.1f'),
        ('Flow', 'flow_score', '.2f'),
        ('Regrips', 'regrip_count', ''),
        ('Triggers', 'trigger_count', ''),
        ('Time (s)', 'estimated_execution_time', '.2f'),
    ]

    for label, attr, fmt in rows:
        line = f'  {label:<26}'
        for name in names:
            val = getattr(results[name], attr)
            if fmt:
                line += f'{val:>{col_width}{fmt}}'
            else:
                line += f'{val!s:>{col_width}}'
        print(line)

    print()


def show_hand_dominance_comparison(algorithm: str) -> None:
    """Show how hand dominance affects ergonomic scores."""
    print(f'{"=" * 70}')
    print(f'HAND DOMINANCE ANALYSIS: {algorithm}')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)

    for dominance in HandDominance:
        ergo = compute_ergonomics(algo, dominance)
        print(f'\n  {dominance.value.upper()} HANDED')
        print(f'    Ergonomic score:       {ergo.ergonomic_score:.2f}')
        print(f'    Comfort score:         {ergo.comfort_score:.1f}/100')
        print(f'    Estimated TPS:         {ergo.estimated_tps:.1f}')
        print(f'    Difficulty:            {ergo.difficulty_classification}')

    print()


# --- Individual Algorithm Analysis ---

# Simple trigger - very ergonomic
show_ergonomics("R U R' U'")

# Sune - common OLL algorithm
show_ergonomics("R U R' U R U2 R'")

# T-Perm - complex PLL algorithm
show_ergonomics("R U R' U' R' F R2 U' R' U' R U R' F'")

# Algorithm with back and slice moves - less ergonomic
show_ergonomics("B' M' U' M B")

# Long algorithm with rotations
show_ergonomics("y R U R' U' R U R' U' R U R' y'")


# --- Side-by-Side Comparison ---

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


# --- Hand Dominance ---

show_hand_dominance_comparison("R U R' U' R' F R F'")
show_hand_dominance_comparison("L U L' U' L' F L F'")
