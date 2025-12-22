"""Demonstrate algorithm visualization with different display options."""
# ruff: noqa: T201
from cubing_algs.parsing import parse_moves


def show_algorithm(name: str, algorithm: str, **kw: object) -> None:
    """
    Display algorithm visualization with optional parameters.

    Args:
        name: Name of the algorithm.
        algorithm: Move sequence string.
        **kw: Additional keyword arguments passed to show method.

    """
    algo = parse_moves(algorithm)

    print(f'{ name}: { algo }')

    algo.show(**kw)  # type: ignore[arg-type]


show_algorithm(
    'Sexy Move',
    "R U R' U'",
)
show_algorithm(
    'Sexy Move y',
    "y R U R' U' y'",
)
show_algorithm(
    'Sexy Move z2',
    "z2 R U R' U' z2",
    orientation='DF',
)
show_algorithm(
    'PLL T-Perm',
    "z2 R U R' U' R' F R2 U' R' U' R U R' F' z2",
    mode='pll',
)
show_algorithm(
    'OLL 21 H',
    "z2 F R U R' U' R U R' U' R U R' U' F' z2",
    mode='oll',
)
