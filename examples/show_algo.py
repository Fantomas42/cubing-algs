from cubing_algs.parsing import parse_moves


def show_algorithm(name, algorithm, **kw):
    algo = parse_moves(algorithm)

    print(f'{ name}: { algo }')

    algo.show(**kw)


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
